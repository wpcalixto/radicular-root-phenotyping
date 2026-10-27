#!/usr/bin/env python3
"""
Title:
    Figure: observed versus predicted mass
File type:
    Script
Purpose:
    Draws observed versus leave-one-rhizotron-out predictions for root and shoot mass
    (13_figura_resultado_*.pdf).
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
    - 13_figura_resultado_a.pdf
    - 13_figura_resultado_b.pdf
    - 13_figura_resultado_legenda.pdf
    - metricas/predictions_by_rhizotron.csv
Outputs:
    - printed results only
Dependencies:
    - matplotlib
    - numpy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_pred.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura suplementar do Bloco E (predição por rizotron) — PAINÉIS SEPARADOS:
  13_figura_resultado_a.pdf  massa radicular observada vs prevista (LORO, Ridge)
  13_figura_resultado_b.pdf  massa aérea observada vs prevista (LORO, SVR)
Um ponto por rizotron (n=12), cor por tratamento; linha 1:1 tracejada.
Entrada: predictions_by_rhizotron.csv.
"""
import os
import sys
import csv
import shutil

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

OUTDIR = C.ROOT / "Artigo_revista"
COR = E.COR_TRAT
LAB_T = {"REF": "Reference", "T1": "Treatment 1", "T2": "Treatment 2", "T3": "Treatment 3"}
MARCA = E.MARCA_TRAT
LINHA = E.LINHA_TRAT

USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)


def painel(alvo, modelo, label, fname):
    """
    Purpose:
        Draw one observed-versus-predicted panel.
    Parameters:
        alvo: outcome
        modelo: model name
        label: axis label
        fname: output file
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rows = [r for r in csv.DictReader(open(C.METRICAS / "predictions_by_rhizotron.csv"))
            if r["alvo"] == alvo and r["modelo"] == modelo]
    yt = [float(r["y_true"]) for r in rows]
    yp = [float(r["y_pred"]) for r in rows]
    trats = [C.tratamento(r["rizotron"])[0] for r in rows]
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    lo, hi = min(yt + yp), max(yt + yp)
    pad = 0.08 * (hi - lo)
    ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], ls="--", color="black", lw=1.2, zorder=1)
    for t in ("REF", "T1", "T2", "T3"):
        m = [i for i, tt in enumerate(trats) if tt == t]
        if m:
            ax.scatter([yt[i] for i in m], [yp[i] for i in m], color=COR[t],
                       marker=MARCA[t], s=90, edgecolor="black", linewidth=0.5,
                       zorder=3, label=LAB_T[t])
    ax.set_xlabel(f"Observed {label} [g]"); ax.set_ylabel(f"Predicted {label} [g]")
    ax.set_xlim(lo - pad, hi + pad); ax.set_ylim(lo - pad, hi + pad)
    return E.finalizar(fig, ax, OUTDIR / fname)


def painel_legenda(fname):
    """Faixa em uma linha, acima da fila: os quatro tratamentos identificam os
    painéis (a) e (b); os três alvos preditos identificam o painel (c)."""
    fig, ax = plt.subplots(figsize=(19.0, 0.55))
    for t in ("REF", "T1", "T2", "T3"):
        ax.scatter([], [], color=COR[t], marker=MARCA[t], s=90,
                   edgecolor="black", linewidth=0.5, label=LAB_T[t])
    for k in ("M_R", "M_PA", "Q"):
        ax.plot([], [], color=E.COR_ALVO[k], marker=E.MARCA_ALVO[k], markersize=8,
                ls=E.LINHA_ALVO[k], lw=2, label=E.LAB_ALVO[k])
    ax.legend(loc="center", frameon=False, ncol=7, handletextpad=0.6,
              columnspacing=1.8, borderpad=0.0)
    ax.set_axis_off()
    return E.finalizar(fig, ax, OUTDIR / fname)


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
    painel("y_M_r", "Ridge", r"root mass $M_{\mathrm{R}}$", "13_figura_resultado_a.pdf")
    painel("y_M_a", "SVR", r"shoot mass $M_{\mathrm{PA}}$", "13_figura_resultado_b.pdf")
    painel_legenda("13_figura_resultado_legenda.pdf")
    print("[fig_pred] modo=%s" % E.modo())


if __name__ == "__main__":
    main()
