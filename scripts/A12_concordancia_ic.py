#!/usr/bin/env python3
"""
Title:
    Agreement coefficients with intervals
File type:
    Script
Purpose:
    Computes Fleiss kappa, Krippendorff ordinal alpha, ICC(2,1) and ICC(3,1) with rhizotron-level
    bootstrap confidence intervals.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-30
Date:
    2026-07-30
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
    - metricas/review_key.csv
Outputs:
    - metricas/A12_concordancia_ic.csv
Dependencies:
    - numpy
    - local: config
Execution:
    python scripts/A12_concordancia_ic.py (from a workspace prepared with
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
A12 — Intervalos de confiança dos coeficientes de concordância entre avaliadores.

Motivação (auditoria 2026-07-30, item 16): os coeficientes de concordância (kappa de
Fleiss, alfa de Krippendorff ordinal e ICC) eram reportados como estimativas pontuais,
sem intervalo, sem o tipo exato de ICC e sem declaração da unidade de concordância e do
tratamento de dados ausentes.

Delineamento: reamostragem bootstrap NO NÍVEL DO RIZOTRON (12 unidades), que é a unidade
experimental. Reamostrar julgamentos ou imagens trataria observações dependentes como
independentes e produziria intervalos artificialmente estreitos — o mesmo erro que a
auditoria aponta em Cochran/McNemar. Rizotrons sorteados mais de uma vez entram como
unidades DISTINTAS (a matriz é indexada por posição, não por identificador), preservando
a variância correta da reamostragem com reposição.

Unidade de concordância: um alvo é a combinação imagem x método; os juízes são os nove
avaliadores. Desenho completamente cruzado (todos julgaram todos os alvos).

Coeficientes:
  - kappa de Fleiss (nominal, escala 0–4) e para a decisão binária de aceitação;
  - alfa de Krippendorff com métrica de discrepância ORDINAL;
  - ICC(2,1) concordância absoluta e ICC(3,1) consistência, duas vias, avaliador único.

Saída: metricas/A12_concordancia_ic.csv
"""
import os
import sys
import csv
import importlib.util
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

_spec = importlib.util.spec_from_file_location("sel08d", C.SCRIPTS / "08D_selecao.py")
sel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sel)

OUT = C.METRICAS / "A12_concordancia_ic.csv"
KEY = C.METRICAS / "review_key.csv"
B = 5000
SEMENTE = 42
MAPA_METODO = {"Frangi": "M1", "Ext": "M2", "Comb": "M3"}
K_CAT = 5           # notas 0..4


# ----------------------------------------------------------------------
def carregar_matrizes():
    """Q[alvo, avaliador] e A[alvo, avaliador] (NaN = ausente), + rizotron de cada alvo."""
    gab = {}
    with open(KEY, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            gab[(r["image_id"], r["codigo"])] = MAPA_METODO.get(r["metodo_real"],
                                                                r["metodo_real"])
    reg = defaultdict(dict)
    avals = set()
    for r in sel.carregar():
        img = str(r.get("image_id", "")).strip()
        cod = str(r.get("codigo", "")).strip()
        met = gab.get((img, cod))
        if met is None or r.get("_Q") is None:
            continue
        a = r["avaliador"]
        avals.add(a)
        reg[(img, met)][a] = (int(r["_Q"]), 1 if sel.marcado(r.get("aceita")) else 0)

    avals = sorted(avals)
    alvos = sorted(reg)
    Q = np.full((len(alvos), len(avals)), np.nan)
    A = np.full((len(alvos), len(avals)), np.nan)
    for i, alvo in enumerate(alvos):
        for j, a in enumerate(avals):
            if a in reg[alvo]:
                Q[i, j], A[i, j] = reg[alvo][a]
    riz = np.array([alvo[0].split("_")[0] for alvo in alvos])
    return Q, A, riz, avals, alvos


# ----------------------------------------------------------------------
def contagens(M, k):
    """M[alvo, juiz] -> C[alvo, categoria] (ignora NaN)."""
    Cc = np.zeros((M.shape[0], k))
    for c in range(k):
        Cc[:, c] = (M == c).sum(axis=1)
    return Cc


def fleiss(M, k):
    """
    Purpose:
        Fleiss kappa for a ratings matrix.
    Parameters:
        M: items x raters matrix
        k: number of categories
    Returns:
        float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    Cc = contagens(M, k)
    n_i = Cc.sum(axis=1)
    ok = n_i >= 2
    Cc, n_i = Cc[ok], n_i[ok]
    if len(n_i) == 0:
        return np.nan
    total = n_i.sum()
    p_j = Cc.sum(axis=0) / total
    Pe = float((p_j ** 2).sum())
    Pbar = float((((Cc ** 2).sum(axis=1) - n_i) / (n_i * (n_i - 1))).mean())
    return (Pbar - Pe) / (1 - Pe) if Pe < 1 else 1.0


def krippendorff_ordinal(M):
    """Alfa com métrica de discrepância ordinal. Forma quadrática por alvo:
    desacordo do alvo = m^T D m / (m_total - 1), com D construída das marginais."""
    Cc = contagens(M, K_CAT)
    n_i = Cc.sum(axis=1)
    ok = n_i >= 2
    Cc, n_i = Cc[ok], n_i[ok]
    if len(n_i) == 0:
        return np.nan
    n_c = Cc.sum(axis=0)
    n_total = n_c.sum()
    if n_total < 2:
        return np.nan
    cum = np.concatenate([[0.0], np.cumsum(n_c)])
    D = np.zeros((K_CAT, K_CAT))
    for c in range(K_CAT):
        for k_ in range(K_CAT):
            lo, hi = min(c, k_), max(c, k_)
            s = (cum[hi + 1] - cum[lo]) - (n_c[lo] + n_c[hi]) / 2.0
            D[c, k_] = s * s
    Do = float((np.einsum("ic,ck,ik->i", Cc, D, Cc) / (n_i - 1)).sum()) / n_total
    De = float(n_c @ D @ n_c) / (n_total * (n_total - 1))
    return 1.0 - Do / De if De > 0 else np.nan


def icc(M):
    """ICC(2,1) e ICC(3,1), avaliador único, sobre os alvos COMPLETOS."""
    Mc = M[~np.isnan(M).any(axis=1)]
    n, k = Mc.shape
    if n < 2 or k < 2:
        return np.nan, np.nan, n
    gm = Mc.mean()
    MSR = k * ((Mc.mean(axis=1) - gm) ** 2).sum() / (n - 1)
    MSC = n * ((Mc.mean(axis=0) - gm) ** 2).sum() / (k - 1)
    SSE = ((Mc - Mc.mean(axis=1, keepdims=True)
            - Mc.mean(axis=0, keepdims=True) + gm) ** 2).sum()
    MSE = SSE / ((n - 1) * (k - 1))
    icc21 = (MSR - MSE) / (MSR + (k - 1) * MSE + k * (MSC - MSE) / n)
    icc31 = (MSR - MSE) / (MSR + (k - 1) * MSE)
    return icc21, icc31, n


def estimar(Q, A):
    """
    Purpose:
        Compute all agreement coefficients for score and acceptance matrices.
    Parameters:
        Q: score matrix
        A: acceptance matrix
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    i21, i31, _ = icc(Q)
    return {
        "kappa_fleiss_Q": fleiss(Q, K_CAT),
        "kappa_fleiss_aceita": fleiss(A, 2),
        "alfa_krippendorff_ordinal": krippendorff_ordinal(Q),
        "ICC_2_1_concordancia": i21,
        "ICC_3_1_consistencia": i31,
    }


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
    Q, A, riz, avals, alvos = carregar_matrizes()
    rizs = sorted(set(riz))
    n_julg = int((~np.isnan(Q)).sum())
    _, _, n_comp = icc(Q)
    print(f"[A12] {n_julg} julgamentos | {len(avals)} avaliadores | "
          f"{len(alvos)} alvos (imagem x método) | {len(rizs)} rizotrons")
    print(f"[A12] alvos completos (sem julgamento ausente): {n_comp} de {len(alvos)}")

    ponto = estimar(Q, A)
    idx_por_riz = {r: np.where(riz == r)[0] for r in rizs}

    rng = np.random.default_rng(SEMENTE)
    dist = defaultdict(list)
    for _ in range(B):
        escolhidos = rng.choice(len(rizs), size=len(rizs), replace=True)
        idx = np.concatenate([idx_por_riz[rizs[e]] for e in escolhidos])
        for k, v in estimar(Q[idx], A[idx]).items():
            if np.isfinite(v):
                dist[k].append(v)

    saida = []
    for k, v in ponto.items():
        d = np.sort(np.array(dist[k]))
        lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        saida.append({"coeficiente": k, "estimativa": round(float(v), 4),
                      "IC95_lo": round(lo, 4), "IC95_hi": round(hi, 4),
                      "B": B, "unidade_reamostragem": "rizotron",
                      "n_rizotrons": len(rizs), "n_alvos": len(alvos),
                      "n_alvos_completos": n_comp})
        print(f"  {k:<28s} {v:.4f}   IC95% [{lo:.4f}; {hi:.4f}]")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(saida[0].keys()))
        w.writeheader()
        w.writerows(saida)
    print(f"\n[A12] {OUT.name} gravado.")


if __name__ == "__main__":
    main()
