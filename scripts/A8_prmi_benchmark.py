#!/usr/bin/env python3
"""
Title:
    M1/M2/M3 benchmark on PRMI test
File type:
    Script
Purpose:
    Applies M1, the development U-Net (M2) and M3 to the PRMI test split and measures pixel,
    centreline and skeleton metrics against ground truth.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-14
Date:
    2026-07-14
Developer:
    Prof. Wesley Pacheco Calixto
Authors:
    Wesley Pacheco Calixto; Universidade de Coimbra (UC), Portugal; Universidade Federal de Goiás
    (UFG), Brazil; Instituto Federal de Educação, Ciência e Tecnologia de Goiás (IFG), Brazil
Corresponding author:
    Wesley Pacheco Calixto
License:
    MIT (see LICENSE)
Citation:
    If you use this code, please cite the Radicular Software record on Zenodo (DOI 10.5281/zenodo.23679263) and the related publication.
Related publication:
    Auditable longitudinal root phenotyping in rhizotrons using Frangi--U-Net fusion and apparent
    conductivity (manuscript in preparation for submission to Royal Society Open Science)
Inputs:
    - modelos/external_development_model.pt
Outputs:
    - A8_prmi_por_imagem.csv
    - A8_prmi_shard_I.csv
Dependencies:
    - cv2
    - numpy
    - scipy
    - segmentation_models_pytorch
    - skimage
    - torch
    - local: config
Execution:
    python scripts/A8_prmi_benchmark.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Not re-executed in the v1.0.0 verification. Environment of the verification: Python 3.9.6
    (macOS) with the versions listed in requirements.txt.
Warnings:
    Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not
    redistributed in these packages.
"""
# Original module notes (Portuguese) are preserved below.
"""
Resultado adicional A8 — benchmark M1/M2/M3 no teste PRMI COMPLETO (sanidade cross-domain).
Aplica M1 (Frangi, parâmetros de RIZOTRON), M2 (modelo de DESENVOLVIMENTO PRMI, sem o teste)
e M3 = R(M1) ∪ M2 a TODAS as imagens do split `test` do PRMI, medindo contra a GT: Dice, IoU,
precisão, sensibilidade, especificidade, clDice (centerline Dice) e métricas de esqueleto com
tolerância. Grava por imagem, com ID PARENTAL (espécie_T###_L###) para bootstrap clusterizado.
RESSALVA: M1/M3 sintonizados para rizotron; Dice baixo no PRMI é DOMAIN SHIFT. Enquadrar como
compromisso precisão–sensibilidade, NÃO como escolha de método no domínio local.
Uso: A8_prmi_benchmark.py <PRMI_ROOT> [N_POR_ESPECIE|all] [--shard I K]
Saída: A8_prmi_shard_I.csv (ou A8_prmi_por_imagem.csv se sem shard).
"""
import os, sys, csv, glob, re, importlib.util
import numpy as np, cv2, torch
from skimage.morphology import skeletonize
from scipy.ndimage import distance_transform_edt
import segmentation_models_pytorch as smp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

ENCODER, LONG, THR, FECHA = "resnet34", 1024, 0.5, 3
IMEAN = np.array([0.485, 0.456, 0.406], np.float32)
ISTD = np.array([0.229, 0.224, 0.225], np.float32)
TOL = 3
PARENT_RE = re.compile(r"(T\d+_L\d+)")


def load_mod(name, path):
    """
    Purpose:
        Import a pipeline script as a module from its file path without executing its main function.
    Parameters:
        name: module name
        path: script path
    Returns:
        module
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def unet_mask(model, dev, bgr):
    """
    Purpose:
        Predict a binary root mask with the U-Net for one BGR image, resizing to the model input and back.
    Parameters:
        model: loaded U-Net
        dev: torch device
        bgr: image array (BGR)
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    H0, W0 = rgb.shape[:2]; s = LONG / max(H0, W0)
    Hn = max(32, int(round(H0 * s / 32)) * 32); Wn = max(32, int(round(W0 * s / 32)) * 32)
    img = cv2.resize(rgb, (Wn, Hn)).astype(np.float32) / 255.0
    x = torch.from_numpy(((img - IMEAN) / ISTD).transpose(2, 0, 1)).unsqueeze(0).to(dev)
    with torch.inference_mode():
        prob = torch.sigmoid(model(x))[0, 0].float().cpu().numpy()
    return cv2.resize(prob, (W0, H0)) >= THR


def pix_metrics(pred, gt):
    """
    Purpose:
        Pixel metrics from TP/FP/TN/FN.
    Parameters:
        pred: prediction
        gt: ground truth
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    tp = int(np.logical_and(pred, gt).sum()); fp = int(np.logical_and(pred, ~gt).sum())
    fn = int(np.logical_and(~pred, gt).sum()); tn = int(np.logical_and(~pred, ~gt).sum())
    dice = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 1.0
    iou = tp / (tp + fp + fn) if (tp + fp + fn) else 1.0
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    spec = tn / (tn + fp) if (tn + fp) else 1.0
    return dice, iou, prec, rec, spec


def cldice(pred, gt):
    """clDice = média harmônica de precisão de topologia (skel_pred dentro de gt) e
    sensibilidade de topologia (skel_gt dentro de pred)."""
    if pred.sum() == 0 or gt.sum() == 0:
        return 0.0 if (pred.sum() or gt.sum()) else 1.0
    sp = skeletonize(pred); sg = skeletonize(gt)
    if sp.sum() == 0 or sg.sum() == 0:
        return 0.0
    tprec = float((sp & gt).sum()) / float(sp.sum())
    tsens = float((sg & pred).sum()) / float(sg.sum())
    return 2 * tprec * tsens / (tprec + tsens) if (tprec + tsens) else 0.0


def skel_tol(pred, gt):
    """
    Purpose:
        Skeleton precision and sensitivity with tolerance.
    Parameters:
        pred: prediction
        gt: ground truth
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    sp = skeletonize(pred); sg = skeletonize(gt)
    if sp.sum() == 0 or sg.sum() == 0:
        return (np.nan, np.nan)
    dg = distance_transform_edt(~sg); dp = distance_transform_edt(~sp)
    return float((dg[sp] <= TOL).mean()), float((dp[sg] <= TOL).mean())


def main():
    """
    Purpose:
        Run the script end to end: read inputs, compute results and write the outputs listed in the header.
    Parameters:
        none (some scripts accept an optional limit or command-line argument)
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    root = sys.argv[1] if len(sys.argv) > 1 else "/root/prmi/PRMI_official"
    n_arg = sys.argv[2] if len(sys.argv) > 2 else "all"
    n_per = None if n_arg == "all" else int(n_arg)
    shard_i, shard_k, out = 0, 1, "A8_prmi_por_imagem.csv"
    if "--shard" in sys.argv:
        j = sys.argv.index("--shard"); shard_i, shard_k = int(sys.argv[j + 1]), int(sys.argv[j + 2])
        out = f"A8_prmi_shard_{shard_i}.csv"
    fr = load_mod("fr", str(C.SCRIPTS / "07_frangi.py"))
    ref = load_mod("ref", str(C.SCRIPTS / "08E_refinamento.py"))
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = smp.Unet(encoder_name=ENCODER, encoder_weights=None, in_channels=3, classes=1).to(dev)
    model.load_state_dict(torch.load(str(C.MODELOS / "external_development_model.pt"), map_location=dev)); model.eval()

    img_root = os.path.join(root, "test", "images")
    msk_root = os.path.join(root, "test", "masks_pixel_gt")
    especies = sorted(d for d in os.listdir(img_root) if os.path.isdir(os.path.join(img_root, d)))
    sel = []
    for sp in especies:
        fns = sorted(glob.glob(os.path.join(img_root, sp, "*.jpg")) + glob.glob(os.path.join(img_root, sp, "*.png")))
        if n_per is not None:
            idx = np.linspace(0, len(fns) - 1, min(n_per, len(fns))).round().astype(int)
            fns = [fns[i] for i in dict.fromkeys(idx)]
        for p in fns:
            stem = os.path.splitext(os.path.basename(p))[0]
            gt = os.path.join(msk_root, sp, f"GT_{stem}.png")
            if os.path.exists(gt):
                mm = PARENT_RE.search(stem); parent = f"{sp}_{mm.group(1)}" if mm else sp
                sel.append((sp, parent, p, gt))
    sel = [s for n, s in enumerate(sel) if n % shard_k == shard_i]
    print(f"[A8] shard {shard_i}/{shard_k} | {len(sel)} imagens | dev={dev}", flush=True)

    def m3_from(m1, m2):
        comb = ref.denoise_frangi(m1) | m2
        return cv2.morphologyEx(comb.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((FECHA, FECHA), np.uint8)).astype(bool)

    rows = []
    for k, (sp, parent, p, gtp) in enumerate(sel, 1):
        gt = cv2.imread(gtp, 0) > 127
        _, m1, _, _, _ = fr.segmentar(p)
        m2 = unet_mask(model, dev, cv2.imread(p))
        if m1.shape != gt.shape: m1 = cv2.resize(m1.astype(np.uint8), (gt.shape[1], gt.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
        if m2.shape != gt.shape: m2 = cv2.resize(m2.astype(np.uint8), (gt.shape[1], gt.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
        m3 = m3_from(m1, m2)
        r = {"especie": sp, "parent": parent, "img": os.path.basename(p)}
        for tag, m in [("M1", m1), ("M2", m2), ("M3", m3)]:
            dice, iou, prec, rec, spec = pix_metrics(m, gt)
            cld = cldice(m, gt); sprec, srec = skel_tol(m, gt)
            r.update({f"dice_{tag}": round(dice, 4), f"iou_{tag}": round(iou, 4),
                      f"prec_{tag}": round(prec, 4), f"rec_{tag}": round(rec, 4), f"spec_{tag}": round(spec, 4),
                      f"cldice_{tag}": round(cld, 4),
                      f"skprec_{tag}": round(sprec, 4) if not np.isnan(sprec) else "",
                      f"skrec_{tag}": round(srec, 4) if not np.isnan(srec) else ""})
        rows.append(r)
        if k % 200 == 0 or k == len(sel):
            print(f"  [{shard_i}: {k}/{len(sel)}]", flush=True)

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"[A8] shard {shard_i} -> {out} ({len(rows)} linhas)", flush=True)


if __name__ == "__main__":
    main()
