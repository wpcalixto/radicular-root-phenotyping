#!/usr/bin/env python3
"""
Title:
    Temporal analysis
File type:
    Script
Purpose:
    Computes, per rhizotron and variable, rates between collections, relative changes, area under
    the curve and regression slopes against DAP, and tests treatment differences.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-13
Date:
    2026-07-13
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
    - metricas/multimodal_long.csv
Outputs:
    - metricas/temporal_by_rhizotron.csv
    - metricas/temporal_by_treatment.csv
    - metricas/temporal_rates.csv
    - metricas/temporal_treatment_stats.csv
Dependencies:
    - numpy
    - scipy
    - local: config
Execution:
    python scripts/12_temporal.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 12 — Análise temporal da fenotipagem radicular (e elétrica).

Por rizotron i e variável x, ao longo das coletas k (ordenadas por DAP):
  G_{i,k} = (x_k - x_{k-1})/(DAP_k - DAP_{k-1})          taxa entre coletas
  Δ_{i,k} = (x_k - x_{k-1})/(x_{k-1}+ε)                  variação relativa
  AUC_i   = Σ (x_k + x_{k-1})/2 · (DAP_k - DAP_{k-1})     área sob a curva (trapézios)
  β_i     = inclinação da regressão linear x ~ DAP
  G_max, k*                                              incremento máximo e a coleta dele
Por tratamento j e coleta k: média x̄_{j,k} e erro-padrão SE = s/√n.

Estatística por tratamento SEM pseudo-replicação: usa UM valor por rizotron (AUC e β),
n=3 por tratamento → Kruskal-Wallis entre os 4 tratamentos.

Entrada: metricas/multimodal_long.csv
Saídas:
  metricas/temporal_by_rhizotron.csv     (rizotron × variável: AUC, β, G_max, k*, G_médio)
  metricas/temporal_rates.csv            (rizotron × variável × intervalo: G, Δ)
  metricas/temporal_by_treatment.csv     (tratamento × coleta × variável: média, SE, n)
  metricas/temporal_treatment_stats.csv  (Kruskal-Wallis por variável em AUC e β)
"""
import os
import sys
import csv
import statistics as st
from collections import defaultdict

import numpy as np
from scipy.stats import kruskal
from scipy.integrate import trapezoid

RNG = np.random.default_rng(42)


def perm_p_kruskal(gs, n_perm=20000):
    """p por permutação: embaralha os rótulos de tratamento entre os 12 valores de
    rizotron e recomputa H (aproximação de Monte Carlo do teste exato, n=3/grupo)."""
    sizes = [len(g) for g in gs]
    pool = np.concatenate([np.asarray(g, float) for g in gs])
    H0, _ = kruskal(*gs)
    cnt = 1
    for _ in range(n_perm):
        p = RNG.permutation(pool)
        idx = 0; parts = []
        for s in sizes:
            parts.append(p[idx:idx + s]); idx += s
        Hp, _ = kruskal(*parts)
        if Hp >= H0 - 1e-9:
            cnt += 1
    return cnt / (n_perm + 1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

LONG = C.METRICAS / "multimodal_long.csv"
VARS = ["L_skel_px", "A_px", "O_ocupacao", "N_br", "sigma_a", "rho_a"]
EPS = 1e-9


def fnum(x):
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
        return float(x)
    except (TypeError, ValueError):
        return None


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
    rows = list(csv.DictReader(open(LONG, encoding="utf-8")))
    # série por rizotron: lista de (DAP, coleta, {var:val}).
    # AUC/inclinação/taxas usam SÓ a janela comum C1-C6 (R1/R12 não têm C7; a elétrica
    # também termina em C6) -> evita janela temporal desigual entre rizotrons.
    porriz = defaultdict(list)
    trat = {}
    for r in rows:
        dap = fnum(r["DAP"])
        if dap is None or r["coleta"] == "" or int(r["coleta"]) > 6:
            continue
        porriz[r["rizotron"]].append((dap, r["coleta"], {v: fnum(r.get(v)) for v in VARS}))
        trat[r["rizotron"]] = r["tratamento"]
    for riz in porriz:
        porriz[riz].sort(key=lambda t: t[0])

    by_riz, rates = [], []
    auc_val = defaultdict(dict)   # var -> riz -> AUC
    beta_val = defaultdict(dict)  # var -> riz -> beta
    for riz, serie in porriz.items():
        for v in VARS:
            pts = [(d, s[v]) for d, k, s in serie if s[v] is not None]
            if len(pts) < 2:
                continue
            D = np.array([p[0] for p in pts], float)
            X = np.array([p[1] for p in pts], float)
            auc = float(trapezoid(X, D))
            beta = float(np.polyfit(D, X, 1)[0])
            Gs = []
            for j in range(1, len(pts)):
                dd = D[j] - D[j - 1]
                G = (X[j] - X[j - 1]) / dd if dd else 0
                delta = (X[j] - X[j - 1]) / (X[j - 1] + EPS)
                Gs.append((G, D[j]))
                rates.append({"rizotron": riz, "tratamento": trat[riz], "variavel": v,
                              "DAP_ini": D[j - 1], "DAP_fim": D[j],
                              "G_taxa": round(G, 5), "delta_rel": round(delta, 5)})
            Gmax, kstar = max(Gs, key=lambda t: t[0])
            by_riz.append({"rizotron": riz, "tratamento": trat[riz], "variavel": v,
                           "AUC": round(auc, 3), "beta_slope": round(beta, 5),
                           "G_max": round(Gmax, 5), "k_star_DAP": int(kstar),
                           "G_medio": round(st.mean(g for g, _ in Gs), 5), "n_pontos": len(pts)})
            auc_val[v][riz] = auc
            beta_val[v][riz] = beta

    with open(C.METRICAS / "temporal_by_rhizotron.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(by_riz[0].keys())); w.writeheader(); w.writerows(by_riz)
    with open(C.METRICAS / "temporal_rates.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rates[0].keys())); w.writeheader(); w.writerows(rates)

    # por tratamento × coleta: média e SE
    grp = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # var->trat->coleta->[vals]
    dapof = {}
    for r in rows:
        dap = fnum(r["DAP"])
        for v in VARS:
            val = fnum(r.get(v))
            if val is not None and r["coleta"] != "":
                grp[v][r["tratamento"]][r["coleta"]].append(val)
                dapof[r["coleta"]] = dap
    trat_rows = []
    for v in VARS:
        for t in ["REF", "T1", "T2", "T3"]:
            for ck in sorted(grp[v][t], key=lambda x: int(x)):
                vals = grp[v][t][ck]
                sd = st.pstdev(vals) if len(vals) > 1 else 0
                trat_rows.append({"variavel": v, "tratamento": t, "coleta": ck,
                                  "DAP": int(dapof[ck]), "n": len(vals),
                                  "media": round(st.mean(vals), 5),
                                  "SE": round(sd / (len(vals) ** 0.5), 5) if vals else 0})
    with open(C.METRICAS / "temporal_by_treatment.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(trat_rows[0].keys())); w.writeheader(); w.writerows(trat_rows)

    # Kruskal-Wallis por variável (1 valor/rizotron = AUC e β; n=3/tratamento) — sem pseudo-repl.
    stat_rows = []
    for v in VARS:
        for metrica, dic in (("AUC", auc_val[v]), ("beta_slope", beta_val[v])):
            grupos = defaultdict(list)
            for riz, val in dic.items():
                grupos[trat[riz]].append(val)
            gs = [grupos[t] for t in ["REF", "T1", "T2", "T3"] if len(grupos[t]) >= 1]
            if len(gs) == 4 and all(len(g) >= 2 for g in gs):
                H, p = kruskal(*gs)
                p_perm = perm_p_kruskal(gs)
                n_tot = sum(len(g) for g in gs)
                eps2 = H / (n_tot - 1)          # ε² de Kruskal-Wallis (tamanho de efeito)
                stat_rows.append({"variavel": v, "metrica_por_rizotron": metrica,
                                  "H": round(H, 3), "epsilon2": round(eps2, 3),
                                  "p": round(p, 4), "p_perm": round(p_perm, 4),
                                  "n_por_grupo": "/".join(str(len(g)) for g in gs)})
    with open(C.METRICAS / "temporal_treatment_stats.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stat_rows[0].keys())); w.writeheader(); w.writerows(stat_rows)

    print(f"[Fase 12] {len(by_riz)} (rizotron×variável) -> temporal_by_rhizotron.csv")
    print(f"   taxas: {len(rates)} intervalos -> temporal_rates.csv")
    print(f"   por tratamento×coleta -> temporal_by_treatment.csv")
    print(f"   Kruskal-Wallis (AUC/β por rizotron, n=3/trat) -> temporal_treatment_stats.csv:")
    for s in stat_rows:
        sig = "*" if s["p"] < 0.05 else ""
        print(f"     {s['variavel']:11s} {s['metrica_por_rizotron']:10s} H={s['H']:.2f} "
              f"p={s['p']:.3f} p_perm={s['p_perm']:.3f}{sig}")


if __name__ == "__main__":
    main()
