#!/usr/bin/env python3
"""
Title:
    Figure: assessment scores and acceptance
File type:
    Script
Purpose:
    Draws quality-score boxplots with assessor means and acceptance rates by method
    (07_figura_resultado_*.pdf).
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
    - metricas/08D_metodos_agregado.csv
    - metricas/08D_por_avaliador.csv
    - metricas/08D_selecao_por_imagem.csv
Outputs:
    - 07_figura_resultado_a.pdf
    - 07_figura_resultado_b.pdf
Dependencies:
    - matplotlib
    - numpy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_segment_quality.py (from a workspace prepared with
    tools/prepare_workspace.py)
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
Figura do Bloco C (qualidade) — PAINÉIS SEPARADOS (1 PDF por painel, \\subfigure; sem
marcador "(a)"/título dentro da figura):
  07_figura_resultado_a.pdf  boxplot da nota Q por método + médias por avaliador
  07_figura_resultado_b.pdf  taxa de aceitação por método
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

PORIMG = C.METRICAS / "08D_selecao_por_imagem.csv"
PORAVA = C.METRICAS / "08D_por_avaliador.csv"
AGG = C.METRICAS / "08D_metodos_agregado.csv"
OUTDIR = C.ROOT / "Artigo_revista"
METS = ["M1", "M2", "M3"]
COR = E.COR_MET
MARCA = E.MARCA_MET
HACHURA = E.HACHURA_MET

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
    porimg = list(csv.DictReader(open(PORIMG, encoding="utf-8")))
    porava = list(csv.DictReader(open(PORAVA, encoding="utf-8")))
    agg = {r["metodo"]: r for r in csv.DictReader(open(AGG, encoding="utf-8"))}
    Q = {m: np.array([float(r[m]) for r in porimg]) for m in METS}
    ava = {m: np.array([float(r[m]) for r in porava]) for m in METS}
    acc = [float(agg[m]["taxa_aceitacao"]) * 100 for m in METS]

    # (a) boxplot + medias por avaliador
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    bp = ax.boxplot([Q[m] for m in METS], positions=range(len(METS)), widths=0.55,
                    patch_artist=True, medianprops=dict(color="black"))
    for patch, m in zip(bp["boxes"], METS):
        patch.set_facecolor(COR[m]); patch.set_alpha(0.55)
    rng = np.linspace(-0.12, 0.12, len(porava))
    for i, m in enumerate(METS):
        ax.scatter(i + rng, ava[m], color="black", s=30, zorder=3)
    ax.set_xticks(range(len(METS))); ax.set_xticklabels(METS)
    ax.set_ylabel(r"Quality score $\bar{Q}$ [0--4]"); ax.set_xlabel("Segmentation method")
    finish(fig, ax, "07_figura_resultado_a.pdf")

    # (b) aceitacao
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    ax.bar(range(len(METS)), acc, color=[COR[m] for m in METS], alpha=0.8, edgecolor="black", linewidth=0.6)
    for i, v in enumerate(acc):
        ax.text(i, v + 1.0, f"{v:.0f}\\%", ha="center")
    ax.set_xticks(range(len(METS))); ax.set_xticklabels(METS)
    ax.set_ylabel("Acceptance rate [\\%]"); ax.set_xlabel("Segmentation method"); ax.set_ylim(0, 100)
    finish(fig, ax, "07_figura_resultado_b.pdf")

    print("[fig_segment_quality] 2 painéis -> 07_figura_resultado_{a,b}.pdf")


if __name__ == "__main__":
    main()
