#!/usr/bin/env python3
"""
Title:
    Figure: root quantification
File type:
    Script
Purpose:
    Draws normalised-depth profiles by treatment, harvested projected length versus root mass and in
    situ occupancy versus root mass (09_figura_resultado_*.pdf).
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
    - metricas/multimodal_targets.csv
    - metricas/root_density_by_layer.csv
    - metricas/root_features_by_image.csv
    - metricas/root_harvested.csv
Outputs:
    - 09_figura_resultado_a.pdf
    - 09_figura_resultado_b.pdf
    - 09_figura_resultado_c.pdf
Dependencies:
    - matplotlib
    - numpy
    - scipy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_quant.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi)
    with identical page size to the RSOS files (SHA-256 differs only by PDF metadata). Environment
    of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Figura do Bloco D (quantificação) — PAINÉIS SEPARADOS (1 PDF por painel, \\subfigure;
sem marcador "(a)"/título dentro da figura):
  09_figura_resultado_a.pdf  perfil de profundidade normalizada por tratamento
                             (agregação por rizotron, seis coletas comuns C1-C6)
  09_figura_resultado_b.pdf  raiz colhida (trena) vs massa radicular seca
  09_figura_resultado_c.pdf  ocupação in situ (C6) vs massa radicular final, por rizotron
"""
import os
import sys
import csv
import shutil
import statistics as st
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

OUTDIR = C.ROOT / "Artigo_revista"
TRATS = ["REF", "T1", "T2", "T3"]
COR = E.COR_TRAT
MARCA = E.MARCA_TRAT
LINHA = E.LINHA_TRAT
NOME = {"REF": "Reference", "T1": "Treatment 1", "T2": "Treatment 2", "T3": "Treatment 3"}

USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)


def finish(fig, ax, fname):
    """
    Purpose:
        Apply the figure style, remove top/right spines where applicable and save the panel.
    Parameters:
        fig: matplotlib figure
        ax: axes
        fname: output file name
    Returns:
        path of the written file or None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    escrito = E.finalizar(fig, ax, OUTDIR / fname)
    print("  [%s] %s" % (E.modo(), escrito.split("Artigo_revista/")[-1]))


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
    feat = list(csv.DictReader(open(C.METRICAS / "root_features_by_image.csv")))
    coleta = {r["image_id"]: (int(r["coleta"]) if r["coleta"] else 99) for r in feat}

    # (a) perfil de profundidade — rizotron-first, seis coletas comuns C1-C6
    rows = [r for r in csv.DictReader(open(C.METRICAS / "root_density_by_layer.csv"))
            if coleta.get(r["image_id"], 99) <= 6]
    riz_band = defaultdict(lambda: defaultdict(list))          # riz -> faixa -> [rho]
    riz_trat = {}
    for r in rows:
        riz_band[r["rizotron"]][int(r["faixa"])].append(float(r["rho_area_valida"]))
        riz_trat[r["rizotron"]] = C.tratamento(r["rizotron"])[0]
    prof = defaultdict(lambda: defaultdict(list))              # trat -> faixa -> [riz-mean]
    for riz in riz_band:
        for fa in riz_band[riz]:
            prof[riz_trat[riz]][fa].append(st.mean(riz_band[riz][fa]))
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    for t in TRATS:
        faixas = sorted(prof[t])
        x = [st.mean(prof[t][f]) * 100 for f in faixas]
        sd = [(st.stdev(prof[t][f]) * 100 if len(prof[t][f]) > 1 else 0) for f in faixas]
        y = [(f - 0.5) / 10.0 for f in faixas]
        ax.plot(x, y, marker=MARCA[t], color=COR[t], markersize=7, label=NOME[t], linewidth=2)
        ax.fill_betweenx(y, np.array(x) - np.array(sd), np.array(x) + np.array(sd),
                         color=COR[t], alpha=0.12)
    ax.invert_yaxis()
    ax.set_xlabel("Mean root density [\\% of valid area]"); ax.set_ylabel("Normalized depth [0--1]")
    ax.legend(frameon=False)
    finish(fig, ax, "09_figura_resultado_a.pdf")

    # (b) raiz colhida vs massa (pós-colheita; escala confiável em 9/12)
    h = {r["rizotron"]: r for r in csv.DictReader(open(C.METRICAS / "root_harvested.csv"))}
    tg = {r["rizotron"]: r for r in csv.DictReader(open(C.METRICAS / "multimodal_targets.csv"))}
    xs, ys, cs = [], [], []
    for k in h:
        if h[k].get("escala_flag") == "ok" and h[k].get("L_r_skel_cm") and k in tg and tg[k].get("M_r"):
            xs.append(float(h[k]["L_r_skel_cm"])); ys.append(float(tg[k]["M_r"])); cs.append(COR[C.tratamento(k)[0]])
    rho, p = spearmanr(xs, ys)
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    ax.scatter(xs, ys, c=cs, s=70, edgecolor="black", linewidth=0.5, zorder=3)
    ax.set_xlabel("Projected harvested length [cm]"); ax.set_ylabel("Dry root mass [g]")
    ax.text(0.05, 0.95, f"Spearman $\\rho={rho:.2f}$\n$p={p:.3f}$ ($n={len(xs)}$)",
            transform=ax.transAxes, va="top")
    finish(fig, ax, "09_figura_resultado_b.pdf")

    # (c) ocupação in situ na C6 vs massa radicular final, por rizotron (n=12)
    O_c6 = {}
    for r in feat:
        if int(r["coleta"]) == 6 if r["coleta"] else False:
            O_c6[r["rizotron"]] = float(r["O_ocupacao"]) * 100
    xs2, ys2, cs2 = [], [], []
    for k in O_c6:
        if k in tg and tg[k].get("M_r"):
            xs2.append(O_c6[k]); ys2.append(float(tg[k]["M_r"])); cs2.append(COR[C.tratamento(k)[0]])
    rho2, p2 = spearmanr(xs2, ys2)
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    ax.scatter(xs2, ys2, c=cs2, s=70, edgecolor="black", linewidth=0.5, zorder=3)
    ax.set_xlabel("In situ occupancy at C6 [\\% of valid area]"); ax.set_ylabel("Dry root mass [g]")
    # texto alinhado a direita: sai de cima da nuvem de pontos
    ax.text(0.97, 0.95, f"Spearman $\\rho={rho2:.2f}$\n$p={p2:.2f}$ ($n={len(xs2)}$)",
            transform=ax.transAxes, va="top", ha="right", multialignment="right")
    finish(fig, ax, "09_figura_resultado_c.pdf")

    print(f"[fig_quant] 3 painéis -> 09_figura_resultado_{{a,b,c}}.pdf  "
          f"(colhida rho={rho:.3f}; O_C6 vs M_r rho={rho2:.3f}, p={p2:.3f}, n={len(xs2)})")


if __name__ == "__main__":
    main()
