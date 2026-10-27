#!/usr/bin/env python3
"""
Title:
    Figure: final biomass by treatment
File type:
    Script
Purpose:
    Draws shoot and root air-dry mass per treatment with individual rhizotrons
    (14_figura_resultado_*.pdf).
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
    - 14_figura_resultado_a.pdf
    - 14_figura_resultado_b.pdf
    - metricas/multimodal_targets.csv
Outputs:
    - printed results only
Dependencies:
    - matplotlib
    - numpy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_biomassa.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura do Bloco D (desfechos) — PAINÉIS SEPARADOS (auditoria V24: pontos individuais
por rizotron, pois n=3 por tratamento):
  14_figura_resultado_a.pdf  massa aérea por tratamento (pontos = rizotrons)
  14_figura_resultado_b.pdf  massa radicular por tratamento (pontos = rizotrons)
Barra = média do tratamento; pontos = 3 rizotrons. Entrada: multimodal_targets.csv.
"""
import os, sys, csv, shutil
import statistics as st
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
LAB = {"REF": "Reference", "T1": "Treat. 1", "T2": "Treat. 2", "T3": "Treat. 3"}

USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)


def painel(col, ylabel, fname):
    """
    Purpose:
        Draw one biomass panel by treatment.
    Parameters:
        col: outcome column
        ylabel: axis label
        fname: output file
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    vals = defaultdict(list)
    for r in csv.DictReader(open(C.METRICAS / "multimodal_targets.csv")):
        if r.get(col):
            vals[r["tratamento"]].append(float(r[col]))
    fig, ax = plt.subplots(figsize=(6.0, 5.0))
    for i, t in enumerate(TRATS):
        m = st.mean(vals[t])
        ax.bar(i, m, color=COR[t], alpha=0.35, width=0.6, edgecolor="black", linewidth=0.6)
        jit = np.linspace(-0.12, 0.12, len(vals[t]))
        ax.scatter(i + jit, vals[t], color=COR[t], marker=MARCA[t], s=95,
                   edgecolor="black", linewidth=0.6, zorder=3)
    ax.set_xticks(range(len(TRATS))); ax.set_xticklabels([LAB[t] for t in TRATS])
    ax.set_ylabel(ylabel)
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
    painel("M_a", "Shoot dry mass [g]", "14_figura_resultado_a.pdf")
    painel("M_r", "Root dry mass [g]", "14_figura_resultado_b.pdf")
    print("[fig_biomassa] 2 painéis -> 14_figura_resultado_{a,b}.pdf")


if __name__ == "__main__":
    main()
