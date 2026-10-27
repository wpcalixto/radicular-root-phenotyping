#!/usr/bin/env python3
"""
Title:
    Union of M1 and M2
File type:
    Script
Purpose:
    Forms the union of M1 and M2 masks (M1 already without components below the minimum area) as the
    unrefined combined mask.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-07
Date:
    2026-07-07
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
    - metricas/combinado_parameters.csv
    - saidas/08_combinado/masks
    - saidas/08_combinado/masks/<data>/<id>.png
Dependencies:
    - cv2
    - numpy
    - local: config
Execution:
    python scripts/08_combinacao.py (from a workspace prepared with tools/prepare_workspace.py)
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
Método COMBINADO (3º candidato da Fase 08): M^Comb = M^Frangi ∪ M^Ext.

Motivação (caderno 6e): Frangi e modelo externo são COMPLEMENTARES — Frangi pega
raízes finas (mas ruidoso e perde as grossas); o modelo externo (PRMI) traça as raízes
principais grossas de forma limpa (mas perde as finas). A união aproveita os dois.

Entradas:
  saidas/07_frangi/masks/<data>/<id>.png        (M^Frangi; já sem componentes < A_MIN)
  saidas/06C_inferencia/masks/<data>/<id>.png   (M^Ext)
Saída:
  saidas/08_combinado/masks/<data>/<id>.png     (M^Comb = união binária)
  metricas/combinado_parameters.csv             (cobertura por imagem)
"""
import os
import sys
import csv

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

FR = C.SAIDAS / "07_frangi" / "masks"
EX = C.SAIDAS / "06C_inferencia" / "masks"
OUT = C.SAIDAS / "08_combinado" / "masks"
CSV = C.METRICAS / "combinado_parameters.csv"


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
    frangi = sorted(FR.rglob("*.png"))
    if not frangi:
        print("[Comb] Sem máscaras Frangi (rode a Fase 07)."); return

    rows = []
    for p in frangi:
        rel = p.relative_to(FR)
        pe = EX / rel
        if not pe.exists():
            print(f"  [pula] {rel}: falta M^Ext"); continue
        mf = cv2.imread(str(p), 0) > 127
        me = cv2.imread(str(pe), 0) > 127
        comb = (mf | me).astype(np.uint8) * 255

        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(dst), comb)

        H, W = comb.shape
        cpx = int((comb > 0).sum())
        rows.append({
            "image_id": p.stem,
            "data": rel.parts[0] if len(rel.parts) > 1 else "",
            "frangi_pct": round(100 * mf.sum() / (H * W), 3),
            "ext_pct": round(100 * me.sum() / (H * W), 3),
            "comb_pct": round(100 * cpx / (H * W), 3),
        })

    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    import statistics as st
    print(f"[Comb] {len(rows)} máscaras combinadas -> {OUT.relative_to(C.ROOT)}/")
    print(f"   cobertura média: Frangi {st.mean(r['frangi_pct'] for r in rows):.2f}%  "
          f"Ext {st.mean(r['ext_pct'] for r in rows):.2f}%  "
          f"Comb {st.mean(r['comb_pct'] for r in rows):.2f}%")
    print(f"   log: {CSV.relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
