#!/usr/bin/env python3
"""
Title:
    Figure: M3 composition
File type:
    Script
Purpose:
    Draws M3 composition per image and the gain of M3 versus the Frangi-exclusive fraction
    (15_figura_resultado_*.pdf).
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
    - metricas/A1_composicao_m3.csv
    - metricas/A1_composicao_m3.csv.
Outputs:
    - 15_figura_resultado_a.pdf
    - 15_figura_resultado_b.pdf
Dependencies:
    - matplotlib
    - numpy
    - scipy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_composicao.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura do resultado A1 (composição de M3) — PAINÉIS SEPARADOS (\\subfigure):
  15_figura_resultado_a.pdf  composição de M3 por imagem (barras empilhadas, ordenadas)
  15_figura_resultado_b.pdf  ganho de M3 sobre cada método vs fração exclusiva do Frangi
Entrada: metricas/A1_composicao_m3.csv.
"""
import os, sys, csv, shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

OUTDIR = C.ROOT / "Artigo_revista"
USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)
C_F, C_E, C_I = E.COR_MET["M1"], E.COR_MET["M2"], E.CINZA   # Frangi / PRMI / interseção
H_F, H_E = E.HACHURA_MET["M1"], E.HACHURA_MET["M2"]
K_F, K_E = E.MARCA_MET["M1"], E.MARCA_MET["M2"]


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
    rows = list(csv.DictReader(open(C.METRICAS / "A1_composicao_m3.csv")))
    pf = np.array([float(r["P_M1"]) for r in rows]) * 100
    pe = np.array([float(r["P_M2"]) for r in rows]) * 100
    pi = np.array([float(r["P_int"]) for r in rows]) * 100
    d31 = np.array([float(r["dQ31"]) for r in rows])
    d32 = np.array([float(r["dQ32"]) for r in rows])

    # (a) barras empilhadas ordenadas por fração exclusiva do Frangi
    o = np.argsort(pf); x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.bar(x, pf[o], color=C_F, hatch=H_F, width=1.0, label="Frangi-exclusive")
    ax.bar(x, pi[o], bottom=pf[o], color=C_I, width=1.0, label="Shared")
    ax.bar(x, pe[o], bottom=pf[o] + pi[o], color=C_E, hatch=H_E, width=1.0, label="PRMI-exclusive")
    ax.set_xlabel("Images (sorted)"); ax.set_ylabel("Composition of M3 [\\%]")
    ax.set_xlim(-0.5, len(rows) - 0.5); ax.set_ylim(0, 100)
    # caixa branca opaca atras da legenda: separa texto e chaves da hachura das barras
    leg = ax.legend(loc="lower right", frameon=True, framealpha=1.0, fancybox=False,
                    facecolor="white", edgecolor="0.35", borderpad=0.55,
                    labelspacing=0.45, handlelength=1.9, handletextpad=0.6)
    leg.set_zorder(10)
    leg.get_frame().set_linewidth(0.9)
    for h in leg.legend_handles:
        h.set_edgecolor("black")
    finish(fig, ax, "15_figura_resultado_a.pdf")

    # (b) ganho de M3 sobre cada método vs fração exclusiva do Frangi
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    r32 = spearmanr(pf, d32)[0]; r31 = spearmanr(pf, d31)[0]
    ax.scatter(pf, d32, s=60, color=C_E, marker=K_E, edgecolor="black", linewidth=0.4,
               label=r"$\Delta\bar{Q}$(M3$-$M2), $\rho=%+.2f$" % r32)
    ax.scatter(pf, d31, s=60, color=C_F, marker=K_F, edgecolor="black", linewidth=0.4,
               label=r"$\Delta\bar{Q}$(M3$-$M1), $\rho=%+.2f$" % r31)
    ax.axhline(0, color="0.6", lw=1.0, ls="--")
    ax.set_xlabel("Frangi-exclusive fraction of M3 [\\%]")
    ax.set_ylabel(r"Quality gain of M3 ($\Delta\bar{Q}$)")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=1, handletextpad=0.4, borderaxespad=0.0)
    finish(fig, ax, "15_figura_resultado_b.pdf")
    print(f"[fig_composicao] 2 painéis -> 15_figura_resultado_{{a,b}}.pdf  (rho32={r32:+.2f}, rho31={r31:+.2f})")


if __name__ == "__main__":
    main()
