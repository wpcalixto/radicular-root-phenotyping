#!/usr/bin/env python3
"""
Title:
    Figure: reflection conditioning example
File type:
    Script
Purpose:
    Writes original, inpainting mask, reconstructed image and removed region panels for one example
    image (04_figura_resultado_*.pdf).
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
    - none detected by static analysis
Outputs:
    - 04_figura_resultado_a.pdf
    - 04_figura_resultado_b.pdf
    - 04_figura_resultado_c.pdf
    - 04_figura_resultado_d.pdf
Dependencies:
    - PIL
    - matplotlib
    - numpy
Execution:
    python scripts/fig_deflash.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura do Bloco B (deflash 05A) — PAINÉIS SEPARADOS (protocolo: 1 PDF por painel,
montagem com \\subfigure no LaTeX; SEM rótulo/título dentro da imagem):
  04_figura_resultado_a.pdf  original com reflexo especular
  04_figura_resultado_b.pdf  máscara do inpainting
  04_figura_resultado_c.pdf  imagem reconstruída (LaMa)
  04_figura_resultado_d.pdf  região removida (vermelho + contorno)
Exemplo: R05_31_05_2025 (reflexo moderado; 4,9% reconstruído).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(AQUI)
IMG = "31_05_2025/R05_31_05_2025.png"
ORIG = os.path.join(BASE, "saidas", "05_registradas", IMG)
MASK = os.path.join(BASE, "saidas", "05A_tratadas", "_mascaras", IMG)
TRAT = os.path.join(BASE, "saidas", "05A_tratadas", IMG)
OUTDIR = os.path.join(BASE, "Artigo_revista")

plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                     "figure.dpi": 300, "savefig.dpi": 300})


def save_panel(fname, img, cmap=None, overlay=None, contour=None):
    """
    Purpose:
        Write one image panel with optional overlay and contour.
    Parameters:
        fname: output file
        img: image
        cmap: colour map
        overlay: mask
        contour: contour flag
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    h, w = img.shape[:2]
    fig = plt.figure(figsize=(4, 4 * h / w))
    ax = fig.add_axes([0, 0, 1, 1])            # eixo preenche a figura (sem margens)
    ax.imshow(img, cmap=cmap)
    if overlay is not None:
        ax.imshow(overlay)
    if contour is not None:
        ax.contour(contour.astype(float), levels=[0.5], colors="k", linewidths=1.6)
    ax.set_axis_off()
    fig.savefig(os.path.join(OUTDIR, fname), format="pdf", dpi=300)
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
    orig = np.asarray(Image.open(ORIG).convert("RGB"))
    trat = np.asarray(Image.open(TRAT).convert("RGB"))
    mask = np.asarray(Image.open(MASK).convert("L"))
    mbin = mask > 127
    over = np.zeros((*mbin.shape, 4)); over[mbin] = [0.90, 0.10, 0.10, 0.45]

    save_panel("04_figura_resultado_a.pdf", orig)
    save_panel("04_figura_resultado_b.pdf", mask, cmap="gray")
    save_panel("04_figura_resultado_c.pdf", trat)
    save_panel("04_figura_resultado_d.pdf", trat, overlay=over, contour=mbin)
    print("[fig_deflash] 4 painéis -> 04_figura_resultado_{a,b,c,d}.pdf")


if __name__ == "__main__":
    main()
