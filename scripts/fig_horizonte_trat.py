#!/usr/bin/env python3
"""
Title:
    Figure: horizon ratio to treatment reference
File type:
    Script
Purpose:
    Draws the MAE ratio to the treatment reference by horizon for root and shoot mass
    (17_figura_resultado_*.pdf).
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
    - 17_figura_resultado_a.pdf
    - 17_figura_resultado_b.pdf
    - 17_figura_resultado_legenda.pdf
    - metricas/A3_horizonte.csv
Outputs:
    - printed results only
Dependencies:
    - matplotlib
    - local: config, estilo_figuras
Execution:
    python scripts/fig_horizonte_trat.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura A3 (complementar) — razão MAE_modelo,h / MAE_referência-tratamento por horizonte:
  17_figura_resultado_a.pdf  massa das raízes (M_R)
  17_figura_resultado_b.pdf  massa da parte aérea (M_PA)
Razão <1 = supera a referência que já conhece o tratamento. Entrada: A3_horizonte.csv.
"""
import os, sys, csv, shutil
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

OUTDIR = C.ROOT / "Artigo_revista"
COR = {"óptica": E.COR_FONTE["optical"], "elétrica": E.COR_FONTE["electrical"],
       "óptica+elétrica": E.COR_FONTE["optical + electrical"], "completo": E.COR_FONTE["full"]}
MARCA = {"óptica": E.MARCA_FONTE["optical"], "elétrica": E.MARCA_FONTE["electrical"],
         "óptica+elétrica": E.MARCA_FONTE["optical + electrical"], "completo": E.MARCA_FONTE["full"]}
LINHA = {"óptica": E.LINHA_FONTE["optical"], "elétrica": E.LINHA_FONTE["electrical"],
         "óptica+elétrica": E.LINHA_FONTE["optical + electrical"], "completo": E.LINHA_FONTE["full"]}
LAB = {"óptica": "optical", "elétrica": "electrical", "óptica+elétrica": "optical+electrical", "completo": "full"}
USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)


def painel(nome, titulo, fname):
    """
    Purpose:
        Draw one horizon-ratio panel.
    Parameters:
        nome: outcome
        titulo: label
        fname: output file
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rows = [r for r in csv.DictReader(open(C.METRICAS / "A3_horizonte.csv")) if r["alvo"] == nome]
    by = defaultdict(list)
    for r in rows:
        by[r["config"]].append((int(r["h"]), float(r["razao"])))
    fig, ax = plt.subplots(figsize=(6.2, 5.0))
    ax.axhline(1.0, color="black", ls="--", lw=1.2)
    for cfg in ["óptica", "elétrica", "óptica+elétrica", "completo"]:
        pts = sorted(by[cfg])
        ax.plot([p[0] for p in pts], [p[1] for p in pts], marker=MARCA[cfg], markersize=7,
                color=COR[cfg], ls=LINHA[cfg], lw=2, label=LAB[cfg])
    ax.set_xlabel(r"Horizon $h$ (collections C1--C$h$)")
    ax.set_ylabel("LORO MAE / treatment-reference MAE")
    return E.finalizar(fig, ax, OUTDIR / fname)


def painel_legenda(fname):
    """Faixa de legenda: item próprio, sem letra, entre os dois painéis."""
    fig, ax = plt.subplots(figsize=(2.7, 2.0))
    for cfg in ["óptica", "elétrica", "óptica+elétrica", "completo"]:
        ax.plot([], [], marker=MARCA[cfg], markersize=7, color=COR[cfg],
                ls=LINHA[cfg], lw=2, label=LAB[cfg])
    ax.plot([], [], color="black", ls="--", lw=1.2, label="treatment reference")
    ax.legend(loc="center", frameon=False, handletextpad=0.6,
              labelspacing=1.0, borderpad=0.0)
    ax.set_axis_off()
    return E.finalizar(fig, ax, OUTDIR / fname)


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
    painel("M_R", "root mass", "17_figura_resultado_a.pdf")
    painel_legenda("17_figura_resultado_legenda.pdf")
    painel("M_PA", "shoot mass", "17_figura_resultado_b.pdf")
    print(f"[fig_horizonte_trat] modo={E.modo()}")


if __name__ == "__main__":
    main()
