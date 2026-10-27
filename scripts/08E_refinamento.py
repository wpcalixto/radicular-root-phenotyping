#!/usr/bin/env python3
"""
Title:
    M3 refinement (Frangi denoising before union)
File type:
    Script
Purpose:
    Removes small, rounded M1 components while keeping elongated and large ones, unites the result
    with M2 and applies a final closing to produce the final M3 masks.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-08
Date:
    2026-07-08
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
    - saidas/06C_inferencia/masks
    - saidas/07_frangi/masks
Outputs:
    - metricas/combinado_limpo_parameters.csv
    - saidas/08_combinado_limpo/masks
    - saidas/08_combinado_limpo/masks/<data>/<id>.png
Dependencies:
    - cv2
    - numpy
    - skimage
    - local: config
Execution:
    python scripts/08E_refinamento.py (from a workspace prepared with tools/prepare_workspace.py)
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
Método M3 "limpo" — refina o combinado reduzindo os erros apontados pelos especialistas
no M3 (excesso_solo 99%, fragmentado 93%), que vêm do ruído do Frangi (M1).

Ideia: antes da união com o M2 (PRMI, já limpo), DENOISE do M1 (Frangi):
  - remove componentes PEQUENOS e ARREDONDADOS (textura/ruído do solo);
  - mantém componentes ALONGADOS (raízes finas, mesmo curtas) e os GRANDES.
Depois:  M3_limpo = M2 ∪ M1_denoise  ->  opcional fechamento leve para reduzir fragmentação.

Entradas:
  saidas/07_frangi/masks/<data>/<id>.png        (M1 = Frangi)
  saidas/06C_inferencia/masks/<data>/<id>.png   (M2 = Ext/PRMI)
Saídas:
  saidas/08_combinado_limpo/masks/<data>/<id>.png
  metricas/combinado_limpo_parameters.csv
"""
import os
import sys
import csv

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from skimage.measure import label, regionprops

FR = C.SAIDAS / "07_frangi" / "masks"          # M1
EX = C.SAIDAS / "06C_inferencia" / "masks"     # M2
OUT = C.SAIDAS / "08_combinado_limpo" / "masks"
CSV = C.METRICAS / "combinado_limpo_parameters.csv"

# denoise do M1 (Frangi): mantém componente se for grande OU alongado
AREA_GRANDE = 350      # componente grande é mantido de qualquer forma
ECC_MIN = 0.90         # excentricidade mínima p/ manter componente pequeno (linha ~0.99; blob ~0.6)
AREA_FINA_MIN = 60     # área mínima de um componente fino p/ manter
FECHA = 3              # fechamento leve final (px) p/ reduzir fragmentação sem colar ruído


def denoise_frangi(m1):
    """
    Purpose:
        Remove small, rounded M1 components and keep elongated or large ones (refinement used for the final M3).
    Parameters:
        m1: M1 binary mask
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    lab = label(m1)
    keep = np.zeros_like(m1, dtype=bool)
    for p in regionprops(lab):
        if p.area >= AREA_GRANDE:
            keep[lab == p.label] = True
        elif p.area >= AREA_FINA_MIN and p.eccentricity >= ECC_MIN:
            keep[lab == p.label] = True
    return keep


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
    m1s = sorted(FR.rglob("*.png"))
    if not m1s:
        print("[M3limpo] Sem máscaras Frangi (Fase 07)."); return

    rows = []
    for p in m1s:
        rel = p.relative_to(FR)
        pe = EX / rel
        if not pe.exists():
            print(f"  [pula] {rel}: falta M2"); continue
        m1 = cv2.imread(str(p), 0) > 127
        m2 = cv2.imread(str(pe), 0) > 127

        m1d = denoise_frangi(m1)
        comb = m1d | m2
        if FECHA:
            comb = cv2.morphologyEx(comb.astype(np.uint8), cv2.MORPH_CLOSE,
                                    np.ones((FECHA, FECHA), np.uint8)).astype(bool)

        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(dst), (comb * 255).astype(np.uint8))

        H, W = comb.shape
        n_m3 = int(label(m1 | m2).max())
        n_lim = int(label(comb).max())
        rows.append({
            "image_id": p.stem, "data": rel.parts[0] if len(rel.parts) > 1 else "",
            "m1_frangi_pct": round(100 * m1.sum() / (H * W), 3),
            "m1_denoise_pct": round(100 * m1d.sum() / (H * W), 3),
            "m2_ext_pct": round(100 * m2.sum() / (H * W), 3),
            "m3_limpo_pct": round(100 * comb.sum() / (H * W), 3),
            "n_comp_m3": n_m3, "n_comp_m3_limpo": n_lim,
        })

    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    import statistics as st
    print(f"[M3limpo] {len(rows)} máscaras -> {OUT.relative_to(C.ROOT)}/")
    print(f"   cobertura média: M1={st.mean(r['m1_frangi_pct'] for r in rows):.2f}% "
          f"-> M1_denoise={st.mean(r['m1_denoise_pct'] for r in rows):.2f}%  "
          f"M3_limpo={st.mean(r['m3_limpo_pct'] for r in rows):.2f}%")
    print(f"   componentes médios: M3={st.mean(r['n_comp_m3'] for r in rows):.0f} "
          f"-> M3_limpo={st.mean(r['n_comp_m3_limpo'] for r in rows):.0f} (menos fragmentação)")
    print(f"   log: {CSV.relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
