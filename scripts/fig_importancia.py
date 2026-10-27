#!/usr/bin/env python3
"""
Title:
    Figure: importance by modality
File type:
    Script
Purpose:
    Draws the sum of absolute permutation importance by modality for root and shoot mass
    (11_figura_resultado_*.pdf).
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
    - 11_figura_resultado_a.pdf
    - 11_figura_resultado_b.pdf
    - metricas/explainability_by_group.csv
Outputs:
    - printed results only
Dependencies:
    - matplotlib
    - local: config, estilo_figuras
Execution:
    python scripts/fig_importancia.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura do Bloco E (explicabilidade) — PAINÉIS SEPARADOS (1 PDF por painel, \\subfigure;
sem marcador "(a)"/título dentro da figura):
  11_figura_resultado_a.pdf  importância por modalidade para a massa radicular (M_r)
  11_figura_resultado_b.pdf  importância por modalidade para a massa aérea (M_a)
Importância = soma de |PI| por modalidade (permutação, modelo Ridge completo).
Entrada: explainability_by_group.csv.
"""
import os
import sys
import csv
import shutil
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

OUTDIR = C.ROOT / "Artigo_revista"
ORDEM = ["optical", "electrical", "management"]
COR = E.COR_FONTE
MARCA = E.MARCA_FONTE
HACHURA = E.HACHURA_FONTE
LAB = {"optical": "Optical", "electrical": "Electrical", "management": "Management"}

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
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(str(OUTDIR / fname), format="pdf")
    plt.close(fig)


def painel(alvo, fname):
    """
    Purpose:
        Draw one importance panel.
    Parameters:
        alvo: outcome
        fname: output file
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    dados, disp = {}, {}
    for r in csv.DictReader(open(C.METRICAS / "explainability_by_group.csv")):
        if r["tipo"] == "fonte" and r["alvo"] == alvo:
            dados[r["grupo"]] = float(r["I"]); disp[r["grupo"]] = float(r.get("I_std", 0) or 0)
    ordem = [m for m in ORDEM if m in dados]
    fig, ax = plt.subplots(figsize=(6.0, 5.0))
    ax.bar([LAB[m] for m in ordem], [dados[m] for m in ordem],
           yerr=[disp[m] for m in ordem], capsize=4, ecolor="black",
           color=[COR[m] for m in ordem], hatch=[HACHURA[m] for m in ordem],
           edgecolor="black", linewidth=0.6)
    ax.set_ylabel(r"Group permutation importance [$\Delta$MAE, g]")
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
    painel("y_M_r", "11_figura_resultado_a.pdf")
    painel("y_M_a", "11_figura_resultado_b.pdf")
    print("[fig_importancia] 2 painéis -> 11_figura_resultado_{a,b}.pdf")


if __name__ == "__main__":
    main()
