#!/usr/bin/env python3
"""
Title:
    Statistical comparison of methods
File type:
    Script
Purpose:
    Tests differences in quality score (Friedman, Kendall W, paired Wilcoxon with Holm correction)
    and acceptance between methods over the repeated-measures design of the blinded assessment.
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
    - figures/08_estatistica
    - metricas/notas_recebidas/*.xlsx
    - metricas/review_key.csv
Outputs:
    - figures/08_estatistica/boxplot_Q.png
    - metricas/08F_estatistica.csv
Dependencies:
    - matplotlib
    - numpy
    - scipy
    - statsmodels
    - local: config
Execution:
    python scripts/08F_estatistica.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 0. Verification in v1.0.0: re-executed in an isolated workspace built from
    the Dataset; outputs byte-identical to the archived versions. Environment of the verification:
    Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Fase 08F — Prova estatística de que o M3 (combinado) é superior a M1 (Frangi) e
M2 (PRMI), a partir das notas dos 5 avaliadores (avaliação cega, escala 0–4).

Desenho: medidas repetidas (mesmas 82 imagens avaliadas pelos 3 métodos), dados
ordinais → testes NÃO paramétricos.
  - Qualidade (Q_global): Friedman (omnibus) + Kendall's W (tamanho de efeito) +
    pós-hoc Wilcoxon pareado (M3×M1, M3×M2, M2×M1) com correção de Holm e
    correlação rank-biserial pareada.
  - Aceitação (binária, maioria ≥3/5): Cochran's Q (omnibus) + McNemar pareado (Holm).
  - Consistência entre avaliadores: cada avaliador ordena os métodos.

Entradas: metricas/notas_recebidas/*.xlsx|*.csv, metricas/review_key.csv
Saídas:   metricas/08F_estatistica.csv, figures/08_estatistica/boxplot_Q.png
"""
import os
import sys
import csv
import importlib.util
import statistics as st
from collections import defaultdict

import numpy as np
from scipy.stats import friedmanchisquare, wilcoxon, rankdata
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.contingency_tables import cochrans_q, mcnemar

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

# reaproveita o carregador robusto do 08D (lê .xlsx/.csv pt-BR, mapeia código→método)
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "08D_selecao.py")
_spec = importlib.util.spec_from_file_location("d08", _p)
d08 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(d08)

ORDEM = ["M1", "M2", "M3"]
NOMES = {"M1": "M1 (Frangi)", "M2": "M2 (PRMI)", "M3": "M3 (combinado)"}


def rank_biserial(a, b):
    """Correlação rank-biserial pareada (efeito do Wilcoxon). a,b = arrays pareados."""
    d = np.asarray(a, float) - np.asarray(b, float)
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    r = rankdata(np.abs(d))
    return float((r[d > 0].sum() - r[d < 0].sum()) / r.sum())


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
    key = {(r["image_id"], r["codigo"]): r["metodo_real"]
           for r in csv.DictReader(open(d08.KEY, encoding="utf-8"))}
    notas = d08.carregar()
    for r in notas:
        r["M"] = d08.LABELS.get(key.get((r["image_id"], r.get("codigo")), "?"), "?")

    # Q por (imagem, método) entre avaliadores; aceite por (imagem, método)
    Q = defaultdict(lambda: defaultdict(list))
    A = defaultdict(lambda: defaultdict(list))
    avaliadores = set()
    for r in notas:
        if r["M"] not in ORDEM:
            continue
        avaliadores.add(r["avaliador"])
        Q[r["image_id"]][r["M"]].append(r["_Q"])
        A[r["image_id"]][r["M"]].append(1 if d08.aceito(r.get("aceita")) else 0)

    imgs = sorted(i for i in Q if all(m in Q[i] for m in ORDEM))
    nav = len(avaliadores)
    # média entre avaliadores por imagem
    QM = {m: np.array([st.mean(Q[i][m]) for i in imgs]) for m in ORDEM}
    # aceite por maioria (≥ metade dos avaliadores)
    AM = {m: np.array([1 if sum(A[i][m]) >= (nav / 2) else 0 for i in imgs]) for m in ORDEM}

    linhas = []
    def add(tipo="", **kw):
        linhas.append({"grupo": kw.get("g", ""), "metrica": kw.get("metrica", tipo), "valor": kw.get("v", ""),
                       "estatistica": kw.get("s", ""), "p_valor": kw.get("p", ""),
                       "p_ajustado_holm": kw.get("pa", ""), "efeito": kw.get("e", "")})

    # ---------- descritivo ----------
    print(f"[08F] {len(imgs)} imagens × 3 métodos | {nav} avaliadores\n")
    print("  Descritivo Q_global (média entre avaliadores, por imagem):")
    for m in ORDEM:
        v = QM[m]
        print(f"    {NOMES[m]:16s} média={v.mean():.3f}  mediana={np.median(v):.3f}  "
              f"IQR=[{np.percentile(v,25):.2f},{np.percentile(v,75):.2f}]")
        add("Q_media", g="descritivo", metrica=f"Q_media_{m}", v=round(v.mean(), 3))

    # ---------- Friedman (qualidade) ----------
    chi, p = friedmanchisquare(QM["M1"], QM["M2"], QM["M3"])
    W = chi / (len(imgs) * (len(ORDEM) - 1))     # Kendall's W
    print(f"\n  Friedman (Q_global, 3 métodos): χ²={chi:.2f}, p={p:.2e}, Kendall W={W:.3f}")
    add("Friedman_Q", g="omnibus_qualidade", s=round(chi, 3), p=f"{p:.3e}", e=f"W={W:.3f}")

    # ---------- pós-hoc Wilcoxon (Holm) ----------
    pares = [("M3", "M1"), ("M3", "M2"), ("M2", "M1")]
    praw, stats_, efs = [], [], []
    for a, b in pares:
        s, pv = wilcoxon(QM[a], QM[b])
        praw.append(pv); stats_.append(s); efs.append(rank_biserial(QM[a], QM[b]))
    padj = multipletests(praw, method="holm")[1]
    print("\n  Pós-hoc Wilcoxon pareado (Holm) — Q_global:")
    for (a, b), s, pv, pa, e in zip(pares, stats_, praw, padj, efs):
        print(f"    {a} vs {b}: W={s:.1f}  p={pv:.2e}  p_Holm={pa:.2e}  rank-biserial={e:+.3f}")
        add("Wilcoxon", g="posthoc_qualidade", metrica=f"{a}_vs_{b}", s=round(s, 1),
            p=f"{pv:.3e}", pa=f"{pa:.3e}", e=round(e, 3))

    # ---------- Cochran's Q (aceitação) ----------
    mat = np.column_stack([AM[m] for m in ORDEM])
    cq = cochrans_q(mat)
    print(f"\n  Cochran's Q (aceitação por maioria): Q={cq.statistic:.2f}, p={cq.pvalue:.2e}")
    add("Cochran_Q", g="omnibus_aceitacao", s=round(float(cq.statistic), 3), p=f"{cq.pvalue:.3e}")
    for m in ORDEM:
        print(f"    aceitação {m}: {AM[m].mean():.0%}")
        add("aceitacao", g="descritivo", metrica=f"aceita_{m}", v=round(float(AM[m].mean()), 3))

    # ---------- pós-hoc McNemar (Holm) ----------
    praw2, stats2 = [], []
    for a, b in pares:
        t = np.array([[int(((AM[a] == 1) & (AM[b] == 1)).sum()), int(((AM[a] == 1) & (AM[b] == 0)).sum())],
                      [int(((AM[a] == 0) & (AM[b] == 1)).sum()), int(((AM[a] == 0) & (AM[b] == 0)).sum())]])
        res = mcnemar(t, exact=True)
        praw2.append(res.pvalue); stats2.append(float(res.statistic))
    padj2 = multipletests(praw2, method="holm")[1]
    print("\n  Pós-hoc McNemar (Holm) — aceitação:")
    for (a, b), s, pv, pa in zip(pares, stats2, praw2, padj2):
        print(f"    {a} vs {b}: p={pv:.2e}  p_Holm={pa:.2e}")
        add("McNemar", g="posthoc_aceitacao", metrica=f"{a}_vs_{b}", s=round(s, 1),
            p=f"{pv:.3e}", pa=f"{pa:.3e}")

    # ---------- consistência entre avaliadores ----------
    topo = defaultdict(int)
    for av in sorted(avaliadores):
        med = {m: st.mean([r["_Q"] for r in notas if r["avaliador"] == av and r["M"] == m]) for m in ORDEM}
        topo[max(med, key=med.get)] += 1
    print("\n  Método preferido (maior Q médio) por avaliador:")
    for m in ORDEM:
        if topo.get(m):
            print(f"    {m}: {topo[m]}/{nav} avaliadores")
    add("consistencia", g="avaliadores", metrica="M3_top_avaliadores", v=f"{topo.get('M3',0)}/{nav}")

    # ---------- CSV + figura ----------
    with open(C.METRICAS / "08F_estatistica.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["grupo", "metrica", "valor", "estatistica", "p_valor",
                                          "p_ajustado_holm", "efeito"])
        w.writeheader(); w.writerows(linhas)

    figd = C.FIGURES / "08_estatistica"; figd.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 5))
    dados = [QM[m] for m in ORDEM]
    bp = ax.boxplot(dados, tick_labels=[NOMES[m] for m in ORDEM], showmeans=True, patch_artist=True)
    for patch, cor in zip(bp["boxes"], ["#DD8452", "#55A868", "#4C72B0"]):
        patch.set_facecolor(cor); patch.set_alpha(0.6)
    for i, m in enumerate(ORDEM, 1):
        ax.scatter(np.random.default_rng(0).normal(i, 0.05, len(QM[m])), QM[m], s=8, c="k", alpha=0.3)
    ax.set_ylabel("Q_global (média entre 5 avaliadores)")
    ax.set_title(f"Qualidade por método (n={len(imgs)} imagens)\nFriedman p={p:.1e}, Kendall W={W:.2f}")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout(); fig.savefig(figd / "boxplot_Q.png", dpi=150); plt.close(fig)

    print(f"\n  → Saídas: metricas/08F_estatistica.csv, figures/08_estatistica/boxplot_Q.png")


if __name__ == "__main__":
    main()
