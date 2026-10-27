#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    Fleiss kappa for dichotomised scores
File type:
    Script
Purpose:
    Computes the 95% interval of Fleiss kappa for scores dichotomised at 3 using the rhizotron-
    clustered resampling of A12.
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
    - none detected by static analysis
Outputs:
    - printed results only
Dependencies:
    - numpy
Execution:
    python scripts/A12b_kappa_dicotomizado.py (from a workspace prepared with
    tools/prepare_workspace.py)
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
"""IC95% do kappa de Fleiss no recorte dicotomizado (nota >= 3), pela mesma
reamostragem agrupada no rizotron usada em A12_concordancia_ic.py."""
import sys, importlib.util, numpy as np
from collections import defaultdict
sys.path.insert(0, 'scripts')
spec = importlib.util.spec_from_file_location("a12", "scripts/A12_concordancia_ic.py")
a12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(a12)

Q, A, riz, avals, alvos = a12.carregar_matrizes()
Qb = np.where(np.isnan(Q), np.nan, (Q >= 3).astype(float))   # 1 = nota boa ou superior
ponto = a12.fleiss(Qb, 2)
rizs = sorted(set(riz)); idx_por_riz = {r: np.where(riz == r)[0] for r in rizs}
rng = np.random.default_rng(a12.SEMENTE)
d = []
for _ in range(a12.B):
    esc = rng.choice(len(rizs), size=len(rizs), replace=True)
    idx = np.concatenate([idx_por_riz[rizs[e]] for e in esc])
    v = a12.fleiss(Qb[idx], 2)
    if not np.isnan(v): d.append(v)
lo, hi = np.percentile(d, [2.5, 97.5])
print("kappa de Fleiss, nota >= 3 : %.4f  IC95%% [%.4f ; %.4f]  (B=%d de %d)"
      % (ponto, lo, hi, len(d), a12.B))
print("confere com 08D_concordancia.csv (0,064)?", abs(ponto - 0.064) < 0.001)
