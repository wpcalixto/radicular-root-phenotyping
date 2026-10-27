#!/usr/bin/env python3
"""
Title:
    Intervals for optical-electrical association
File type:
    Script
Purpose:
    Computes rhizotron-bootstrap intervals for the trajectory correlations and slopes linking
    apparent conductivity and optical descriptors.
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
    - metricas/electrical_features_by_rhizotron.csv
    - metricas/root_features_by_image.csv
Outputs:
    - metricas/A16_ic_optico_eletrico.csv
Dependencies:
    - numpy
    - scipy
    - local: config
Execution:
    python scripts/A16_ic_optico_eletrico.py (from a workspace prepared with
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
A16 — Intervalos de confiança da associação óptico-elétrica.

Motivação (auditoria 2026-07-30, item 22): a tabela de associação reportava $\\rho$ e
$\\beta$ como estimativas pontuais com valores de $p$, sem intervalo de confiança.

Delineamento: reamostragem bootstrap NO NÍVEL DO RIZOTRON (12 unidades), coerente com o
restante do trabalho. Rizotrons sorteados mais de uma vez entram como unidades distintas.

Estimandos:
  A2.2  rho de Spearman entre as inclinações Theil--Sen de sigma_a e de cada descritor,
        na forma bruta e centrada dentro do tratamento;
  A2.3  beta padronizado do modelo misto que relaciona o desvio de sigma_a em relação à
        média da própria unidade ao desvio do descritor, controlando coleta e tratamento.

Saída: metricas/A16_ic_optico_eletrico.csv
"""
import os
import sys
import csv
import itertools
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

OUT = C.METRICAS / "A16_ic_optico_eletrico.csv"
B = 5000
SEMENTE = 42
COLETAS = [1, 2, 3, 4, 5, 6]
VARS = [("O_ocupacao", "O"), ("L_skel_px", "L_skel"), ("N_br", "N_br")]


def theil_sen(x, y):
    """
    Purpose:
        Compute the Theil-Sen slope (median of pairwise slopes).
    Parameters:
        x: abscissae
        y: ordinates
    Returns:
        float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    s = [(y[j] - y[i]) / (x[j] - x[i]) for i, j in itertools.combinations(range(len(x)), 2)
         if x[j] != x[i]]
    return float(np.median(s)) if s else float("nan")


def carregar():
    """
    Purpose:
        Load DAP, optical and electrical series and treatments per rhizotron.
    Parameters:
        none
    Returns:
        tuple
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    dapc = {i + 1: C.dap(C.parse_data_pasta(d)) for i, d in enumerate(C.COLETAS)}
    opt, trat = defaultdict(dict), {}
    with open(C.METRICAS / "root_features_by_image.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["coleta"] and int(r["coleta"]) in COLETAS:
                trat[r["rizotron"]] = r["tratamento"]
                opt[r["rizotron"]][int(r["coleta"])] = {k: float(r[k]) for k, _ in VARS}
    ele = defaultdict(dict)
    with open(C.METRICAS / "electrical_features_by_rhizotron.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    datas = sorted({r["collection_date"] for r in rows}, key=lambda x: C.parse_data_pasta(x))
    ordem = {d: i + 1 for i, d in enumerate(datas)}
    for r in rows:
        ele[r["rhizotron_id"]][ordem[r["collection_date"]]] = float(r["sigma_a"])
    return dapc, opt, ele, trat


def inclinacoes(rizs, dapc, opt, ele):
    """{riz: (s_sigma, {var: s_var})} pelas coletas comuns disponíveis."""
    out = {}
    for r in rizs:
        cs = [c for c in COLETAS if c in opt.get(r, {}) and c in ele.get(r, {})]
        if len(cs) < 3:
            continue
        x = [dapc[c] for c in cs]
        out[r] = (theil_sen(x, [ele[r][c] for c in cs]),
                  {k: theil_sen(x, [opt[r][c][k] for c in cs]) for k, _ in VARS})
    return out


def rho_bruto_e_intra(unidades, trat):
    """unidades: lista de (riz_id_unico, s_sigma, {var: s_var}, tratamento)."""
    res = {}
    for k, _ in VARS:
        a = np.array([u[1] for u in unidades], float)
        b = np.array([u[2][k] for u in unidades], float)
        ok = np.isfinite(a) & np.isfinite(b)
        a, b = a[ok], b[ok]
        tt = [unidades[i][3] for i in range(len(unidades)) if ok[i]]
        if len(a) < 4:
            res[k] = (np.nan, np.nan); continue
        rho = stats.spearmanr(a, b).correlation
        ac, bc = a.copy(), b.copy()
        for t in set(tt):
            m = [i for i, x in enumerate(tt) if x == t]
            if len(m) > 1:
                ac[m] -= ac[m].mean(); bc[m] -= bc[m].mean()
        rhoc = stats.spearmanr(ac, bc).correlation
        res[k] = (rho, rhoc)
    return res


def beta_intra(unidades_lin):
    """beta padronizado por variável: regressão dos desvios intra-unidade,
    com coleta como fator (dummies) e tratamento absorvido pelo centro da unidade."""
    res = {}
    for k, _ in VARS:
        X, Y, cols = [], [], []
        for (rid, ck, sig, val, _t) in unidades_lin:
            X.append((rid, ck, sig)); Y.append(val[k])
        # desvio em relação à média da própria unidade (dentro do rizotron)
        porU = defaultdict(list)
        for i, (rid, ck, sig) in enumerate(X):
            porU[rid].append(i)
        xs, ys, cks = [], [], []
        for rid, idx in porU.items():
            if len(idx) < 2:
                continue
            ms = np.mean([X[i][2] for i in idx]); my = np.mean([Y[i] for i in idx])
            for i in idx:
                xs.append(X[i][2] - ms); ys.append(Y[i] - my); cks.append(X[i][1])
        if len(xs) < 6:
            res[k] = np.nan; continue
        xs = np.array(xs, float); ys = np.array(ys, float)
        # padroniza ambos -> beta comparável entre descritores
        if xs.std() == 0 or ys.std() == 0:
            res[k] = np.nan; continue
        xz = (xs - xs.mean()) / xs.std(); yz = (ys - ys.mean()) / ys.std()
        # controla coleta por dummies
        cs = sorted(set(cks))
        D = np.column_stack([np.array([1.0 if c == cc else 0.0 for c in cks]) for cc in cs[1:]]) \
            if len(cs) > 1 else np.empty((len(xz), 0))
        M = np.column_stack([np.ones(len(xz)), xz, D]) if D.size else np.column_stack([np.ones(len(xz)), xz])
        try:
            beta = np.linalg.lstsq(M, yz, rcond=None)[0][1]
        except Exception:
            beta = np.nan
        res[k] = float(beta)
    return res


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
    dapc, opt, ele, trat = carregar()
    rizs = sorted(set(opt) & set(ele))
    print(f"[A16] {len(rizs)} rizotrons | B={B} | reamostragem no nível do rizotron")

    incl = inclinacoes(rizs, dapc, opt, ele)
    base_u = [(r, incl[r][0], incl[r][1], trat[r]) for r in sorted(incl)]
    base_lin = [(r, c, ele[r][c], opt[r][c], trat[r])
                for r in rizs for c in COLETAS if c in opt[r] and c in ele[r]]

    ponto_rho = rho_bruto_e_intra(base_u, trat)
    ponto_beta = beta_intra(base_lin)

    idx_u = {r: [u for u in base_u if u[0] == r] for r in rizs}
    idx_l = {r: [l for l in base_lin if l[0] == r] for r in rizs}

    rng = np.random.default_rng(SEMENTE)
    dist = defaultdict(list)
    for _ in range(B):
        esc = rng.choice(len(rizs), size=len(rizs), replace=True)
        u, lin = [], []
        for j, e in enumerate(esc):
            r = rizs[e]
            for x in idx_u[r]:
                u.append((f"{r}#{j}", x[1], x[2], x[3]))
            for x in idx_l[r]:
                lin.append((f"{r}#{j}", x[1], x[2], x[3], x[4]))
        rr = rho_bruto_e_intra(u, trat)
        bb = beta_intra(lin)
        for k, _ in VARS:
            if np.isfinite(rr[k][0]): dist[("rho", k)].append(rr[k][0])
            if np.isfinite(rr[k][1]): dist[("rho_intra", k)].append(rr[k][1])
            if np.isfinite(bb[k]):    dist[("beta", k)].append(bb[k])

    linhas = []
    print("\n  %-10s %-12s %8s   %s" % ("estimando", "descritor", "ponto", "IC95%"))
    for est, rot in (("rho", "rho_bruto"), ("rho_intra", "rho_intra_trat"), ("beta", "beta_intra")):
        for k, nome in VARS:
            v = ponto_rho[k][0] if est == "rho" else (ponto_rho[k][1] if est == "rho_intra" else ponto_beta[k])
            d = np.array(dist[(est, k)])
            lo, hi = (np.percentile(d, 2.5), np.percentile(d, 97.5)) if len(d) > 10 else (np.nan, np.nan)
            print("  %-10s %-12s %+8.3f   [%+.3f, %+.3f]" % (rot, nome, v, lo, hi))
            linhas.append({"estimando": rot, "descritor": nome, "ponto": round(float(v), 3),
                           "IC95_lo": round(float(lo), 3), "IC95_hi": round(float(hi), 3),
                           "B": B, "unidade_reamostragem": "rizotron", "n": len(rizs)})

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader(); w.writerows(linhas)
    print(f"\n[A16] {OUT.name} gravado.")


if __name__ == "__main__":
    main()
