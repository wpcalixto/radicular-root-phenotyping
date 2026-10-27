#!/usr/bin/env python3
"""
Title:
    Figure: segmentation comparison
File type:
    Script
Purpose:
    Writes conditioned image, M1, M2 and M3 panels for one example (06_figura_resultado_*.pdf).
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
    - 06_figura_resultado_a.pdf
    - 06_figura_resultado_b.pdf
    - 06_figura_resultado_c.pdf
    - 06_figura_resultado_d.pdf
Dependencies:
    - PIL
    - matplotlib
    - numpy
    - local: config
Execution:
    python scripts/fig_segment_compare.py (from a workspace prepared with
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
Figura do Bloco C (comparação de métodos) — PAINÉIS SEPARADOS (1 PDF por painel,
\\subfigure no LaTeX; SEM rótulo dentro da imagem). Máscara em verde.
  06_figura_resultado_a.pdf  imagem condicionada
  06_figura_resultado_b.pdf  M1 (Frangi)
  06_figura_resultado_c.pdf  M2 (PRMI)
  06_figura_resultado_d.pdf  M3 (M1 ∪ M2)
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

IMG = "14_06_2025/R05_14_06_2025.png"
BASE = C.SAIDAS
IMGP = BASE / "05A_tratadas" / IMG
M1P = BASE / "07_frangi" / "masks" / IMG
M2P = BASE / "06C_inferencia" / "masks" / IMG
M3P = BASE / "08_combinado_limpo" / "masks" / IMG   # M3 final (Frangi refinado ∪ M2)
OUTDIR = C.ROOT / "Artigo_revista"

plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                     "figure.dpi": 300, "savefig.dpi": 300})


def save_panel(fname, rgb, mask=None):
    """
    Purpose:
        Write one mask panel over the image.
    Parameters:
        fname: output file
        rgb: image
        mask: mask
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    img = rgb.copy()
    if mask is not None:
        img[mask] = [0.15, 0.85, 0.15]
    h, w = img.shape[:2]
    fig = plt.figure(figsize=(4, 4 * h / w))
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.set_axis_off()
    fig.savefig(str(OUTDIR / fname), format="pdf", dpi=300)
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
    rgb = np.asarray(Image.open(IMGP).convert("RGB")).astype(float) / 255.0
    m1 = np.asarray(Image.open(M1P).convert("L")) > 127
    m2 = np.asarray(Image.open(M2P).convert("L")) > 127
    m3 = np.asarray(Image.open(M3P).convert("L")) > 127
    save_panel("06_figura_resultado_a.pdf", rgb)
    save_panel("06_figura_resultado_b.pdf", rgb, m1)
    save_panel("06_figura_resultado_c.pdf", rgb, m2)
    save_panel("06_figura_resultado_d.pdf", rgb, m3)
    print("[fig_segment_compare] 4 painéis -> 06_figura_resultado_{a,b,c,d}.pdf")


if __name__ == "__main__":
    main()
