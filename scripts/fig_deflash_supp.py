#!/usr/bin/env python3
"""
Title:
    Figure: reconstruction characterisation (SI)
File type:
    Script
Purpose:
    Draws the distribution of reconstructed fraction and specular cores and their relation to
    collection, rhizotron and glare indices (05_figura_resultado_*.pdf).
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
    - metricas/image_qc.csv
    - metricas/pretratamento_05A.csv
Outputs:
    - 05_figura_resultado_a.pdf
    - 05_figura_resultado_b.pdf
    - 05_figura_resultado_c.pdf
    - 05_figura_resultado_d.pdf
    - 05_figura_resultado_e.pdf
    - 05_figura_resultado_f.pdf
Dependencies:
    - matplotlib
    - numpy
    - scipy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_deflash_supp.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura SUPLEMENTAR do Bloco B (deflash) — PAINÉIS SEPARADOS (1 PDF por painel,
\\subfigure no LaTeX; SEM marcador "(a)" nem título dentro da figura):
  05_figura_resultado_a.pdf  distribuição da fração reconstruída
  05_figura_resultado_b.pdf  núcleos especulares por imagem
  05_figura_resultado_c.pdf  fração por coleta (DAS)
  05_figura_resultado_d.pdf  fração por rizotron
  05_figura_resultado_e.pdf  fração vs G_c
  05_figura_resultado_f.pdf  fração vs R_c
Cruza pretratamento_05A.csv com image_qc.csv. Protocolo: usetex, serif/CM, 18 pt.
"""
import os
import sys
import csv
import shutil

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

DEFLASH = C.METRICAS / "pretratamento_05A.csv"
QC = C.METRICAS / "image_qc.csv"
OUTDIR = C.ROOT / "Artigo_revista"
COL = "#4C72B0"

USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)


def new_ax():
    """
    Purpose:
        Create a figure with the standard SI size.
    Parameters:
        none
    Returns:
        tuple (fig, ax)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    return fig, ax


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
    d = list(csv.DictReader(open(DEFLASH, encoding="utf-8")))
    qc = {r["image_id"]: r for r in csv.DictReader(open(QC, encoding="utf-8"))}
    pct = np.array([float(r["pct_inpintado"]) for r in d])
    nuc = np.array([int(r["n_nucleos_glare"]) for r in d])
    dap = np.array([C.dap(C.parse_data_pasta(r["data"])) for r in d])
    riz = [r["image_id"].split("_")[0] for r in d]
    Gc = np.array([float(qc[r["image_id"]]["G_c"]) for r in d])
    Rc = np.array([float(qc[r["image_id"]]["R_c"]) for r in d])

    # (a) histograma
    fig, ax = new_ax()
    ax.hist(pct, bins=12, color=COL, edgecolor="black", linewidth=0.6)
    ax.axvline(np.median(pct), color="#C44E52", lw=2, ls="--")
    ax.set_xlabel("Reconstructed fraction [\\% of frame]"); ax.set_ylabel("Images")
    finish(fig, ax, "05_figura_resultado_a.pdf")

    # (b) nucleos
    fig, ax = new_ax()
    vals, cnts = np.unique(nuc, return_counts=True)
    ax.bar(vals, cnts, color=COL, edgecolor="black", linewidth=0.6)
    ax.set_xticks(range(1, int(nuc.max()) + 1))
    ax.set_xlabel("Specular nuclei per image"); ax.set_ylabel("Images")
    finish(fig, ax, "05_figura_resultado_b.pdf")

    # (c) por coleta
    fig, ax = new_ax()
    daps = sorted(set(dap.tolist()))
    ax.boxplot([pct[dap == dd] for dd in daps], positions=range(len(daps)), widths=0.6,
               patch_artist=True, boxprops=dict(facecolor=COL, alpha=0.6), medianprops=dict(color="black"))
    ax.set_xticks(range(len(daps))); ax.set_xticklabels([str(dd) for dd in daps])
    ax.set_xlabel("Days after planting [DAP]"); ax.set_ylabel("Reconstructed fraction [\\%]")
    finish(fig, ax, "05_figura_resultado_c.pdf")

    # (d) por rizotron
    fig, ax = new_ax()
    rid = sorted(set(riz), key=lambda s: int(s[1:]))
    ax.boxplot([pct[[i for i, rr in enumerate(riz) if rr == rk]] for rk in rid],
               positions=range(len(rid)), widths=0.6, patch_artist=True,
               boxprops=dict(facecolor=COL, alpha=0.6), medianprops=dict(color="black"))
    ax.set_xticks(range(len(rid))); ax.set_xticklabels([r[1:] for r in rid])
    ax.set_xlabel("Rhizotron"); ax.set_ylabel("Reconstructed fraction [\\%]")
    finish(fig, ax, "05_figura_resultado_d.pdf")

    # (e) vs G_c
    fig, ax = new_ax()
    rho_g, _ = spearmanr(Gc, pct)
    ax.scatter(Gc, pct, s=28, color=COL, edgecolor="black", linewidth=0.4, alpha=0.8)
    ax.set_xlabel("Central saturation $G_c$"); ax.set_ylabel("Reconstructed fraction [\\%]")
    ax.text(0.95, 0.95, f"$\\rho={rho_g:.2f}$", transform=ax.transAxes, ha="right", va="top")
    finish(fig, ax, "05_figura_resultado_e.pdf")

    # (f) vs R_c
    fig, ax = new_ax()
    rho_r, _ = spearmanr(Rc, pct)
    ax.scatter(Rc, pct, s=28, color=COL, edgecolor="black", linewidth=0.4, alpha=0.8)
    ax.set_xlabel("Brightness ratio $R_c$"); ax.set_ylabel("Reconstructed fraction [\\%]")
    ax.text(0.95, 0.95, f"$\\rho={rho_r:.2f}$", transform=ax.transAxes, ha="right", va="top")
    finish(fig, ax, "05_figura_resultado_f.pdf")

    print(f"[fig_deflash_supp] 6 painéis -> 05_figura_resultado_{{a..f}}.pdf  (rho_Gc={rho_g:.3f}, rho_Rc={rho_r:.3f})")


if __name__ == "__main__":
    main()
