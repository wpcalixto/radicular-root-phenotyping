#!/usr/bin/env python3
"""
Title:
    Figure: M3 refinement example
File type:
    Script
Purpose:
    Writes conditioned image, raw M3, removed components and refined M3 panels
    (08_figura_resultado_*.pdf).
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
    - 08_figura_resultado_a.pdf
    - 08_figura_resultado_b.pdf
    - 08_figura_resultado_c.pdf
    - 08_figura_resultado_d.pdf
Dependencies:
    - PIL
    - cv2
    - matplotlib
    - numpy
    - local: config
Execution:
    python scripts/fig_m3_refino.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura do Bloco C (refinamento M3) — PAINÉIS SEPARADOS (1 PDF por painel, \\subfigure;
SEM rótulo dentro da imagem). Raízes em verde; removidos em vermelho.
  08_figura_resultado_a.pdf  imagem condicionada
  08_figura_resultado_b.pdf  M3 bruto (M1 ∪ M2)
  08_figura_resultado_c.pdf  componentes removidos
  08_figura_resultado_d.pdf  M3-limpo
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
M3P = BASE / "08_combinado" / "masks" / IMG
M3LP = BASE / "08_combinado_limpo" / "masks" / IMG
OUTDIR = C.ROOT / "Artigo_revista"

plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                     "figure.dpi": 300, "savefig.dpi": 300})


def save_panel(fname, rgb, mask=None, cor=(0.15, 0.85, 0.15)):
    """
    Purpose:
        Write one mask panel over the image.
    Parameters:
        fname: output file
        rgb: image
        mask: mask
        cor: colour
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    img = rgb.copy()
    if mask is not None:
        img[mask] = cor
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
    m3 = np.asarray(Image.open(M3P).convert("L")) > 127
    m3l = np.asarray(Image.open(M3LP).convert("L")) > 127
    if m3l.shape != m3.shape:
        import cv2
        m3l = cv2.resize(m3l.astype(np.uint8), (m3.shape[1], m3.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
    removed = m3 & ~m3l
    save_panel("08_figura_resultado_a.pdf", rgb)
    save_panel("08_figura_resultado_b.pdf", rgb, m3)
    save_panel("08_figura_resultado_c.pdf", rgb, removed, cor=(0.90, 0.10, 0.10))
    save_panel("08_figura_resultado_d.pdf", rgb, m3l)
    print(f"[fig_m3_refino] 4 painéis (removidos={int(removed.sum())}px) -> 08_figura_resultado_{{a,b,c,d}}.pdf")


if __name__ == "__main__":
    main()
