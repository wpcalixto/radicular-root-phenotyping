#!/usr/bin/env python3
"""
Title:
    Figure: M3 advantage across conditions
File type:
    Script
Purpose:
    Draws forest plots of M3-minus-M1/M2 score and acceptance differences by condition with
    clustered intervals (files 19_figura_resultado_*.pdf).
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
    - 19_figura_resultado_a.pdf
    - 19_figura_resultado_b.pdf
    - 19_figura_resultado_legenda.pdf
    - metricas/A7_resiliencia.csv
Outputs:
    - printed results only
Dependencies:
    - matplotlib
    - numpy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_a7_resiliencia.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura do resultado A7 (estabilidade da vantagem de M3 entre condições) — forest plot,
PAINÉIS SEPARADOS (protocolo: 1 PDF por painel, montados com \\subfigure no .tex):
  19_figura_resultado_a.pdf  Delta Q (M3-M1 e M3-M2) por condição, IC95% cluster bootstrap
  19_figura_resultado_b.pdf  Delta taxa de aceitação (M3-M1 e M3-M2) por condição
Estratos PRIMÁRIOS (independentes da segmentação): G_c, DAP, brilho, contraste, nitidez.
Rótulos em INGLÊS (padrão do projeto). Entrada: metricas/A7_resiliencia.csv.
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

# ordem (topo->base) e rótulo em inglês; None = espaçador visual entre blocos
ORDER = [
    ("Global", "Global"),
    ("Reflexo G_c baixo", r"$G_c$ below median"),
    ("Reflexo G_c alto", r"$G_c$ above median"),
    ("DAP inicial", "Early DAP"),
    ("DAP tardio", "Late DAP"),
    ("Brilho baixo", "Low brightness"),
    ("Brilho alto", "High brightness"),
    ("Contraste baixo", "Low contrast"),
    ("Contraste alto", "High contrast"),
    ("Nitidez baixa", "Low sharpness"),
    ("Nitidez alta", "High sharpness"),
]
C_M1, C_M2 = E.COR_MET["M1"], E.COR_MET["M2"]   # contraste M3-M1 / M3-M2
K_M1, K_M2 = E.MARCA_MET["M1"], E.MARCA_MET["M2"]


def painel(pref, xlabel, fname):
    """
    Purpose:
        Draw one forest-plot panel.
    Parameters:
        pref: column prefix
        xlabel: axis label
        fname: output file
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rows = {r["condicao"]: r for r in csv.DictReader(open(C.METRICAS / "A7_resiliencia.csv"))}
    labels, y = [], []
    fig, ax = plt.subplots(figsize=(6.4, 6.6))
    n = len(ORDER)
    for k, (cond, lab) in enumerate(ORDER):
        yy = n - k
        r = rows[cond]
        labels.append(f"{lab}  ($n_I{{=}}${r['n_img']}, $n_R{{=}}${r['n_riz']})")
        y.append(yy)
        for tag, cor, mk, off in [("M1", C_M1, K_M1, +0.16), ("M2", C_M2, K_M2, -0.16)]:
            m = float(r[f"{pref}_M3_{tag}"]); lo = float(r[f"{pref}_M3_{tag}_lo"]); hi = float(r[f"{pref}_M3_{tag}_hi"])
            ax.plot([lo, hi], [yy + off, yy + off], color=cor, lw=1.6, zorder=2)
            ax.scatter([m], [yy + off], color=cor, marker=mk, s=70, edgecolor="black", linewidth=0.5, zorder=3)
    ax.axvline(0, color="0.6", lw=1.0, ls="--", zorder=1)
    ax.set_yticks(y); ax.set_yticklabels(labels)
    ax.set_ylim(0.4, n + 0.6)
    ax.set_xlabel(xlabel)
    ax.tick_params(axis="x", labelsize=13)
    # sem legenda interna: ela e um painel proprio, o (a) do conjunto
    escrito = E.finalizar(fig, ax, OUTDIR / fname)
    print("  [%s] %s" % (E.modo(), escrito.split("Artigo_revista/")[-1]))


def painel_legenda(fname):
    """Painel (a): apenas a legenda das duas series, em uma linha."""
    fig, ax = plt.subplots(figsize=(6.4, 0.30))
    ax.scatter([], [], color=C_M1, marker=K_M1, s=70, edgecolor="black", linewidth=0.5,
               label=r"M3 $-$ M1")
    ax.scatter([], [], color=C_M2, marker=K_M2, s=70, edgecolor="black", linewidth=0.5,
               label=r"M3 $-$ M2")
    ax.legend(loc="center", ncol=2, frameon=False, handletextpad=0.6, columnspacing=2.6,
              borderpad=0.0)
    ax.set_axis_off()
    escrito = E.finalizar(fig, ax, OUTDIR / fname)
    print("  [%s] %s" % (E.modo(), escrito.split("Artigo_revista/")[-1]))


def main():
    # a faixa de legenda nao e painel: nao recebe letra e tem nome proprio
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
    painel_legenda("19_figura_resultado_legenda.pdf")
    painel("dQ", r"$\Delta \bar{Q}$ (M3 vs. M1 / M2)", "19_figura_resultado_a.pdf")
    painel("dacc", r"$\Delta$ acceptance rate", "19_figura_resultado_b.pdf")


if __name__ == "__main__":
    main()
