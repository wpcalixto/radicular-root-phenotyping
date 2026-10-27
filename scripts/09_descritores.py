#!/usr/bin/env python3
"""
Title:
    Morphological descriptors per image
File type:
    Script
Purpose:
    Extracts pixel-based root descriptors (area, occupancy, skeleton length, branch nodes, depth
    distribution) from the final M3 masks, excluding reconstructed pixels from numerator and
    denominator; also for M1 and M2.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-31
Date:
    2026-07-31
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
    - saidas/05A_tratadas/_mascaras
    - saidas/06C_inferencia/masks
    - saidas/07_frangi/masks
    - saidas/08_combinado_limpo/masks
Outputs:
    - metricas/root_density_by_layer.csv
    - metricas/root_features_by_image.csv
    - metricas/root_features_by_treatment_dap.csv
Dependencies:
    - cv2
    - numpy
    - scipy
    - skimage
    - local: config
Execution:
    python scripts/09_descritores.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs
    byte-identical to the archived versions. Environment of the verification: Python 3.9.6 (macOS)
    with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Fase 09 — Extração de descritores radiculares (por imagem).

Máscara-fonte: M3 "limpo" (método escolhido na Fase 08 = Frangi ∪ PRMI, denoise).
EXCLUI a área inpintada na 05A (onde o flash destruiu o sinal → raiz não é medível).

UNIDADES = PIXELS. O enquadramento não tem borda do rizotron nem fiducial, logo não
há escala métrica confiável (px->cm exigiria s_x=s_y isotrópico, e 60/W_px != 80/H_px).
Os descritores são reportados em pixels, proporção da área válida e profundidade
NORMALIZADA (0–1), o que preserva a comparabilidade sem conversão métrica não sustentada.

Descritores (metodologia):
  A_px (área em px), O (ocupação = A_px/quadro), D_max_norm (profundidade/altura),
  W_max_norm (largura/largura do quadro), L_skel_px (comprimento esqueletizado =
  n_h + n_v + n_d·√2), B (pontos de ramificação, grau≥3),
  ρ_l (densidade por 10 faixas de profundidade normalizada),
  A_hull_px (envoltório convexo), F_hull (índice de preenchimento).

Saídas:
  metricas/root_features_by_image.csv      (1 linha por imagem)
  metricas/root_density_by_layer.csv       (imagem × faixa; ρ e comprimento por profundidade)
  metricas/root_features_by_treatment_dap.csv  (média por tratamento × DAP)
"""
import os
import sys
import csv
import math
import statistics as st
from collections import defaultdict

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from skimage.morphology import skeletonize, convex_hull_image
from scipy.ndimage import convolve, label

# Máscara-fonte parametrizável: por padrão M3 (método selecionado). Passando o rótulo
# do método como argumento (M1|M2|M3), extrai os mesmos descritores das máscaras dos
# ramos isolados, para a análise de sensibilidade à escolha do segmentador.
_METODOS = {
    "M3": (C.SAIDAS / "08_combinado_limpo" / "masks", ""),
    "M1": (C.SAIDAS / "07_frangi" / "masks", "_M1"),
    "M2": (C.SAIDAS / "06C_inferencia" / "masks", "_M2"),
}
_MET = sys.argv[1].upper() if len(sys.argv) > 1 and sys.argv[1].upper() in _METODOS else "M3"
MASK_DIR, _SUF = _METODOS[_MET]
INPAINT_DIR = C.SAIDAS / "05A_tratadas" / "_mascaras"    # região inpintada (excluir)
OUT_IMG = C.METRICAS / f"root_features_by_image{_SUF}.csv"
OUT_LAYER = C.METRICAS / f"root_density_by_layer{_SUF}.csv"
OUT_TRAT = C.METRICAS / f"root_features_by_treatment_dap{_SUF}.csv"


def comprimento_skel(S):
    """L (px) = n_h + n_v + n_d·√2 — arestas do esqueleto (contadas uma vez)."""
    n_h = int(np.logical_and(S[:, :-1], S[:, 1:]).sum())
    n_v = int(np.logical_and(S[:-1, :], S[1:, :]).sum())
    n_d = int(np.logical_and(S[:-1, :-1], S[1:, 1:]).sum()
              + np.logical_and(S[:-1, 1:], S[1:, :-1]).sum())
    return n_h + n_v + n_d * math.sqrt(2.0)


def descritores(M, inpaint):
    """Descritores em PIXELS / proporção / profundidade normalizada (sem cm)."""
    H, W = M.shape
    Mv = M & ~inpaint                                    # exclui área inpintada (numerador)
    a_valid = int((H * W) - int(inpaint.sum()))          # área válida = quadro - inpaint (denominador)
    d = {}
    a_px = int(Mv.sum())
    d["A_px"] = a_px
    # ocupação normalizada pela ÁREA VÁLIDA (não pelo quadro cheio): evita subestimar
    # imagens com maior fração reconstruída, que têm denominador menor.
    d["O_ocupacao"] = round(a_px / a_valid, 5) if a_valid > 0 else 0
    d["inpintado_pct"] = round(100 * inpaint.sum() / (H * W), 3)
    if a_px == 0:
        d.update({"Dmax_px": 0, "Dmax_norm": 0, "Wmax_px": 0, "Wmax_norm": 0,
                  "L_skel_px": 0, "B_ramif": 0, "N_br": 0, "A_hull_px": 0, "F_hull": 0})
        return d, Mv
    ys, xs = np.where(Mv)
    dmax_px = int(ys.max() - ys.min())
    wmax_px = int(xs.max() - xs.min())
    d["Dmax_px"] = dmax_px
    d["Dmax_norm"] = round(dmax_px / H, 4)              # profundidade normalizada (0–1)
    d["Wmax_px"] = wmax_px
    d["Wmax_norm"] = round(wmax_px / W, 4)              # largura normalizada (0–1)
    S = skeletonize(Mv)
    d["L_skel_px"] = round(comprimento_skel(S), 1)
    deg = convolve(S.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - S
    J = np.logical_and(S, deg >= 3)                     # pixels de junção (grau≥3)
    d["B_ramif"] = int(J.sum())                          # nº de pixels de junção (legado)
    _, d["N_br"] = label(J, structure=np.ones((3, 3)))   # nº de nós de ramificação (clusters 8-conex.)
    hull = convex_hull_image(Mv)
    a_hull = float(hull.sum())
    d["A_hull_px"] = int(a_hull)
    d["F_hull"] = round(a_px / a_hull, 4) if a_hull > 0 else 0
    return d, Mv


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
    masks = sorted(MASK_DIR.rglob("*.png"))
    if not masks:
        print("[Fase 09] Sem máscaras M3-limpo (rode 08E)."); return

    img_rows, layer_rows = [], []
    for p in masks:
        rel = p.relative_to(MASK_DIR)
        data = rel.parts[0] if len(rel.parts) > 1 else ""
        riz = p.stem.split("_")[0]
        M = cv2.imread(str(p), 0) > 127
        H, W = M.shape
        ip_path = INPAINT_DIR / rel
        inpaint = (cv2.imread(str(ip_path), 0) > 127) if ip_path.exists() else np.zeros_like(M)
        if inpaint.shape != M.shape:        # garante alinhamento máscara×inpaint
            inpaint = cv2.resize(inpaint.astype(np.uint8), (M.shape[1], M.shape[0]),
                                 interpolation=cv2.INTER_NEAREST) > 0

        d, Mv = descritores(M, inpaint)
        cod, nome = C.tratamento(riz)
        dt = C.parse_data_pasta(data) if data else None
        row = {"image_id": p.stem, "rizotron": riz, "data": data,
               "tratamento": cod, "replicata": C.replicata(riz),
               "DAP": C.dap(dt) if dt else "", "coleta": (C.COLETAS.index(data) + 1) if data in C.COLETAS else ""}
        row.update(d)
        img_rows.append(row)

        # faixas de profundidade normalizada — ρ por área e comprimento por faixa
        nlay = C.N_CAMADAS
        bh = H // nlay
        for l in range(nlay):
            y0, y1 = l * bh, (H if l == nlay - 1 else (l + 1) * bh)
            band = Mv[y0:y1, :]
            band_ip = inpaint[y0:y1, :]
            valido = band.size - int(band_ip.sum())
            Sb = skeletonize(band) if band.any() else np.zeros_like(band)
            layer_rows.append({
                "image_id": p.stem, "rizotron": riz, "data": data,
                "tratamento": cod, "DAP": row["DAP"], "faixa": l + 1,
                "prof_frac_ini": round(l / nlay, 3), "prof_frac_fim": round((l + 1) / nlay, 3),
                "root_px": int(band.sum()),
                "rho_area": round(band.sum() / band.size, 6),
                "rho_area_valida": round(band.sum() / valido, 6) if valido > 0 else 0,
                "L_skel_px": round(comprimento_skel(Sb), 1),
            })
        print(f"  {rel}  A={d['A_px']}px  L={d['L_skel_px']}px  Dmax={d['Dmax_norm']}  B={d['B_ramif']}")

    with open(OUT_IMG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(img_rows[0].keys())); w.writeheader(); w.writerows(img_rows)
    with open(OUT_LAYER, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(layer_rows[0].keys())); w.writeheader(); w.writerows(layer_rows)

    # agregação por tratamento × DAP (médias) — base para as séries temporais
    agg = defaultdict(list)
    for r in img_rows:
        agg[(r["tratamento"], r["DAP"], r["data"])].append(r)
    trat_rows = []
    METRICAS_AGG = ["A_px", "L_skel_px", "Dmax_norm", "Wmax_norm", "B_ramif", "N_br", "O_ocupacao", "F_hull"]
    for (trat, dap, data), rs in sorted(agg.items(), key=lambda k: (k[0][0], k[0][1] if k[0][1] != "" else 0)):
        linha = {"tratamento": trat, "DAP": dap, "data": data, "n": len(rs)}
        for m in METRICAS_AGG:
            vals = [r[m] for r in rs]
            linha[m + "_media"] = round(st.mean(vals), 4)
            linha[m + "_dp"] = round(st.pstdev(vals), 4) if len(vals) > 1 else 0
        trat_rows.append(linha)
    with open(OUT_TRAT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(trat_rows[0].keys())); w.writeheader(); w.writerows(trat_rows)

    print(f"\n[Fase 09] {len(img_rows)} imagens -> {OUT_IMG.relative_to(C.ROOT)}")
    print(f"   por camada: {OUT_LAYER.relative_to(C.ROOT)}  ({len(layer_rows)} linhas)")
    print(f"   por tratamento×DAP: {OUT_TRAT.relative_to(C.ROOT)}")
    print(f"   L_skel médio: {st.mean(r['L_skel_px'] for r in img_rows):.0f} px | "
          f"A médio: {st.mean(r['A_px'] for r in img_rows):.0f} px | "
          f"inpintado médio: {st.mean(r['inpintado_pct'] for r in img_rows):.1f}%")


if __name__ == "__main__":
    main()
