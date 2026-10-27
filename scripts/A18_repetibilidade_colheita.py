#!/usr/bin/env python3
"""
Title:
    Relative consistency and harvested-root correspondence
File type:
    Script
Purpose:
    Computes between-collection rank consistency (Spearman, ICC(3,1)) of M3 descriptors and the
    correspondence of in situ descriptors and root mass with harvested projected length, with
    bootstrap and leave-one-out sensitivity.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-09-21
Date:
    2026-09-21
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
    - metricas/A4_profundidade.csv
    - metricas/multimodal_long.csv
    - metricas/multimodal_targets.csv
    - metricas/root_features_by_image.csv
    - metricas/root_features_by_image_M1.csv
    - metricas/root_features_by_image_M2.csv
    - metricas/root_harvested.csv
Outputs:
    - metricas/A18_insitu_colheita.csv
    - metricas/A18_repetibilidade.csv
Dependencies:
    - numpy
    - scipy
    - local: config
Execution:
    python scripts/A18_repetibilidade_colheita.py (from a workspace prepared with
    tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Verification in v1.0.0: re-executed in an isolated workspace built
    from the Dataset; outputs byte-identical to the archived versions. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
A18 — Repetibilidade dos descritores entre coletas e comparação in situ x raiz colhida.

Bloco 1 — Repetibilidade da ordenação dos rizotrons entre coletas (unidade = rizotron, n=12):
  Para O, L_skel, N_br (M3; root_features_by_image.csv) e D50 (A4_profundidade.csv), na
  janela comum C1-C6:
  1a. Spearman rho entre coletas consecutivas (C_k x C_{k+1}, k=1..5) e a mediana das cinco.
  1b. ICC(3,1) de consistencia (duas vias, coleta como efeito fixo), que remove a tendencia
      temporal comum e mede a estabilidade da posicao relativa de cada unidade.
  IC95% por reamostragem dos 12 rizotrons (B=5000, semente 42).
  Sensibilidade ao segmentador: 1a/1b para O de M1 e M2 (root_features_by_image_M{1,2}.csv).

Bloco 2 — Comprimento esqueletizado projetado da raiz colhida x observacao in situ
  (unidade = rizotron; n=9 com escala aceita; root_harvested.csv):
  2a. L_colhida (cm) x L_skel in situ na ultima coleta comum (C6)
  2b. L_colhida (cm) x O in situ em C6
  2c. L_colhida (cm) x AUC(O) C1-C6
  2d. L_colhida (cm) x M_R (reproduz o valor do manuscrito, para controle)
  Spearman rho, p, IC95% por reamostragem das unidades e faixa de rho por exclusao de uma unidade.

Entrada: metricas/root_features_by_image{,_M1,_M2}.csv, A4_profundidade.csv,
         multimodal_long.csv, multimodal_targets.csv, root_harvested.csv
Saida:   metricas/A18_repetibilidade.csv, metricas/A18_insitu_colheita.csv
"""
import os
import sys
import csv
from collections import defaultdict

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

COLETAS_COMUNS = [1, 2, 3, 4, 5, 6]
B_BOOT = 5000
SEMENTE = 42


def fnum(v):
    """
    Purpose:
        Convert a CSV field to float, returning None for empty or non-numeric values.
    Parameters:
        x: value read from a CSV field
    Returns:
        float or None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def ler_matriz(arquivo, coluna, col_coleta="coleta", col_riz="rizotron"):
    """Retorna {rizotron: {coleta: valor}} restrito a C1-C6."""
    m = defaultdict(dict)
    for r in csv.DictReader(open(arquivo, encoding="utf-8")):
        if r[col_coleta] == "":
            continue
        c = int(float(r[col_coleta]))
        if c not in COLETAS_COMUNS:
            continue
        v = fnum(r[coluna])
        if v is not None:
            m[r[col_riz]][c] = v
    return {k: v for k, v in m.items() if len(v) == len(COLETAS_COMUNS)}


def icc31(X):
    """ICC(3,1) consistencia: linhas = unidades, colunas = coletas (efeito fixo)."""
    n, k = X.shape
    gm = X.mean()
    ms_r = k * ((X.mean(axis=1) - gm) ** 2).sum() / (n - 1)
    ms_c = n * ((X.mean(axis=0) - gm) ** 2).sum() / (k - 1)
    ss_e = ((X - X.mean(axis=1, keepdims=True) - X.mean(axis=0, keepdims=True) + gm) ** 2).sum()
    ms_e = ss_e / ((n - 1) * (k - 1))
    return (ms_r - ms_e) / (ms_r + (k - 1) * ms_e)


def rho_consecutivas(X):
    """
    Purpose:
        Spearman correlations between consecutive collections.
    Parameters:
        X: rhizotron x collection matrix
    Returns:
        list of float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return [spearmanr(X[:, j], X[:, j + 1]).statistic for j in range(X.shape[1] - 1)]


def boot_ic(X, estat, rng):
    """
    Purpose:
        Percentile bootstrap interval over rhizotrons for a statistic.
    Parameters:
        X: matrix
        estat: statistic function
        rng: numpy Generator
    Returns:
        tuple (low, high) or (None, None)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    vals = []
    n = X.shape[0]
    for _ in range(B_BOOT):
        sel = rng.choice(n, size=n, replace=True)
        Xb = X[sel]
        if len(np.unique(sel)) < 4:
            continue
        v = estat(Xb)
        if v is not None and not np.isnan(v):
            vals.append(v)
    if len(vals) < 100:
        return None, None
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def bloco1():
    """
    Purpose:
        Compute between-collection consistency of descriptors.
    Parameters:
        none
    Returns:
        list of rows
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    fontes = [
        ("M3", "O", C.METRICAS / "root_features_by_image.csv", "O_ocupacao"),
        ("M3", "L_skel", C.METRICAS / "root_features_by_image.csv", "L_skel_px"),
        ("M3", "N_br", C.METRICAS / "root_features_by_image.csv", "N_br"),
        ("M3", "D50", C.METRICAS / "A4_profundidade.csv", "D50"),
        ("M1", "O", C.METRICAS / "root_features_by_image_M1.csv", "O_ocupacao"),
        ("M2", "O", C.METRICAS / "root_features_by_image_M2.csv", "O_ocupacao"),
    ]
    out = []
    for seg, nome, arq, col in fontes:
        m = ler_matriz(arq, col)
        rizs = sorted(m)
        X = np.array([[m[r][c] for c in COLETAS_COMUNS] for r in rizs])
        rhos = rho_consecutivas(X)
        rng = np.random.default_rng(SEMENTE)
        lo_r, hi_r = boot_ic(X, lambda Xb: float(np.median(rho_consecutivas(Xb))), rng)
        rng = np.random.default_rng(SEMENTE)
        lo_i, hi_i = boot_ic(X, icc31, rng)
        out.append({
            "segmentador": seg, "descritor": nome, "n_rizotrons": len(rizs),
            "coletas": "C1-C6",
            "rho_consecutivas": ";".join("%+.2f" % r for r in rhos),
            "rho_mediana": round(float(np.median(rhos)), 3),
            "rho_min": round(float(min(rhos)), 3), "rho_max": round(float(max(rhos)), 3),
            "rho_mediana_IC_lo": round(lo_r, 3), "rho_mediana_IC_hi": round(hi_r, 3),
            "ICC31": round(float(icc31(X)), 3),
            "ICC31_IC_lo": round(lo_i, 3), "ICC31_IC_hi": round(hi_i, 3), "B": B_BOOT,
        })
    return out


def bloco2():
    """
    Purpose:
        Compute in situ and mass correspondence with harvested length.
    Parameters:
        none
    Returns:
        list of rows
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    ser_O = ler_matriz(C.METRICAS / "multimodal_long.csv", "O_ocupacao")
    ser_L = ler_matriz(C.METRICAS / "multimodal_long.csv", "L_skel_px")
    dap = {}
    for r in csv.DictReader(open(C.METRICAS / "multimodal_long.csv", encoding="utf-8")):
        if r["coleta"] != "":
            dap[int(r["coleta"])] = fnum(r["DAP"])
    alvo = {r["rizotron"]: fnum(r["M_r"])
            for r in csv.DictReader(open(C.METRICAS / "multimodal_targets.csv", encoding="utf-8"))}
    colh = {r["rizotron"]: (fnum(r["L_r_skel_cm"]), r["escala_flag"])
            for r in csv.DictReader(open(C.METRICAS / "root_harvested.csv", encoding="utf-8"))}

    rizs = sorted(r for r in colh if colh[r][1] == "ok" and colh[r][0] is not None)

    def auc(s):
        cs = sorted(s)
        return sum((s[a] + s[b]) / 2.0 * (dap[b] - dap[a]) for a, b in zip(cs[:-1], cs[1:]))

    xs = {
        "L_skel_C6_px": {r: ser_L[r][6] for r in rizs},
        "O_C6": {r: ser_O[r][6] for r in rizs},
        "AUC_O_C1C6": {r: auc(ser_O[r]) for r in rizs},
        "M_R_g": {r: alvo[r] for r in rizs},
    }
    out = []
    for nome, val in xs.items():
        x = np.array([colh[r][0] for r in rizs])
        y = np.array([val[r] for r in rizs])
        sp = spearmanr(x, y)
        X = np.column_stack([x, y])
        rng = np.random.default_rng(SEMENTE)
        lo, hi = boot_ic(X, lambda Xb: spearmanr(Xb[:, 0], Xb[:, 1]).statistic, rng)
        loo = [spearmanr(np.delete(x, i), np.delete(y, i)).statistic for i in range(len(rizs))]
        out.append({
            "x": "L_colhida_cm", "y": nome, "n": len(rizs), "unidade": "rizotron",
            "rizotrons": ";".join(rizs),
            "rho": round(float(sp.statistic), 3), "p": round(float(sp.pvalue), 4),
            "IC_lo": round(lo, 3), "IC_hi": round(hi, 3),
            "LOO_rho_min": round(float(min(loo)), 3), "LOO_rho_max": round(float(max(loo)), 3),
            "B": B_BOOT,
        })
    return out


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
    b1 = bloco1()
    print("=" * 100)
    print("A18 — BLOCO 1: REPETIBILIDADE ENTRE COLETAS (C1-C6, n=12 rizotrons)")
    print("=" * 100)
    print("%-4s %-7s %-32s %8s %18s %8s %18s" % ("seg", "descr", "rho C_k x C_k+1", "mediana", "IC95%", "ICC(3,1)", "IC95%"))
    for l in b1:
        print("%-4s %-7s %-32s %+8.2f   [%+.2f; %+.2f] %8.2f   [%+.2f; %+.2f]"
              % (l["segmentador"], l["descritor"], l["rho_consecutivas"], l["rho_mediana"],
                 l["rho_mediana_IC_lo"], l["rho_mediana_IC_hi"], l["ICC31"],
                 l["ICC31_IC_lo"], l["ICC31_IC_hi"]))
    with open(C.METRICAS / "A18_repetibilidade.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(b1[0].keys()))
        w.writeheader()
        w.writerows(b1)

    b2 = bloco2()
    print()
    print("=" * 100)
    print("A18 — BLOCO 2: RAIZ COLHIDA (cm) x IN SITU (n=%d rizotrons com escala aceita)" % b2[0]["n"])
    print("=" * 100)
    print("%-16s %5s %8s %8s %18s %20s" % ("y", "n", "rho", "p", "IC95%", "LOO rho [min;max]"))
    for l in b2:
        print("%-16s %5d %+8.3f %8.4f   [%+.2f; %+.2f]   [%+.2f; %+.2f]"
              % (l["y"], l["n"], l["rho"], l["p"], l["IC_lo"], l["IC_hi"],
                 l["LOO_rho_min"], l["LOO_rho_max"]))
    with open(C.METRICAS / "A18_insitu_colheita.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(b2[0].keys()))
        w.writeheader()
        w.writerows(b2)
    print("\n-> metricas/A18_repetibilidade.csv, metricas/A18_insitu_colheita.csv")


if __name__ == "__main__":
    main()
