#!/usr/bin/env python3
"""
Title:
    Figure: multimodal availability matrix
File type:
    Script
Purpose:
    Draws the 12 x 7 availability matrix of images and electrical measurements
    (03_figura_resultado.pdf).
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
    - Artigo_revista/03_figura_resultado.pdf
Dependencies:
    - matplotlib
    - numpy
    - local: estilo_figuras
Execution:
    python scripts/fig_disponibilidade.py (from a workspace prepared with
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
Figura principal da subseção "Preparação e controle de qualidade do conjunto de dados".

Matriz de disponibilidade multimodal (12 rizotrons x 7 coletas), 3 categorias:
  - imagem e medição elétrica disponíveis (72 células);
  - somente imagem disponível          (10 células, 7ª coleta);
  - ausência de imagem e elétrica       (2 células: R1 e R12 na 7ª coleta).

Fonte auditável: manifestos/dataset_manifest.csv (colunas I_img, E_elec).
Protocolo de figuras: usetex, serif/Computer Modern, 18 pt, sem título interno.
Saída: Artigo_revista/03_figura_resultado.pdf
"""
import os
import sys
import csv
import shutil

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import estilo_figuras as E
BASE = os.path.dirname(AQUI)                       # Nova_versao/
MANIF = os.path.join(BASE, "manifestos", "dataset_manifest.csv")
OUT = os.path.join(BASE, "Artigo_revista", "03_figura_resultado.pdf")

USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)

# cores fixas das categorias (0 = ausência, 1 = só imagem, 2 = imagem+elétrica)
COR = {0: "#D9D9D9", 1: E.OKABE_ITO["laranja"], 2: E.OKABE_ITO["azul"]}


def carregar_matriz():
    """
    Purpose:
        Load the 12 x 7 availability matrix from the manifest.
    Parameters:
        none
    Returns:
        numpy array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rz = [f"R{i:02d}" for i in range(1, 13)]
    co = [str(k) for k in range(1, 8)]
    M = np.zeros((12, 7), dtype=int)
    for r in csv.DictReader(open(MANIF, encoding="utf-8")):
        i, j = rz.index(r["rhizotron_id"]), co.index(r["collection_id"])
        I, E = int(r["I_img"]), int(r["E_elec"])
        M[i, j] = 2 if (I and E) else (1 if I else 0)
    return M


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
    M = carregar_matriz()                        # (12 rizotrons, 7 coletas)
    Mt = M.T                                      # transposta -> paisagem (7 x 12)
    cmap = ListedColormap([COR[0], COR[1], COR[2]])

    fig, ax = plt.subplots(figsize=(10.0, 5.0))
    ax.imshow(Mt, cmap=cmap, vmin=-0.5, vmax=2.5, aspect="equal")

    # hachuras por categoria (acessível em monocromático): verde e laranja
    # viram cinzas parecidos sem padrão de preenchimento.
    HATCH = {1: "////", 0: "xxx"}
    for rr in range(Mt.shape[0]):
        for cc in range(Mt.shape[1]):
            v = int(Mt[rr, cc])
            if v in HATCH:
                ax.add_patch(Rectangle((cc - 0.5, rr - 0.5), 1, 1, fill=False,
                                       hatch=HATCH[v], edgecolor="black", linewidth=0.0))

    # grade branca entre as células
    ax.set_xticks(np.arange(-0.5, 12, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 7, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2.5)
    ax.tick_params(which="minor", length=0)

    ax.set_xticks(range(12)); ax.set_xticklabels([f"R{i}" for i in range(1, 13)])
    ax.set_yticks(range(7)); ax.set_yticklabels([f"C{k}" for k in range(1, 8)])
    ax.set_xlabel("Rhizotron")
    ax.set_ylabel("Sampling")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    leg = [Patch(facecolor=COR[2], label="Image and electrical measurement"),
           Patch(facecolor=COR[1], hatch="////", label="Image only"),
           Patch(facecolor=COR[0], hatch="xxx", label="No data")]
    ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.5, -0.18),
              ncol=3, frameon=False, handlelength=1.3, handleheight=1.3)

    fig.savefig(OUT, format="pdf", dpi=300)
    plt.close(fig)
    cont = {v: int((M == v).sum()) for v in (2, 1, 0)}
    print(f"[fig_disponibilidade] usetex={USETEX} -> {OUT}")
    print(f"   categorias: img+elétrica={cont[2]}, só imagem={cont[1]}, ausência={cont[0]}")


if __name__ == "__main__":
    main()
