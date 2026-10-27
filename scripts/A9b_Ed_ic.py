#!/usr/bin/env python3
"""
Title:
    Intervals for spatial enrichment E_d
File type:
    Script
Purpose:
    Computes rhizotron-clustered bootstrap intervals of the median spatial enrichment E_d per method
    and distance band.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-08-01
Date:
    2026-08-01
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
    - metricas/A9_ablacao.csv
Outputs:
    - metricas/A9b_Ed_ic.csv
Dependencies:
    - numpy
    - local: config
Execution:
    python scripts/A9b_Ed_ic.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 5000. Verification in v1.0.0: re-executed in an isolated workspace built
    from the Dataset; outputs byte-identical to the archived versions. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""IC95% do enriquecimento espacial E_d das alteracoes de segmentacao junto a
regiao reconstruida, por reamostragem agrupada no rizotron (mesma convencao de A12).
Entrada: metricas/A9_ablacao.csv   Saida: metricas/A9b_Ed_ic.csv
"""
import os, sys, csv
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

B, SEMENTE = 5000, 42
r = list(csv.DictReader(open(C.METRICAS / "A9_ablacao.csv", encoding="utf-8")))
riz = np.array([x["image_id"].split("_")[0] for x in r])
rizs = sorted(set(riz)); idx = {k: np.where(riz == k)[0] for k in rizs}
out = []
print("faixa   metodo  mediana   IC95%%                n_img  n_riz")
for faixa in ("E60", "E120", "E240"):
    for met in ("M1", "M2", "M3"):
        v = np.array([float(x[f"{faixa}_{met}"]) for x in r])
        pt = float(np.median(v))
        rng = np.random.default_rng(SEMENTE); d = []
        for _ in range(B):
            e = rng.choice(len(rizs), size=len(rizs), replace=True)
            d.append(np.median(v[np.concatenate([idx[rizs[i]] for i in e])]))
        lo, hi = np.percentile(d, [2.5, 97.5])
        print("%-7s %-6s %7.3f   [%.3f ; %.3f]   %5d  %5d" % (faixa, met, pt, lo, hi, len(v), len(rizs)))
        out.append({"faixa_px": faixa[1:], "metodo": met, "E_d_mediana": round(pt, 3),
                    "IC95_lo": round(float(lo), 3), "IC95_hi": round(float(hi), 3),
                    "B": B, "unidade_reamostragem": "rizotron", "n_img": len(v)})
with open(C.METRICAS / "A9b_Ed_ic.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("\n-> metricas/A9b_Ed_ic.csv")
