#!/usr/bin/env python3
"""
Title:
    Figure: MAE by horizon
File type:
    Script
Purpose:
    Draws leave-one-rhizotron-out MAE by horizon and outcome against the mean baseline
    (12_figura_resultado_a.pdf).
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
    - metricas/model_performance.csv
Outputs:
    - 12_figura_resultado_a.pdf
Dependencies:
    - matplotlib
    - local: config, estilo_figuras
Execution:
    python scripts/fig_horizon.py (from a workspace prepared with tools/prepare_workspace.py)
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
Figura do Bloco E (predição por horizonte) — PAINEL ÚNICO (1 PDF; sem título dentro):
  12_figura_resultado_a.pdf  MAE LORO em função do horizonte h (coletas C1..h), por alvo,
                             com a linha de referência (predição pela média).
Entrada: model_performance.csv (melhor modelo por alvo).
"""
import os
import sys
import csv
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

OUTDIR = C.ROOT / "Artigo_revista"
# melhor modelo por alvo (menor MAE observado, horizonte completo) — ver Tabela de modelagem
BEST = {"y_M_r": ("Lasso", "M_R"), "y_M_a": ("SVR", "M_PA"), "y_R_ar": ("Lasso", "Q")}

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
    mp = list(csv.DictReader(open(C.METRICAS / "model_performance.csv")))
    # mesma figsize dos painéis (a) e (b): no .tex os três entram com a mesma
    # largura, e figuras-fonte de larguras diferentes dariam corpos de letra
    # diferentes na mesma fila (regra 9)
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    for alvo, (modelo, chave) in BEST.items():
        pts = sorted([(int(r["horizonte_h"]), float(r["MAE"])) for r in mp
                      if r["alvo"] == alvo and r["modelo"] == modelo])
        base = sorted([(int(r["horizonte_h"]), float(r["MAE"])) for r in mp
                       if r["alvo"] == alvo and r["modelo"] == "baseline_media"])
        # normaliza pela referência (MAE relativo) p/ alvos comparáveis na mesma escala
        h = [p[0] for p in pts]
        rel = [p[1] / b[1] for p, b in zip(pts, base)]
        ax.plot(h, rel, marker=E.MARCA_ALVO[chave], markersize=8,
                color=E.COR_ALVO[chave], ls=E.LINHA_ALVO[chave], linewidth=2,
                label=E.LAB_ALVO[chave])
    ax.axhline(1.0, color="black", ls="--", lw=1.2)
    ax.set_xlabel("Horizon $h$ (collections C1--C$h$)")
    ax.set_ylabel("LORO MAE / reference MAE")
    E.finalizar(fig, ax, OUTDIR / "12_figura_resultado_a.pdf")
    print("[fig_horizon] modo=%s" % E.modo())


if __name__ == "__main__":
    main()
