#!/usr/bin/env python3
"""
Title:
    Figure: temporal dynamics
File type:
    Script
Purpose:
    Draws treatment mean curves of apparent conductivity and skeleton length versus DAP
    (10_figura_resultado_*.pdf).
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
    - 10_figura_resultado_a.pdf
    - 10_figura_resultado_b.pdf
    - 10_figura_resultado_legenda.pdf
    - metricas/multimodal_long.csv
    - metricas/temporal_by_treatment.csv
Outputs:
    - printed results only
Dependencies:
    - matplotlib
    - numpy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_temporal.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura do Bloco E (dinâmica temporal) — PAINÉIS SEPARADOS (1 PDF por painel, \\subfigure;
sem marcador "(a)"/título dentro da figura):
  10_figura_resultado_a.pdf  condutividade aparente sigma_a por tratamento ao longo do DAP
  10_figura_resultado_b.pdf  comprimento esqueletizado L_skel por tratamento ao longo do DAP
Curvas média +/- erro-padrão por tratamento (n=3 rizotrons). Entrada: temporal_by_treatment.csv.
"""
import os
import sys
import csv
import shutil
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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


ADUB = {30: "Treatment 2", 60: "Treatment 3"}   # adubações dentro da janela (DAP)


def serie_media(var, scale):
    """
    Purpose:
        Treatment mean and standard error series for one variable.
    Parameters:
        var: variable
        scale: scale factor
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rows = [r for r in csv.DictReader(open(C.METRICAS / "temporal_by_treatment.csv"))
            if r["variavel"] == var]
    d = defaultdict(dict)
    for r in rows:
        d[r["tratamento"]][int(r["DAP"])] = float(r["media"]) * scale
    return d


def serie_rizotron(var, scale):
    """{tratamento: {rizotron: {DAP: val}}} a partir do multimodal_long."""
    d = defaultdict(lambda: defaultdict(dict))
    for r in csv.DictReader(open(C.METRICAS / "multimodal_long.csv")):
        v = r.get(var, "")
        if v not in ("", None) and r["DAP"] not in ("", None):
            d[r["tratamento"]][r["rizotron"]][int(r["DAP"])] = float(v) * scale
    return d


def painel(var, scale, ylabel, fname):
    """
    Purpose:
        Draw one temporal panel.
    Parameters:
        var: variable
        scale: scale
        ylabel: label
        fname: output file
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    med = serie_media(var, scale)
    ind = serie_rizotron(var, scale)
    fig, ax = plt.subplots(figsize=(6.2, 5.0))
    for dap in ADUB:
        ax.axvline(dap, color="0.6", ls=":", lw=1.2, zorder=0)
    for t in TRATS:
        for riz, s in ind[t].items():                       # trajetórias individuais (finas)
            daps = sorted(s)
            ax.plot(daps, [s[k] for k in daps], color=COR[t], lw=0.8, alpha=0.35, zorder=1)
        daps = sorted(med[t])                               # média do tratamento (espessa)
        ax.plot(daps, [med[t][k] for k in daps], marker=MARCA[t], color=COR[t], markersize=7,
                label=NOME[t], lw=2.6, zorder=3)
    ax.set_xlabel("Days after planting [DAP]"); ax.set_ylabel(ylabel)
    finish(fig, ax, fname)


def painel_legenda(fname):
    """Faixa de legenda: item proprio, sem letra, entre os dois paineis."""
    fig, ax = plt.subplots(figsize=(1.9, 2.0))
    for t in TRATS:
        ax.plot([], [], marker=MARCA[t], color=COR[t], markersize=7, lw=2.6, label=NOME[t])
    ax.legend(loc="center", frameon=False, handletextpad=0.6, labelspacing=1.0, borderpad=0.0)
    ax.set_axis_off()
    finish(fig, ax, fname)


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
    painel("sigma_a", 1000.0, r"Apparent conductivity $\sigma_a$ [mS m$^{-1}$]", "10_figura_resultado_a.pdf")
    painel_legenda("10_figura_resultado_legenda.pdf")
    painel("L_skel_px", 1 / 1000.0, r"Skeleton length $L_{\mathrm{skel}}$ [kpx]", "10_figura_resultado_b.pdf")
    print("[fig_temporal] 2 painéis (trajetórias individuais + média; adubações 30/60 DAP) "
          "-> 10_figura_resultado_{a,b}.pdf")


if __name__ == "__main__":
    main()
