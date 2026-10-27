#!/usr/bin/env python3
"""
Title:
    Reflection-treatment ablation
File type:
    Script
Purpose:
    Runs M1, M2 and M3 on original and reconstructed images and compares masks only in genuinely
    unchanged areas, reporting Jaccard, Dice, descriptor changes and spatial enrichment E_d.
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
    - modelos/external_final_model_PRMI_all.pt
    - saidas/05A_tratadas
    - saidas/05_registradas
Outputs:
    - metricas/A9_ablacao.csv
Dependencies:
    - cv2
    - numpy
    - scipy
    - segmentation_models_pytorch
    - skimage
    - torch
    - local: config
Execution:
    python scripts/A9_ablacao.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Not re-executed in the v1.0.0 verification. Environment of the verification: Python 3.9.6
    (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Resultado adicional A9 — ablação do tratamento do reflexo (estabilidade espacial).
Roda M1 (Frangi), M2 (U-Net final) e M3 = R(M1) ∪ M2 na imagem ORIGINAL (com reflexo,
05_registradas) e na RECONSTRUÍDA por LaMa (05A_tratadas), e compara SOMENTE na área
GENUINAMENTE INALTERADA V = 1 − dilata(M_inpaint, ~40px) — excluindo o SUPORTE EFETIVO da
mistura gaussiana (σ=12 ⇒ ~3σ=36px), não apenas a máscara binária. NÃO afirma acurácia.
Métricas por imagem (em V): Jaccard/Dice(M3_orig, M3_recon) e idem M1, M2; deltas assinados,
ABSOLUTOS e RELATIVOS dos descritores (ocupação em pp, L_skel e N_br relativos); e enriquecimento
espacial E_d das alterações em bandas de distância ao reflexo, normalizado pela geometria de V,
por método (M1/M2/M3) — para NÃO atribuir a propagação a um único ramo.
Saída: metricas/A9_ablacao.csv (por imagem) + resumo (mediana [IIQ]).
"""
import os, sys, csv, importlib.util
import statistics as st
import numpy as np, cv2, torch
from scipy.ndimage import distance_transform_edt
from skimage.morphology import skeletonize
import segmentation_models_pytorch as smp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

REG = C.SAIDAS / "05_registradas"
TRAT = C.SAIDAS / "05A_tratadas"
MASC = TRAT / "_mascaras"
ENCODER, LONG, THR, FECHA = "resnet34", 1024, 0.5, 3
IMEAN = np.array([0.485, 0.456, 0.406], np.float32)
ISTD = np.array([0.229, 0.224, 0.225], np.float32)
BLEND_EXCL = 40          # exclui o suporte efetivo da mistura (σ=12, 3σ≈36) + margem
BANDS = [60, 120, 240]   # bandas de distância (px) p/ enriquecimento espacial


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


def jac_dice(a, b):
    """
    Purpose:
        Jaccard and Dice between two masks.
    Parameters:
        a, b: boolean masks
    Returns:
        tuple
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    inter = np.logical_and(a, b).sum(); uni = np.logical_or(a, b).sum(); sa = a.sum() + b.sum()
    return (inter / uni if uni else 1.0), (2 * inter / sa if sa else 1.0)


def Lskel(m):
    """
    Purpose:
        Skeleton length of a mask.
    Parameters:
        m: mask
    Returns:
        tuple (length, skeleton)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    S = skeletonize(m)
    nh = np.logical_and(S[:, :-1], S[:, 1:]).sum(); nv = np.logical_and(S[:-1, :], S[1:, :]).sum()
    nd = np.logical_and(S[:-1, :-1], S[1:, 1:]).sum() + np.logical_and(S[:-1, 1:], S[1:, :-1]).sum()
    return nh + nv + nd * 2 ** 0.5, S


def nbr(S):
    """
    Purpose:
        Count branch nodes of a skeleton.
    Parameters:
        S: skeleton
    Returns:
        int
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    from scipy.ndimage import convolve, label
    deg = convolve(S.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - S
    return int(label(np.logical_and(S, deg >= 3), structure=np.ones((3, 3)))[1])


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
    fr = load_mod("fr", str(C.SCRIPTS / "07_frangi.py"))
    ref = load_mod("ref", str(C.SCRIPTS / "08E_refinamento.py"))
    dev = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    model = smp.Unet(encoder_name=ENCODER, encoder_weights=None, in_channels=3, classes=1).to(dev)
    model.load_state_dict(torch.load(str(C.MODELOS / "external_final_model_PRMI_all.pt"), map_location=dev)); model.eval()

    def masks_from(path_img):
        _, m1, _, _, _ = fr.segmentar(str(path_img))
        m2 = unet_mask(model, dev, cv2.imread(str(path_img)))
        if m2.shape != m1.shape:
            m2 = cv2.resize(m2.astype(np.uint8), (m1.shape[1], m1.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
        comb = ref.denoise_frangi(m1) | m2
        comb = cv2.morphologyEx(comb.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((FECHA, FECHA), np.uint8)).astype(bool)
        return {"M1": m1, "M2": m2, "M3": comb}

    rows = []
    masks = sorted(MASC.rglob("*.png"))
    for k, mp in enumerate(masks, 1):
        rel = mp.relative_to(MASC); orig = REG / rel; recon = TRAT / rel
        if not orig.exists() or not recon.exists():
            continue
        inpaint = cv2.imread(str(mp), 0) > 127
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * BLEND_EXCL + 1, 2 * BLEND_EXCL + 1))
        inpaint_eff = cv2.dilate(inpaint.astype(np.uint8), ker) > 0     # suporte efetivo da mistura
        V = ~inpaint_eff
        dist = distance_transform_edt(~inpaint)                          # distância ao reflexo (binário)
        mo = masks_from(orig); mr = masks_from(recon)
        r = {"image_id": mp.stem, "data": rel.parts[0], "inpaint_pct": round(100 * inpaint.mean(), 3),
             "V_pct": round(100 * V.mean(), 2)}
        for tag in ("M1", "M2", "M3"):
            a, b = mo[tag] & V, mr[tag] & V
            j, d = jac_dice(a, b)
            r[f"jac_{tag}"] = round(j, 4); r[f"dice_{tag}"] = round(d, 4)
            chg = np.logical_xor(a, b); nchg = int(chg.sum())
            r[f"pctchg_{tag}"] = round(100 * nchg / int(V.sum()), 4)
            for bd in BANDS:                                            # enriquecimento normalizado
                fc = (np.logical_and(chg, dist <= bd).sum() / nchg) if nchg else np.nan
                fv = np.logical_and(V, dist <= bd).sum() / V.sum()
                r[f"E{bd}_{tag}"] = round(fc / fv, 3) if (nchg and fv > 0) else ""
        # descritores de M3 em V: ocupação (pp), L_skel, N_br — assinado/absoluto/relativo
        occ_o = 100 * (mo["M3"] & V).sum() / V.sum(); occ_r = 100 * (mr["M3"] & V).sum() / V.sum()
        Lo, So = Lskel(mo["M3"] & V); Lr, Sr = Lskel(mr["M3"] & V)
        No, Nr = nbr(So), nbr(Sr)
        r["dOcc_pp"] = round(occ_r - occ_o, 4); r["absdOcc_pp"] = round(abs(occ_r - occ_o), 4)
        r["reldL"] = round((Lr - Lo) / Lo, 4) if Lo > 0 else ""
        r["absreldL"] = round(abs(Lr - Lo) / Lo, 4) if Lo > 0 else ""
        r["reldNbr"] = round((Nr - No) / No, 4) if No > 0 else ""
        r["absreldNbr"] = round(abs(Nr - No) / No, 4) if No > 0 else ""
        rows.append(r)
        if k % 10 == 0 or k == len(masks):
            print(f"  [{k}/{len(masks)}] {mp.stem}: Jac(M3)={r['jac_M3']:.3f} E60(M3)={r.get('E60_M3','')}")

    with open(C.METRICAS / "A9_ablacao.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    def mi(k):
        v = sorted(r[k] for r in rows if r[k] != "" and not (isinstance(r[k], float) and np.isnan(r[k])))
        q = np.percentile(v, [25, 50, 75]); return q[1], q[0], q[2]
    print(f"\n[A9] RESUMO (mediana [IIQ], {len(rows)} imagens; V exclui mistura, dilatação {BLEND_EXCL}px):")
    for k, lab in [("V_pct", "área válida V (% do quadro)"),
                   ("jac_M3", "Jaccard M3 (orig×recon)"), ("dice_M3", "Dice M3"),
                   ("jac_M1", "Jaccard M1"), ("jac_M2", "Jaccard M2"),
                   ("pctchg_M3", "% de V alterada (M3)"),
                   ("dOcc_pp", "Δocupação assinada (pp)"), ("absdOcc_pp", "|Δocupação| (pp)"),
                   ("absreldL", "|ΔL_skel| relativo"), ("absreldNbr", "|ΔN_br| relativo"),
                   ("E60_M1", "E60 M1 (enriq. ≤60px)"), ("E60_M2", "E60 M2"), ("E60_M3", "E60 M3")]:
        md, q1, q3 = mi(k)
        print(f"   {lab:34s} {md:8.3f} [{q1:.3f}, {q3:.3f}]")
    print(f"\n[A9] -> metricas/A9_ablacao.csv")


if __name__ == "__main__":
    main()
