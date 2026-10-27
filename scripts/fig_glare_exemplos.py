#!/usr/bin/env python3
"""
Title:
    Figure: low and moderate glare examples
File type:
    Script
Purpose:
    Draws two same-date examples of low and moderate central reflection with the quality-control
    central region.
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
    - R05_31_05_2025.png
    - R12_31_05_2025.png
Outputs:
    - Artigo_revista/04_figura_resultado.pdf
Dependencies:
    - PIL
    - matplotlib
    - numpy
    - local: estilo_figuras
Execution:
    python scripts/fig_glare_exemplos.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura COMPLEMENTAR (opcional) da subseção de preparação/QC:
exemplos representativos de reflexo especular central BAIXO e MODERADO,
com o retângulo da região central (35%-65% de largura e altura) usada no QC.

Par escolhido na MESMA data (31/05/2025) para controlar o estágio de crescimento:
  - baixo:    R12_31_05_2025 (R_c=1,36; G_c=0,036)
  - moderado: R05_31_05_2025 (R_c=1,67; G_c=0,059)

Saída: Artigo_revista/04_figura_resultado.pdf
"""
import os
import sys
import shutil

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import estilo_figuras as E
BASE = os.path.dirname(AQUI)
CONV = os.path.join(BASE, "saidas", "03_convertidas", "31_05_2025")
OUT = os.path.join(BASE, "Artigo_revista", "04_figura_resultado.pdf")

PAINEIS = [
    ("R12_31_05_2025.png", r"(a) Reflexo baixo ($R_c=1{,}36$)"),
    ("R05_31_05_2025.png", r"(b) Reflexo moderado ($R_c=1{,}67$)"),
]
A1, A2 = 0.35, 0.65          # limites da região central (fração)

USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)


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
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 6.6))
    for ax, (fn, rot) in zip(axs, PAINEIS):
        im = np.asarray(Image.open(os.path.join(CONV, fn)).convert("RGB"))
        H, W = im.shape[:2]
        ax.imshow(im)
        ax.add_patch(Rectangle((A1 * W, A1 * H), (A2 - A1) * W, (A2 - A1) * H,
                               fill=False, edgecolor="#e6194b", linewidth=2.2,
                               linestyle="--"))
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_xlabel(rot)
    fig.savefig(OUT, format="pdf", dpi=200)
    plt.close(fig)
    print(f"[fig_glare_exemplos] usetex={USETEX} -> {OUT}")


if __name__ == "__main__":
    main()
