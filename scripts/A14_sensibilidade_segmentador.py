#!/usr/bin/env python3
"""
Title:
    Sensitivity to the segmenter
File type:
    Script
Purpose:
    Extracts the same descriptors from M1, M2 and M3 and repeats the temporal and treatment analyses
    to separate root properties from mask properties.
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
    - metricas/multimodal_targets.csv
Outputs:
    - metricas/A14_sensibilidade_segmentador.csv
Dependencies:
    - numpy
    - scipy
    - sklearn
    - local: config
Execution:
    python scripts/A14_sensibilidade_segmentador.py (from a workspace prepared with
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
A14 — Sensibilidade dos achados biológicos e temporais à escolha do segmentador.

Motivação (auditoria 2026-07-30, item 15): os descritores morfológicos foram extraídos
apenas de M3. Sem reproduzir os achados sobre M1 e M2, não é possível separar o que é
propriedade do sistema radicular do que é propriedade da máscara combinada selecionada.

Delineamento: os mesmos descritores (Fase 09) são extraídos das máscaras dos três
métodos e as análises-chave são refeitas sobre cada conjunto, mantendo idênticos o
tratamento da região reconstruída, a janela temporal (C1--C6), a unidade experimental
(rizotron) e os procedimentos estatísticos.

Análises reproduzidas:
  1. Descritores por tratamento (rizotron-first, média das seis coletas comuns);
  2. Distribuição vertical (D50, D90, F_prof) e densidade estrutural (B_d);
  3. Efeito de tratamento na dinâmica temporal (Kruskal--Wallis sobre AUC e inclinação,
     com permutação de Monte Carlo);
  4. Concordância direcional das trajetórias óptico-elétricas (Theil--Sen por rizotron,
     Spearman entre inclinações, bruto e centrado dentro do tratamento);
  5. Predição LORO dos desfechos finais (Ridge, configurações óptica / elétrica / fusão).

Saída: metricas/A14_sensibilidade_segmentador.csv (+ relatório no stdout)
"""
import os
import sys
import csv
import math
import itertools
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

METODOS = ["M3", "M1", "M2"]
SUF = {"M3": "", "M1": "_M1", "M2": "_M2"}
OUT = C.METRICAS / "A14_sensibilidade_segmentador.csv"
COLETAS_COMUNS = [1, 2, 3, 4, 5, 6]      # janela comum a todas as unidades
B_PERM = 20000
SEMENTE = 42
Z_PROF = 0.60


# ----------------------------------------------------------------------
def carregar(met):
    """{rizotron: {coleta: {descritor: valor}}} + tratamento por rizotron."""
    d = defaultdict(dict)
    trat = {}
    with open(C.METRICAS / f"root_features_by_image{SUF[met]}.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r["coleta"]:
                continue
            ck = int(r["coleta"])
            if ck not in COLETAS_COMUNS:
                continue
            riz = r["rizotron"]
            trat[riz] = r["tratamento"]
            d[riz][ck] = {k: float(r[k]) for k in
                          ("A_px", "O_ocupacao", "L_skel_px", "N_br") if r.get(k) not in ("", None)}
    return d, trat


def eletrica():
    """{rizotron: {coleta: sigma_a}} — independe do segmentador."""
    d = defaultdict(dict)
    ordem = {}
    with open(C.METRICAS / "electrical_features_by_rhizotron.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    datas = sorted({r["collection_date"] for r in rows}, key=lambda x: C.parse_data_pasta(x))
    for i, dt in enumerate(datas, 1):
        ordem[dt] = i
    for r in rows:
        d[r["rhizotron_id"]][ordem[r["collection_date"]]] = float(r["sigma_a"])
    return d


def dap_por_coleta():
    """
    Purpose:
        Map collection index to DAP.
    Parameters:
        none
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return {i + 1: C.dap(C.parse_data_pasta(dt)) for i, dt in enumerate(C.COLETAS)}


# ----------------------------------------------------------------------
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
    n = len(x)
    if n < 2:
        return float("nan")
    s = [(y[j] - y[i]) / (x[j] - x[i]) for i, j in itertools.combinations(range(n), 2)
         if x[j] != x[i]]
    return float(np.median(s)) if s else float("nan")


def auc_trapz(x, y):
    """
    Purpose:
        Area under a curve by the trapezoidal rule after sorting by x.
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
    o = np.argsort(x)
    return float(np.trapz(np.array(y)[o], np.array(x)[o]))


def kruskal_perm(grupos, rng):
    """
    Purpose:
        Kruskal-Wallis statistic with a permutation p-value.
    Parameters:
        grupos: lists of values
        rng: numpy Generator
    Returns:
        tuple (H, p)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    vals = [v for g in grupos for v in g]
    tam = [len(g) for g in grupos]
    H = stats.kruskal(*grupos).statistic
    n = len(vals)
    cnt = 0
    arr = np.array(vals)
    for _ in range(B_PERM):
        rng.shuffle(arr)
        ini, gs = 0, []
        for t in tam:
            gs.append(arr[ini:ini + t]); ini += t
        if stats.kruskal(*gs).statistic >= H - 1e-12:
            cnt += 1
    eps2 = H / (n - 1)
    return H, eps2, (cnt + 1) / (B_PERM + 1)


def ridge_loro(X, y, riz):
    """LORO com padronização dentro do treino; Ridge(alpha=10) como no artigo."""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    us = sorted(set(riz))
    err = []
    for u in us:
        tr = [i for i, r in enumerate(riz) if r != u]
        te = [i for i, r in enumerate(riz) if r == u]
        sc = StandardScaler().fit(X[tr])
        m = Ridge(alpha=10).fit(sc.transform(X[tr]), y[tr])
        err.append(abs(float(m.predict(sc.transform(X[te]))[0]) - float(y[te][0])))
    return float(np.mean(err))


# ----------------------------------------------------------------------
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
    dapc = dap_por_coleta()
    ele = eletrica()
    bio = {}
    with open(C.METRICAS / "multimodal_targets.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            bio[r["rizotron"]] = (float(r["M_r"]), float(r["M_a"]))

    linhas = []
    def add(**kw):
        linhas.append(kw)

    print("=" * 76)
    print("A14 — SENSIBILIDADE À ESCOLHA DO SEGMENTADOR")
    print("=" * 76)

    for met in METODOS:
        d, trat = carregar(met)
        rizs = sorted(d)
        rng = np.random.default_rng(SEMENTE)
        print(f"\n{'#' * 24} {met} {'#' * 24}")

        # ---------- 1. descritores por tratamento (rizotron-first) ----------
        print("\n  [1] Descritores por tratamento (média ± dp entre rizotrons)")
        porT = defaultdict(list)
        for r in rizs:
            cs = [c for c in COLETAS_COMUNS if c in d[r]]
            porT[trat[r]].append({k: float(np.mean([d[r][c][k] for c in cs]))
                                  for k in ("A_px", "O_ocupacao", "L_skel_px", "N_br")})
        print("      %-5s %10s %10s %10s %10s" % ("Trat", "A(kpx)", "L(kpx)", "O(%)", "N_br"))
        for t in ("REF", "T1", "T2", "T3"):
            if t not in porT:
                continue
            v = porT[t]
            f = lambda k, s=1: (np.mean([x[k] for x in v]) * s, np.std([x[k] for x in v], ddof=1) * s)
            a, la, o, nb = f("A_px", 1e-3), f("L_skel_px", 1e-3), f("O_ocupacao", 100), f("N_br")
            print("      %-5s %5.1f±%-4.1f %5.1f±%-4.1f %5.2f±%-4.2f %5.0f±%-4.0f"
                  % (t, a[0], a[1], la[0], la[1], o[0], o[1], nb[0], nb[1]))
            add(metodo=met, analise="descritores_por_tratamento", grupo=t,
                A_kpx=round(a[0], 1), L_kpx=round(la[0], 1),
                O_pct=round(o[0], 2), N_br=round(nb[0], 0))

        # ---------- 2/3. dinâmica temporal ----------
        print("\n  [2] Efeito de tratamento na dinâmica (Kruskal, %d permutações)" % B_PERM)
        for var in ("O_ocupacao", "L_skel_px", "N_br"):
            for resumo in ("AUC", "beta"):
                porG = defaultdict(list)
                for r in rizs:
                    cs = [c for c in COLETAS_COMUNS if c in d[r]]
                    x = [dapc[c] for c in cs]; y = [d[r][c][var] for c in cs]
                    porG[trat[r]].append(auc_trapz(x, y) if resumo == "AUC" else theil_sen(x, y))
                gs = [porG[t] for t in ("REF", "T1", "T2", "T3") if t in porG]
                H, e2, pp = kruskal_perm(gs, rng)
                print("      %-12s %-5s H=%5.2f eps2=%.2f p_perm=%.4f" % (var, resumo, H, e2, pp))
                add(metodo=met, analise="temporal_kruskal", variavel=var, resumo=resumo,
                    H=round(H, 3), epsilon2=round(e2, 3), p_perm=round(pp, 4))

        # ---------- 4. associação óptico-elétrica (A2.2) ----------
        print("\n  [3] Trajetórias óptico-elétricas (Theil--Sen + Spearman)")
        s_sig, s_var, tt = {}, defaultdict(dict), {}
        for r in rizs:
            cs = [c for c in COLETAS_COMUNS if c in d[r] and c in ele.get(r, {})]
            if len(cs) < 3:
                continue
            x = [dapc[c] for c in cs]
            s_sig[r] = theil_sen(x, [ele[r][c] for c in cs])
            for var in ("O_ocupacao", "L_skel_px", "N_br"):
                s_var[var][r] = theil_sen(x, [d[r][c][var] for c in cs])
            tt[r] = trat[r]
        for var in ("O_ocupacao", "L_skel_px", "N_br"):
            com = [r for r in s_sig if r in s_var[var]]
            a = np.array([s_sig[r] for r in com]); b = np.array([s_var[var][r] for r in com])
            rho = stats.spearmanr(a, b).correlation
            # centrado dentro do tratamento
            ac, bc = a.copy(), b.copy()
            for t in set(tt[r] for r in com):
                m = [i for i, r in enumerate(com) if tt[r] == t]
                ac[m] -= ac[m].mean(); bc[m] -= bc[m].mean()
            rho_c = stats.spearmanr(ac, bc).correlation
            print("      %-12s rho_bruto=%+.2f  rho_intra-trat=%+.2f  (n=%d)"
                  % (var, rho, rho_c, len(com)))
            add(metodo=met, analise="A2_trajetorias", variavel=var, n=len(com),
                rho_bruto=round(float(rho), 3), rho_intra_trat=round(float(rho_c), 3))

        # ---------- 5. predição LORO ----------
        print("\n  [4] Predição LORO da massa seca ao ar (Ridge, MAE em g)")
        rz = [r for r in rizs if r in bio]
        dapv = [dapc[c] for c in COLETAS_COMUNS]
        def feats(fonte):
            X = []
            for r in rz:
                cs = [c for c in COLETAS_COMUNS if c in d[r]]
                x = [dapc[c] for c in cs]
                v = []
                if fonte in ("optica", "fusao"):
                    for var in ("O_ocupacao", "L_skel_px", "N_br"):
                        s = [d[r][c][var] for c in cs]
                        v += [float(np.mean(s)), theil_sen(x, s)]
                if fonte in ("eletrica", "fusao"):
                    ce = [c for c in COLETAS_COMUNS if c in ele.get(r, {})]
                    s = [ele[r][c] for c in ce]
                    v += [float(np.mean(s)), theil_sen([dapc[c] for c in ce], s)]
                X.append(v)
            return np.array(X)
        for alvo, idx, rot in ((0, 0, "M_R"), (1, 1, "M_PA")):
            y = np.array([bio[r][idx] for r in rz])
            ref = float(np.mean([abs(y[i] - np.mean(np.delete(y, i))) for i in range(len(y))]))
            out = {"referencia": ref}
            for fonte in ("optica", "eletrica", "fusao"):
                out[fonte] = ridge_loro(feats(fonte), y, rz)
            print("      %-5s ref=%5.2f | óptica=%5.2f | elétrica=%5.2f | fusão=%5.2f"
                  % (rot, out["referencia"], out["optica"], out["eletrica"], out["fusao"]))
            add(metodo=met, analise="LORO_MAE", alvo=rot,
                **{k: round(v, 3) for k, v in out.items()})

    campos = sorted({k for l in linhas for k in l})
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print(f"\n[A14] {OUT.name} gravado ({len(linhas)} linhas).")


if __name__ == "__main__":
    main()
