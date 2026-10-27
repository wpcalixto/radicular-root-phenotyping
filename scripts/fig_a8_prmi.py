#!/usr/bin/env python3
"""
Title:
    Figure: PRMI paired differences
File type:
    Script
Purpose:
    Draws the forest plot of M3-M2 and M3-M1 differences on the PRMI test (20_figura_resultado.pdf).
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
    - metricas/A8_prmi_resumo.csv
Outputs:
    - 20_figura_resultado.pdf
Dependencies:
    - matplotlib
    - numpy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_a8_prmi.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi)
    with identical page size to the RSOS files (SHA-256 differs only by PDF metadata). Environment
    of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not
    redistributed in these packages.
"""
# Original module notes (Portuguese) are preserved below.
"""
Figura do resultado A8 — diferenças pareadas M3−M2 e M3−M1 no teste PRMI (sanidade cross-domain),
forest plot (1 painel PDF): 20_figura_resultado.pdf. IC95% clusterizado por unidade parental.
Rótulos em INGLÊS (padrão do projeto). Entrada: metricas/A8_prmi_resumo.csv.
"""
import os, sys, csv, shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

OUTDIR = C.ROOT / "Artigo_revista"
USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)

# métrica -> rótulo inglês; ordem topo->base
MET = [("dice", "Dice"), ("iou", "IoU"), ("prec", "Precision"),
       ("rec", "Sensitivity"), ("spec", "Specificity"), ("cldice", "clDice"), ("skrec", "Skeleton recall")]
C_M2, C_M1 = E.COR_MET["M2"], E.COR_MET["M1"]   # contraste M3-M2 / M3-M1
K_M2, K_M1 = E.MARCA_MET["M2"], E.MARCA_MET["M1"]


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
    rows = {r["metrica"]: r for r in csv.DictReader(open(C.METRICAS / "A8_prmi_resumo.csv"))
            if r["tipo"] == "diff"}
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    n = len(MET)
    yt, yl = [], []
    for k, (met, lab) in enumerate(MET):
        yy = n - k; yt.append(yy); yl.append(lab)
        for ref, cor, mk, off in [("M2", C_M2, K_M2, +0.15), ("M1", C_M1, K_M1, -0.15)]:
            key = f"{met}_M3-{ref}"
            if key not in rows: continue
            m = float(rows[key]["valor"]); lo = float(rows[key]["lo"]); hi = float(rows[key]["hi"])
            ax.plot([lo, hi], [yy + off, yy + off], color=cor, lw=1.8, zorder=2)
            ax.scatter([m], [yy + off], color=cor, marker=mk, s=75, edgecolor="black", linewidth=0.5, zorder=3)
    ax.axvline(0, color="0.6", lw=1.0, ls="--", zorder=1)
    ax.set_yticks(yt); ax.set_yticklabels(yl)
    ax.set_ylim(0.4, n + 0.6)
    ax.set_xlabel(r"Paired difference (M3 $-$ M2 / M1) on PRMI test")
    ax.tick_params(axis="x", labelsize=13)
    ax.scatter([], [], color=C_M2, marker=K_M2, s=75, edgecolor="black", linewidth=0.5, label=r"M3 $-$ M2")
    ax.scatter([], [], color=C_M1, marker=K_M1, s=75, edgecolor="black", linewidth=0.5, label=r"M3 $-$ M1")
    ax.legend(loc="lower right", frameon=True)
    fig.savefig(OUTDIR / "20_figura_resultado.pdf", format="pdf")
    plt.close(fig)
    print("  -> 20_figura_resultado.pdf")


if __name__ == "__main__":
    main()
