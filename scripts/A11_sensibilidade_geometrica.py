#!/usr/bin/env python3
"""
Title:
    Geometric sensitivity of descriptors
File type:
    Script
Purpose:
    Re-runs the full segmentation chain on images subjected to six small affine perturbations
    (translation, scale, rotation) and reports signed and absolute relative descriptor changes and
    rank correlations.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-30
Date:
    2026-07-30
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
Outputs:
    - metricas/A11_sensibilidade_geometrica.csv
    - metricas/A11_sensibilidade_resumo.csv
Dependencies:
    - cv2
    - numpy
    - scipy
    - segmentation_models_pytorch
    - skimage
    - torch
    - local: config
Execution:
    python scripts/A11_sensibilidade_geometrica.py (from a workspace prepared with
    tools/prepare_workspace.py)
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
A11 — Sensibilidade dos descritores ao enquadramento (deslocamento, escala, rotação).

Motivação (auditoria 2026-07-30, item 10): o enquadramento não tem fiducial nem borda do
rizotron, logo não se garante que o mesmo pixel represente a mesma região física entre
coletas. Variações de distância lente–vidro, inclinação e enquadramento podem, portanto,
contribuir para as mudanças longitudinais observadas. Este script quantifica esse efeito.

Delineamento (pareado, por imagem):
  1. Parte da imagem CONDICIONADA (05A, sem flash) e da respectiva máscara de inpainting.
  2. Aplica uma transformação afim que SIMULA um reenquadramento (translação, escala ou
     rotação), à imagem e à máscara de inpainting, com a MESMA matriz.
  3. Recorta, tanto da referência quanto da versão perturbada, a MESMA região interior
     (margem MARGEM), de modo que nenhuma das duas contenha borda indefinida.
  4. Reexecuta a cadeia completa de segmentação sobre as duas: M1 (Frangi), M2 (U-Net) e
     M3 = C(R(M1) u M2) — a perturbação atravessa realmente os segmentadores.
  5. Compara os descritores (O, L_skel, N_br, D50, F_prof) entre referência e perturbada.

O que a análise responde: quanto de variação nos descritores é explicável por um
reenquadramento plausível, sem qualquer mudança biológica. É o piso de ruído geométrico
contra o qual as tendências temporais devem ser lidas.

Saídas:
  metricas/A11_sensibilidade_geometrica.csv       (1 linha por imagem x perturbação)
  metricas/A11_sensibilidade_resumo.csv           (resumo por perturbação e descritor)
"""
import os
import sys
import csv
import math
import time
import statistics as st

import numpy as np
import cv2
import torch
import segmentation_models_pytorch as smp

from skimage import io as skio, img_as_float
from skimage.color import rgb2lab
from skimage.filters import frangi, gaussian, threshold_otsu
from skimage.exposure import equalize_adapthist
from skimage.morphology import (binary_opening, binary_closing, disk,
                                remove_small_objects, skeletonize)
from skimage.measure import label as sklabel, regionprops
from scipy.ndimage import convolve, label as ndlabel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

EPS = 1e-8
IN_DIR = C.SAIDAS / "05A_tratadas"
INPAINT_DIR = IN_DIR / "_mascaras"
MODELO = C.MODELOS / "external_final_model_PRMI_all.pt"
OUT_LONG = C.METRICAS / "A11_sensibilidade_geometrica.csv"
OUT_RES = C.METRICAS / "A11_sensibilidade_resumo.csv"

# margem interior descartada dos DOIS lados da comparação (fração de cada eixo).
# Cobre com folga o maior deslocamento gerado pelas perturbações abaixo.
MARGEM = 0.04

# --- refinamento R(M1), idêntico a 08E_refinamento.py ---
AREA_GRANDE, ECC_MIN, AREA_FINA_MIN, FECHA = 350, 0.90, 60, 3

# --- inferência M2, idêntica a 06C_inferencia.py ---
ENCODER, LONG, THR = "resnet34", 1024, 0.5
IMEAN = np.array([0.485, 0.456, 0.406], np.float32)
ISTD = np.array([0.229, 0.224, 0.225], np.float32)
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

Z_PROF = 0.60          # corte de profundidade para F_prof (Fase 09 / A4)

# Perturbações: (rótulo, tipo, magnitude). Escolhidas na ordem de grandeza de um
# reenquadramento manual plausível entre coletas.
PERTURBACOES = [
    ("desloc_x_+1pct", "shift_x", 0.01),
    ("desloc_y_+1pct", "shift_y", 0.01),
    ("escala_+2pct", "scale", 1.02),
    ("escala_-2pct", "scale", 0.98),
    ("rotacao_+1deg", "rot", 1.0),
    ("rotacao_-1deg", "rot", -1.0),
]


# ----------------------------------------------------------------------
# Segmentação (réplica fiel de 07_frangi.py, 06C e 08E)
# ----------------------------------------------------------------------
def m1_frangi(rgb):
    """
    Purpose:
        Segment M1 on an RGB image with the production Frangi parameters.
    Parameters:
        rgb: image
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    L = rgb2lab(rgb)[:, :, 0]
    Ln = (L - L.min()) / (L.max() - L.min() + EPS)
    BL = gaussian(Ln, sigma=C.FLATFIELD_SIGMA)
    Lcorr = np.clip(Ln / (BL + EPS) * np.median(BL), 0, 1)
    Lclahe = equalize_adapthist(Lcorr, clip_limit=C.CLAHE_CLIP)

    Mglare = Lclahe >= C.GLARE_TAU_L
    Mglare = binary_closing(binary_opening(Mglare, disk(3)), disk(3))
    frac = float(Mglare.mean())
    if 0 < frac <= C.GLARE_INPAINT_MAX:
        Lu = (Lclahe * 255).astype(np.uint8)
        Lu = cv2.inpaint(Lu, (Mglare * 255).astype(np.uint8),
                         C.GLARE_INPAINT_RADIUS, cv2.INPAINT_TELEA)
        Lclahe = Lu.astype(np.float32) / 255.0
        Mvalid = np.ones_like(Mglare)
    else:
        Mvalid = ~Mglare

    V = frangi(Lclahe, sigmas=C.FRANGI_SIGMAS, black_ridges=C.FRANGI_BLACK_RIDGES)
    V = V / (V.max() + EPS)
    if C.THRESH_METHOD == "percentile":
        T = float(np.percentile(V, C.THRESH_PERCENTILE))
    else:
        try:
            T = float(threshold_otsu(V[V > 0]))
        except Exception:
            T = C.FRANGI_THRESHOLD
    M = (V >= T) & Mvalid
    if C.MORPH_OPEN_R:
        M = binary_opening(M, disk(C.MORPH_OPEN_R))
    M = remove_small_objects(M, min_size=C.A_MIN)
    if C.MORPH_CLOSE_R:
        M = binary_closing(M, disk(C.MORPH_CLOSE_R))
    return M


def m2_unet(model, rgb_u8):
    """
    Purpose:
        Segment M2 with the U-Net.
    Parameters:
        model: U-Net
        rgb_u8: 8-bit image
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    H0, W0 = rgb_u8.shape[:2]
    s = LONG / max(H0, W0)
    Hn = max(32, int(round(H0 * s / 32)) * 32)
    Wn = max(32, int(round(W0 * s / 32)) * 32)
    img = cv2.resize(rgb_u8, (Wn, Hn)).astype(np.float32) / 255.0
    x = torch.from_numpy(((img - IMEAN) / ISTD).transpose(2, 0, 1)).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        pr = torch.sigmoid(model(x))[0, 0].float().cpu().numpy()
    pr = cv2.resize(pr, (W0, H0), interpolation=cv2.INTER_LINEAR)
    return pr >= THR


def refinar_m1(m1):
    """
    Purpose:
        Refine M1 by component filtering as in 08E.
    Parameters:
        m1: M1 mask
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    lab = sklabel(m1)
    keep = np.zeros_like(m1, dtype=bool)
    for p in regionprops(lab):
        if p.area >= AREA_GRANDE or (p.area >= AREA_FINA_MIN and p.eccentricity >= ECC_MIN):
            keep[lab == p.label] = True
    return keep


def m3_combinar(m1, m2):
    """
    Purpose:
        Form M3 as the refined M1 united with M2 and closed.
    Parameters:
        m1: M1 mask
        m2: M2 mask
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    comb = refinar_m1(m1) | m2
    if FECHA:
        comb = binary_closing(comb, disk(FECHA))
    return comb


# ----------------------------------------------------------------------
# Descritores (subconjunto usado nas comparações do artigo)
# ----------------------------------------------------------------------
def comprimento_skel(S):
    """
    Purpose:
        Estimate skeleton length counting horizontal/vertical and diagonal neighbour links.
    Parameters:
        S: binary skeleton
    Returns:
        float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    n_h = int(np.logical_and(S[:, :-1], S[:, 1:]).sum())
    n_v = int(np.logical_and(S[:-1, :], S[1:, :]).sum())
    n_d = int(np.logical_and(S[:-1, :-1], S[1:, 1:]).sum()
              + np.logical_and(S[:-1, 1:], S[1:, :-1]).sum())
    return n_h + n_v + n_d * math.sqrt(2.0)


def descritores(M, inpaint):
    """
    Purpose:
        Compute descriptors of a mask excluding reconstructed pixels.
    Parameters:
        M: mask
        inpaint: reconstruction mask
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    H, W = M.shape
    Mv = M & ~inpaint
    a_valid = int(H * W - int(inpaint.sum()))
    a_px = int(Mv.sum())
    d = {"O": a_px / a_valid if a_valid > 0 else 0.0}
    if a_px == 0:
        d.update({"L_skel": 0.0, "N_br": 0, "D50": 0.0, "F_prof": 0.0})
        return d
    S = skeletonize(Mv)
    d["L_skel"] = comprimento_skel(S)
    deg = convolve(S.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - S
    J = np.logical_and(S, deg >= 3)
    _, n_br = ndlabel(J, structure=np.ones((3, 3)))
    d["N_br"] = int(n_br)
    ys, _ = np.where(Mv)
    z = ys / float(H)                       # profundidade normalizada (0 topo, 1 base)
    d["D50"] = float(np.percentile(z, 50))
    d["F_prof"] = float((z >= Z_PROF).mean())
    return d


# ----------------------------------------------------------------------
# Perturbação geométrica
# ----------------------------------------------------------------------
def matriz(tipo, mag, H, W):
    """
    Purpose:
        Build the affine matrix of a perturbation.
    Parameters:
        tipo: translation, scale or rotation
        mag: magnitude
        H, W: image size
    Returns:
        numpy 2x3 array
    Raises:
        ValueError (raised explicitly in the body)
    Notes:
        Parameter types are not annotated in the original code.
    """
    cx, cy = W / 2.0, H / 2.0
    if tipo == "shift_x":
        return np.float32([[1, 0, mag * W], [0, 1, 0]])
    if tipo == "shift_y":
        return np.float32([[1, 0, 0], [0, 1, mag * H]])
    if tipo == "scale":
        return cv2.getRotationMatrix2D((cx, cy), 0.0, mag)
    if tipo == "rot":
        return cv2.getRotationMatrix2D((cx, cy), mag, 1.0)
    raise ValueError(tipo)


def recorte_interior(a):
    """
    Purpose:
        Crop the common interior region discarding a 4% margin.
    Parameters:
        a: array
    Returns:
        array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    H, W = a.shape[:2]
    my, mx = int(round(MARGEM * H)), int(round(MARGEM * W))
    return a[my:H - my, mx:W - mx]


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
    C.METRICAS.mkdir(parents=True, exist_ok=True)
    def valida(p):
        return not any(x in p.parts for x in ("_mascaras", "_previas"))
    imgs = sorted([p for p in IN_DIR.rglob("*.png") if valida(p)])
    if not imgs:
        print("[A11] Sem imagens condicionadas em", IN_DIR)
        return

    model = smp.Unet(encoder_name=ENCODER, encoder_weights=None,
                     in_channels=3, classes=1).to(DEVICE)
    model.load_state_dict(torch.load(MODELO, map_location=DEVICE))
    model.eval()
    print(f"[A11] {len(imgs)} imagens | {len(PERTURBACOES)} perturbações | device={DEVICE}")
    print(f"[A11] margem interior descartada = {MARGEM:.0%} de cada eixo")

    linhas = []
    t0 = time.time()
    for i, p in enumerate(imgs, 1):
        rel = p.relative_to(IN_DIR)
        data = rel.parts[0] if len(rel.parts) > 1 else ""
        riz = p.stem.split("_")[0]

        rgb_u8 = cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB)
        H, W = rgb_u8.shape[:2]
        ip_path = INPAINT_DIR / rel
        if ip_path.exists():
            ip = cv2.imread(str(ip_path), 0)
            if ip.shape != (H, W):
                ip = cv2.resize(ip, (W, H), interpolation=cv2.INTER_NEAREST)
        else:
            ip = np.zeros((H, W), np.uint8)

        # --- referência: mesmo recorte interior, sem transformação ---
        ref_rgb = recorte_interior(rgb_u8)
        ref_ip = recorte_interior(ip) > 127
        m1 = m1_frangi(img_as_float(ref_rgb))
        m2 = m2_unet(model, ref_rgb)
        d_ref = descritores(m3_combinar(m1, m2), ref_ip)

        for rot, tipo, mag in PERTURBACOES:
            Mt = matriz(tipo, mag, H, W)
            wr = cv2.warpAffine(rgb_u8, Mt, (W, H), flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_REFLECT_101)
            wi = cv2.warpAffine(ip, Mt, (W, H), flags=cv2.INTER_NEAREST,
                                borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            c_rgb = recorte_interior(wr)
            c_ip = recorte_interior(wi) > 127
            m1p = m1_frangi(img_as_float(c_rgb))
            m2p = m2_unet(model, c_rgb)
            d_p = descritores(m3_combinar(m1p, m2p), c_ip)

            linha = {"image_id": p.stem, "rizotron": riz, "data": data,
                     "tratamento": C.tratamento(riz)[0], "perturbacao": rot,
                     "tipo": tipo, "magnitude": mag}
            for k in ("O", "L_skel", "N_br", "D50", "F_prof"):
                r, v = float(d_ref[k]), float(d_p[k])
                linha[f"{k}_ref"] = round(r, 6)
                linha[f"{k}_pert"] = round(v, 6)
                linha[f"{k}_dabs"] = round(v - r, 6)
                linha[f"{k}_drel_pct"] = round(100.0 * (v - r) / r, 3) if r else ""
            linhas.append(linha)

        el = time.time() - t0
        print(f"  [{i:>3}/{len(imgs)}] {rel}  ({el/i:.1f} s/img, ~{(len(imgs)-i)*el/i/60:.0f} min restantes)",
              flush=True)

    with open(OUT_LONG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    # ---- resumo por perturbação x descritor ----
    try:
        from scipy.stats import spearmanr
    except Exception:
        spearmanr = None
    res = []
    for rot, tipo, mag in PERTURBACOES:
        sub = [l for l in linhas if l["perturbacao"] == rot]
        for k in ("O", "L_skel", "N_br", "D50", "F_prof"):
            rel_v = [l[f"{k}_drel_pct"] for l in sub if l[f"{k}_drel_pct"] != ""]
            ref_v = [l[f"{k}_ref"] for l in sub]
            per_v = [l[f"{k}_pert"] for l in sub]
            rho = spearmanr(ref_v, per_v).correlation if (spearmanr and len(ref_v) > 2) else ""
            res.append({
                "perturbacao": rot, "descritor": k, "n": len(sub),
                "drel_mediana_pct": round(st.median(rel_v), 3) if rel_v else "",
                "drel_abs_mediana_pct": round(st.median([abs(x) for x in rel_v]), 3) if rel_v else "",
                "drel_p90_abs_pct": round(sorted(abs(x) for x in rel_v)[int(0.9 * len(rel_v))], 3) if rel_v else "",
                "spearman_ref_vs_pert": round(float(rho), 4) if rho != "" else "",
            })
    with open(OUT_RES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)

    print(f"\n[A11] {OUT_LONG.name} ({len(linhas)} linhas) e {OUT_RES.name} gravados.")
    print(f"[A11] tempo total: {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
