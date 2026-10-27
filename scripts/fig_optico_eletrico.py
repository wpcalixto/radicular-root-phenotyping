#!/usr/bin/env python3
"""
Title:
    Figure: optical-electrical trajectory agreement
File type:
    Script
Purpose:
    Draws per-rhizotron conductivity slopes against occupancy and length slopes
    (16_figura_resultado_*.pdf).
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
    - 16_figura_resultado_a.pdf
    - 16_figura_resultado_b.pdf
    - 16_figura_resultado_legenda.pdf
    - metricas/A2_slopes_by_rizotron.csv
Outputs:
    - printed results only
Dependencies:
    - matplotlib
    - numpy
    - scipy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_optico_eletrico.py (from a workspace prepared with
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
Figura do resultado A2.2 (concordância direcional das trajetórias) — PAINÉIS SEPARADOS:
  16_figura_resultado_a.pdf  inclinação temporal de sigma_a vs inclinação da ocupação (por rizotron)
  16_figura_resultado_b.pdf  inclinação temporal de sigma_a vs inclinação do comprimento
Um ponto por rizotron (n=12), cor por tratamento. Entrada: A2_slopes_by_rizotron.csv.
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
COR = E.COR_TRAT
LAB_T = {"REF": "Reference", "T1": "Treatment 1", "T2": "Treatment 2", "T3": "Treatment 3"}
MARCA = E.MARCA_TRAT
LINHA = E.LINHA_TRAT
USETEX = bool(shutil.which("latex") and shutil.which("dvipng"))
E.aplicar(usetex=USETEX)


PPERM = {"s_O": 0.005, "s_L": 0.005}   # p por permutação bloqueada dentro do tratamento (A2_auditoria)


AREA_MARCA = 95                    # `s` do scatter, em pt^2
FOLGA_X, FOLGA_Y = 0.018, 0.022    # respiro em volta da caixa do rótulo
# direções de tentativa: direita, esquerda, acima, abaixo e as quatro diagonais
DIRECOES = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
ANEIS = (1.0, 1.6, 2.3)            # afastamentos sucessivos, em múltiplos da caixa


def _rotulos_sem_sobreposicao(fig, ax, xs, ys, labs):
    """Posiciona cada rótulo na primeira posição livre de colisão.

    As caixas são medidas no próprio renderizador — não estimadas — e a busca
    percorre oito direções em três afastamentos, testando contra os marcadores
    de todos os pontos e contra as caixas já posicionadas.
    """
    ren = fig.canvas.get_renderer()
    cx_ax = ax.get_window_extent(ren)
    W, H = cx_ax.width, cx_ax.height
    raio = (AREA_MARCA ** 0.5 / 2) * fig.dpi / 72.0     # meio-lado do marcador, em px
    rx, ry = raio / W, raio / H

    tam = []
    for l in labs:
        t = ax.text(0.5, 0.5, l, transform=ax.transAxes, ha="center", va="center")
        e = t.get_window_extent(ren)
        tam.append((e.width / W + FOLGA_X, e.height / H + FOLGA_Y))
        t.remove()

    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    pts = [((x - x0) / (x1 - x0), (y - y0) / (y1 - y0)) for x, y in zip(xs, ys)]
    postas = []                                        # (cx, cy, w, h) já fixados

    def colide(cx, cy, w, h, i):
        if not (w / 2 <= cx <= 1 - w / 2 and h / 2 <= cy <= 1 - h / 2):
            return True
        for j, (px, py) in enumerate(pts):
            if j != i and abs(cx - px) < w / 2 + rx and abs(cy - py) < h / 2 + ry:
                return True
        return any(abs(cx - bx) < (w + bw) / 2 and abs(cy - by) < (h + bh) / 2
                   for bx, by, bw, bh in postas)

    for i, (px, py) in enumerate(pts):
        w, h = tam[i]
        alvo = None
        for k in ANEIS:
            for sx, sy in DIRECOES:
                cx = px + sx * k * (rx + w / 2)
                cy = py + sy * k * (ry + h / 2)
                if not colide(cx, cy, w, h, i):
                    alvo = (cx, cy)
                    break
            if alvo:
                break
        if alvo is None:                               # nenhuma livre: acima e à direita
            alvo = (px + rx + w / 2, py + ry + h)
        postas.append((alvo[0], alvo[1], w, h))
        ax.annotate(labs[i], alvo, xycoords="axes fraction",
                    ha="center", va="center", zorder=4)


def painel(col, scale, ylabel, fname):
    """
    Purpose:
        Draw one slope-versus-slope panel and return the correlation.
    Parameters:
        col: optical slope column
        scale: scale
        ylabel: label
        fname: output file
    Returns:
        tuple
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rows = [r for r in csv.DictReader(open(C.METRICAS / "A2_slopes_by_rizotron.csv")) if r[col]]
    xs = np.array([float(r["s_sigma"]) * 1000 for r in rows])          # mS/m por dia
    ys = np.array([float(r[col]) * scale for r in rows])
    trats = [r["tratamento"] for r in rows]
    labs = [r"$R_{%d}$" % int(r["rizotron"][1:]) for r in rows]
    rho, p = spearmanr(xs, ys)
    fig, ax = plt.subplots(figsize=(6.0, 5.2))
    ax.axhline(0, color="0.7", lw=1.0, ls="--"); ax.axvline(0, color="0.7", lw=1.0, ls="--")
    for t in ("REF", "T1", "T2", "T3"):          # laço por tratamento: marcador próprio
        m = [i for i, tt in enumerate(trats) if tt == t]
        if m:
            ax.scatter(xs[m], ys[m], color=COR[t], marker=MARCA[t], s=95,
                       edgecolor="black", linewidth=0.5, zorder=3, label=LAB_T[t])
    ax.set_xlabel(r"$\sigma_a$ trend [mS m$^{-1}$ day$^{-1}$]"); ax.set_ylabel(ylabel)
    ax.margins(x=0.16, y=0.14)                   # folga para os rótulos junto às bordas
    ax.autoscale_view()                          # limites resolvidos antes de posicionar
    fig.canvas.draw()                            # renderizador pronto para medir as caixas
    _rotulos_sem_sobreposicao(fig, ax, xs, ys, labs)
    return rho, E.finalizar(fig, ax, OUTDIR / fname)


def painel_legenda(fname):
    """Faixa de legenda: item próprio, sem letra, entre os dois painéis."""
    fig, ax = plt.subplots(figsize=(1.9, 2.0))
    for t in ("REF", "T1", "T2", "T3"):
        ax.scatter([], [], color=COR[t], marker=MARCA[t], s=95,
                   edgecolor="black", linewidth=0.5, label=LAB_T[t])
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
    r1, _ = painel("s_O", 1.0, r"Occupancy trend [day$^{-1}$]", "16_figura_resultado_a.pdf")
    painel_legenda("16_figura_resultado_legenda.pdf")
    r2, _ = painel("s_L", 1 / 1000.0, r"Length trend [kpx day$^{-1}$]", "16_figura_resultado_b.pdf")
    print(f"[fig_optico_eletrico] modo={E.modo()}  (rho_O={r1:+.2f}, rho_L={r2:+.2f})")


if __name__ == "__main__":
    main()
