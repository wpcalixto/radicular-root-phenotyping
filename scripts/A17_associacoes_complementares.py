#!/usr/bin/env python3
"""
Title:
    Complementary associations
File type:
    Script
Purpose:
    Tests in situ occupancy versus final root mass and conditioning cost versus intervention
    complexity with Spearman correlations and bootstrap intervals.
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
    - metricas/A6_custo.csv
    - metricas/multimodal_long.csv
    - metricas/multimodal_targets.csv
Outputs:
    - metricas/A17_associacoes.csv
Dependencies:
    - numpy
    - scipy
    - local: config
Execution:
    python scripts/A17_associacoes_complementares.py (from a workspace prepared with
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
A17 — Duas associações complementares previstas na Metodologia e ainda sem resultado.

Bloco 1 — Observação in situ x massa radicular final (unidade = rizotron, n=12):
  1a. O na última coleta comum (C6)      x  M_R
  1b. AUC(O) na janela C1-C6 (trapézios) x  M_R
  Spearman rho, p, IC95% por reamostragem das 12 unidades.

Bloco 2 — Custo do condicionamento x complexidade da intervenção (n=82 imagens, 12 rizotrons):
  2a. t_deflash x numero de nucleos especulares
  2b. t_deflash x fracao reconstruida por imagem
  Spearman rho, IC95% por reamostragem AGRUPADA no rizotron (o p ingenuo ignora o
  agrupamento e e reportado apenas como referencia).

Entrada: metricas/multimodal_long.csv, multimodal_targets.csv, A6_custo.csv
Saida:   metricas/A17_associacoes.csv
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


def ic_boot(pares, rng, agrupado):
    """pares: lista (grupo, x, y). agrupado=True reamostra grupos inteiros."""
    por_grupo = defaultdict(list)
    for g, x, y in pares:
        por_grupo[g].append((x, y))
    grupos = sorted(por_grupo)
    rs = []
    for _ in range(B_BOOT):
        sel = rng.choice(len(grupos), size=len(grupos), replace=True)
        xs, ys = [], []
        for i in sel:
            for x, y in por_grupo[grupos[i]]:
                xs.append(x)
                ys.append(y)
        if len(set(xs)) < 3 or len(set(ys)) < 3:
            continue
        r = spearmanr(xs, ys).statistic
        if not np.isnan(r):
            rs.append(r)
    if len(rs) < 100:
        return None, None
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def bloco1():
    """
    Purpose:
        Compute in situ occupancy versus final root mass associations.
    Parameters:
        none
    Returns:
        list of result rows
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    ser = defaultdict(dict)
    dap = {}
    for r in csv.DictReader(open(C.METRICAS / "multimodal_long.csv", encoding="utf-8")):
        if r["coleta"] == "":
            continue
        c = int(r["coleta"])
        if c not in COLETAS_COMUNS:
            continue
        o = fnum(r["O_ocupacao"])
        if o is not None:
            ser[r["rizotron"]][c] = o
            dap[c] = fnum(r["DAP"])
    alvo = {r["rizotron"]: fnum(r["M_r"])
            for r in csv.DictReader(open(C.METRICAS / "multimodal_targets.csv", encoding="utf-8"))}

    rizs = sorted(r for r in ser if r in alvo and alvo[r] is not None)
    c6, auc = {}, {}
    for r in rizs:
        cs = sorted(ser[r])
        c6[r] = ser[r][cs[-1]]
        a = 0.0
        for k1, k2 in zip(cs[:-1], cs[1:]):
            a += (ser[r][k1] + ser[r][k2]) / 2.0 * (dap[k2] - dap[k1])
        auc[r] = a

    out = []
    for nome, val in (("O_C6", c6), ("AUC_O_C1C6", auc)):
        pares = [(r, val[r], alvo[r]) for r in rizs]
        x = [p[1] for p in pares]
        y = [p[2] for p in pares]
        sp = spearmanr(x, y)
        rng = np.random.default_rng(SEMENTE)
        lo, hi = ic_boot(pares, rng, agrupado=True)
        out.append({"bloco": "1_ocupacao_x_massa", "x": nome, "y": "M_R", "n": len(pares),
                    "unidade": "rizotron", "rho": round(float(sp.statistic), 3),
                    "p": round(float(sp.pvalue), 4),
                    "IC_lo": round(lo, 3), "IC_hi": round(hi, 3), "B": B_BOOT})
    return out


def bloco2():
    """
    Purpose:
        Compute conditioning cost versus intervention complexity associations.
    Parameters:
        none
    Returns:
        list of result rows
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rows = list(csv.DictReader(open(C.METRICAS / "A6_custo.csv", encoding="utf-8")))
    out = []
    for nome, col in (("n_nucleos", "n_nucleos"), ("fracao_reconstruida_pct", "flash_pct")):
        pares = []
        for r in rows:
            t = fnum(r["t_deflash_s"])
            v = fnum(r[col])
            if t is None or v is None:
                continue
            pares.append((r["image_id"].split("_")[0], v, t))
        x = [p[1] for p in pares]
        y = [p[2] for p in pares]
        sp = spearmanr(x, y)
        rng = np.random.default_rng(SEMENTE)
        lo, hi = ic_boot(pares, rng, agrupado=True)
        out.append({"bloco": "2_custo_x_complexidade", "x": nome, "y": "t_deflash_s",
                    "n": len(pares), "unidade": "imagem (cluster=rizotron)",
                    "rho": round(float(sp.statistic), 3),
                    "p": round(float(sp.pvalue), 4),
                    "IC_lo": round(lo, 3), "IC_hi": round(hi, 3), "B": B_BOOT})
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
    linhas = bloco1() + bloco2()
    print("=" * 92)
    print("A17 — ASSOCIACOES COMPLEMENTARES")
    print("=" * 92)
    print("%-24s %-24s %5s %8s %9s %20s" % ("x", "y", "n", "rho", "p", "IC95%"))
    for l in linhas:
        print("%-24s %-24s %5d %+8.3f %9.4f   [%+.2f; %+.2f]"
              % (l["x"], l["y"], l["n"], l["rho"], l["p"], l["IC_lo"], l["IC_hi"]))
    with open(C.METRICAS / "A17_associacoes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print("\n-> metricas/A17_associacoes.csv")


if __name__ == "__main__":
    main()
