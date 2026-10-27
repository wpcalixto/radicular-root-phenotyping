#!/usr/bin/env python3
"""
Title:
    Supporting Information figures
File type:
    Script
Purpose:
    Draws the Supporting Information figure panels S1-S9 (training curves, PRMI, profiles by
    segmenter, root under reflection, scores per image, rates, electrical trajectories, horizon by
    model, parameters).
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-08-01
Date:
    2026-08-01
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
    - 08D_selecao_por_imagem.csv
    - A8_por_especie.csv
    - A8_prmi_por_imagem.csv
    - S3_legenda.pdf
    - S6_legenda.pdf
    - S7_legenda.pdf
    - S8_legenda.pdf
    - combinado_limpo_parameters.csv
    - deflash_root_overlap.csv
    - electrical_features_by_rhizotron.csv
    - external_training_log.csv
    - frangi_parameters.csv
    - model_horizon.csv
    - root_density_by_layer.csv
    - root_density_by_layer_M1.csv
    - root_density_by_layer_M2.csv
    - temporal_rates.csv
Outputs:
    - S2_a.pdf
    - S2_b.pdf
    - S4_a.pdf
    - S4_b.pdf
    - S4_c.pdf
    - S5_a.pdf
    - S5_b.pdf
    - S7_a.pdf
    - S7_b.pdf
    - S9_a.pdf
    - S9_b.pdf
    - S9_c.pdf
Dependencies:
    - matplotlib
    - numpy
    - local: config, estilo_figuras
Execution:
    python scripts/fig_si.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated
    PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only
    by PDF metadata). Environment of the verification: Python 3.9.6 (macOS) with the versions listed
    in requirements.txt.
Warnings:
    Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not
    redistributed in these packages.
"""
# Original module notes (Portuguese) are preserved below.
"""
Figuras do Supporting Information, sob o protocolo de figuras do artigo.

Regra 4: UM ARQUIVO POR PAINEL. A montagem multi-painel é feita no .tex com
\\subfigure. Saidas: Artigo_revista/S<n>_<letra>.pdf
Regra 5: legenda apenas no primeiro painel de cada conjunto.
Regras 1, 2, 3, 6, 9, 10, 11, 12: delegadas a estilo_figuras.aplicar/finalizar.
Regras 7 e 8: cor e marcador vindos dos dicionarios de estilo_figuras.
"""
import os
import sys
import csv
import shutil
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

OUT = C.ROOT / "Artigo_revista"
E.aplicar(usetex=bool(shutil.which("latex") and shutil.which("dvipng")))

FIGSIZE = (4.6, 3.6)          # identico em todos os paineis
MS = 6                        # tamanho de marcador
LW = 1.8

LAB_MET = {"M1": "M1", "M2": "M2", "M3": "M3"}
LAB_T = {"REF": "Reference", "T1": "Treatment 1", "T2": "Treatment 2", "T3": "Treatment 3"}
ORD_T = ["REF", "T1", "T2", "T3"]


def rd(nome):
    """
    Purpose:
        Read a metrics CSV.
    Parameters:
        nome: file name
    Returns:
        list of dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return list(csv.DictReader(open(C.METRICAS / nome, encoding="utf-8")))


def f(v):
    """
    Purpose:
        Convert a CSV field to float, returning None when conversion fails.
    Parameters:
        v: value read from a CSV field
    Returns:
        float or None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def novo():
    """
    Purpose:
        Create a figure with the SI size.
    Parameters:
        none
    Returns:
        tuple (fig, ax)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return plt.subplots(figsize=FIGSIZE)


def grava(fig, ax, nome):
    """
    Purpose:
        Finalise and write one SI panel.
    Parameters:
        fig, ax: figure and axes
        nome: output file
    Returns:
        path or None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    escrito = E.finalizar(fig, ax, OUT / nome)
    print("  [%s] %s" % (E.modo(), escrito.split("Artigo_revista/")[-1]))


def faixa_legenda(nome, itens, larg=1.9):
    """Legenda como item próprio, sem letra, para painéis que a compartilham.

    `itens` é uma lista de (rótulo, kwargs de plot); a faixa entra no .tex entre
    os painéis, no lugar da legenda que antes ficava dentro do quadro.
    """
    fig, ax = plt.subplots(figsize=(larg, 2.0))
    for rot, kw in itens:
        ax.plot([], [], label=rot, **kw)
    ax.legend(loc="center", frameon=False, handletextpad=0.6,
              labelspacing=1.0, borderpad=0.0)
    ax.set_axis_off()
    grava(fig, ax, nome)


def faixa_legenda_linha(nome, itens, larg=13.0, ncol=None):
    """Legenda em uma única linha, para entrar acima de uma fila de painéis."""
    fig, ax = plt.subplots(figsize=(larg, 0.55))
    for rot, kw in itens:
        ax.plot([], [], label=rot, **kw)
    ax.legend(loc="center", frameon=False, ncol=ncol or len(itens),
              handletextpad=0.6, columnspacing=2.0, borderpad=0.0)
    ax.set_axis_off()
    grava(fig, ax, nome)


def itens_algoritmo(mods):
    """
    Purpose:
        Legend items for algorithms.
    Parameters:
        mods: algorithm names
    Returns:
        list
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return [(E.LAB_ALGO[m], dict(color=E.COR_ALGO[m], ls=E.LINHA_ALGO[m],
                                 marker=E.MARCA_ALGO[m], ms=MS,
                                 lw=2.2 if m == "baseline" else LW)) for m in mods]


def itens_tratamento():
    """
    Purpose:
        Legend items for treatments.
    Parameters:
        none
    Returns:
        list
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return [(LAB_T[t], dict(color=E.COR_TRAT[t], ls=E.LINHA_TRAT[t],
                            marker=E.MARCA_TRAT[t], ms=MS, lw=LW)) for t in ORD_T]


# ---------------------------------------------------------------- S1
def s1_treinamento():
    """
    Purpose:
        Draw Figure S1 training curves.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    r = rd("external_training_log.csv")
    for letra, fase in (("a", "dev"), ("b", "final")):
        rr = [x for x in r if x["fase"] == fase]
        ep = [int(x["epoca"]) for x in rr]
        fig, ax = novo()
        ax.plot(ep, [f(x["dice_tr"]) for x in rr], color=E.COR_MET["M3"],
                ls=E.LINHA_MET["M3"], marker=E.MARCA_MET["M3"], ms=MS, lw=LW,
                label="Training")
        vv = [(e, f(x["dice_val"])) for e, x in zip(ep, rr) if f(x["dice_val"]) is not None]
        if vv:
            ax.plot([a for a, _ in vv], [b for _, b in vv], color=E.COR_MET["M1"],
                    ls=E.LINHA_MET["M1"], marker=E.MARCA_MET["M1"], ms=MS, lw=LW,
                    label="Validation")
            be, bv = max(vv, key=lambda t: t[1])
            ax.scatter([be], [bv], s=220, facecolor="none", edgecolor=E.NEUTRO, lw=1.6,
                       zorder=5)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Dice")
        ax.set_xlim(0, 26)
        E.legenda_primeiro_painel(ax, letra, loc="lower right")
        grava(fig, ax, "S1_%s.pdf" % letra)


# ---------------------------------------------------------------- S2
def s2_prmi():
    """
    Purpose:
        Draw Figure S2 PRMI panels.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    r = rd("A8_prmi_por_imagem.csv")
    fig, ax = novo()
    for m in ("M1", "M2", "M3"):
        v = np.sort([x for x in (f(t["dice_" + m]) for t in r) if x is not None])
        ax.plot(v, np.linspace(0, 1, len(v)), color=E.COR_MET[m], ls=E.LINHA_MET[m],
                lw=LW, label=LAB_MET[m])
    ax.set_xlabel(E.rotulo("Dice per image"))
    ax.set_ylabel("Cumulative fraction")
    ax.set_xlim(0, 1)
    E.legenda_primeiro_painel(ax, "a", loc="lower right")
    grava(fig, ax, "S2_a.pdf")

    e = rd("A8_por_especie.csv")
    nomes = [x["especie"].split("_")[0] for x in e]
    idx = np.arange(len(e)); w = 0.27
    fig, ax = novo()
    for k, m in enumerate(("M1", "M2", "M3")):
        ax.bar(idx + (k - 1) * w, [f(x["dice_" + m]) for x in e], w, color=E.COR_MET[m],
               hatch=E.HACHURA_MET[m], edgecolor=E.NEUTRO, linewidth=0.6)
    ax.set_xticks(idx)
    ax.set_xticklabels(nomes, rotation=45, ha="right")
    ax.set_ylabel("Dice")
    grava(fig, ax, "S2_b.pdf")


# ---------------------------------------------------------------- S3
def s3_perfil():
    """
    Purpose:
        Draw Figure S3 profiles by segmenter.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    for letra, (m, arq) in zip("abc", (("M1", "root_density_by_layer_M1.csv"),
                                       ("M2", "root_density_by_layer_M2.csv"),
                                       ("M3", "root_density_by_layer.csv"))):
        r = rd(arq)
        por = defaultdict(lambda: defaultdict(list))
        for x in r:
            v = f(x["rho_area_valida"])
            if v is not None:
                por[x["tratamento"]][int(x["faixa"])].append(100 * v)
        fig, ax = novo()
        for t in ORD_T:
            if t not in por:
                continue
            fx = sorted(por[t])
            ax.plot([np.mean(por[t][i]) for i in fx], [(i - 0.5) / len(fx) for i in fx],
                    color=E.COR_TRAT[t], ls=E.LINHA_TRAT[t], marker=E.MARCA_TRAT[t],
                    ms=MS, lw=LW, label=LAB_T[t])
        ax.set_xlabel(E.rotulo("Root density", r"\% of valid area"))
        ax.set_ylabel(E.rotulo("Normalized depth", "0--1"))
        ax.invert_yaxis()
        grava(fig, ax, "S3_%s.pdf" % letra)
    faixa_legenda_linha("S3_legenda.pdf", itens_tratamento())


# ---------------------------------------------------------------- S4
def s4_raiz_sob_reflexo():
    """
    Purpose:
        Draw Figure S4 root under reflection panels.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    r = rd("deflash_root_overlap.csv")
    frac = [f(x["frac_root_in_mask_pct"]) for x in r]
    raz = [f(x["razao_in_out"]) for x in r]
    ip = [f(x["inpaint_pct"]) for x in r]

    fig, ax = novo()
    ax.hist(frac, bins=18, color=E.COR_MET["M3"], edgecolor=E.NEUTRO, linewidth=0.6)
    ax.axvline(np.median(frac), color=E.NEUTRO, ls="--", lw=LW)
    ax.set_xlabel(E.rotulo("Root pixels inside reconstruction", r"\%"))
    ax.set_ylabel("Images")
    grava(fig, ax, "S4_a.pdf")

    fig, ax = novo()
    ax.hist(raz, bins=18, color=E.COR_MET["M1"], edgecolor=E.NEUTRO, linewidth=0.6)
    ax.axvline(np.median(raz), color=E.NEUTRO, ls="--", lw=LW)
    ax.set_xlabel("Density ratio, inside / outside")
    ax.set_ylabel("Images")
    grava(fig, ax, "S4_b.pdf")

    fig, ax = novo()
    ax.scatter(ip, raz, s=60, color=E.COR_MET["M2"], edgecolor=E.NEUTRO, linewidth=0.5)
    ax.set_xlabel(E.rotulo("Reconstructed fraction", r"\% of frame"))
    ax.set_ylabel("Density ratio, inside / outside")
    grava(fig, ax, "S4_c.pdf")


# ---------------------------------------------------------------- S5
def s5_notas():
    """
    Purpose:
        Draw Figure S5 scores per image.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    r = rd("08D_selecao_por_imagem.csv")
    rng = np.random.default_rng(42)
    fig, ax = novo()
    for k, m in enumerate(("M1", "M2", "M3")):
        v = np.array([f(x[m]) for x in r])
        ax.scatter(np.full(len(v), k) + rng.uniform(-0.16, 0.16, len(v)), v, s=34,
                   color=E.COR_MET[m], alpha=0.7, edgecolor="none")
        ax.hlines(np.median(v), k - 0.3, k + 0.3, color=E.NEUTRO, lw=2.2)
    ax.set_xticks(range(3)); ax.set_xticklabels([LAB_MET[m] for m in ("M1", "M2", "M3")])
    ax.set_ylabel(E.rotulo("Mean score per image", "0--4"))
    grava(fig, ax, "S5_a.pdf")

    win = defaultdict(int)
    for x in r:
        win[x["vencedor"]] += 1
    met = [m for m in ("M1", "M2", "M3") if m in win]
    fig, ax = novo()
    ax.bar([LAB_MET[m] for m in met], [win[m] for m in met],
           color=[E.COR_MET[m] for m in met], hatch=[E.HACHURA_MET[m] for m in met],
           edgecolor=E.NEUTRO, linewidth=0.6)
    ax.set_ylabel("Images with highest score")
    grava(fig, ax, "S5_b.pdf")


# ---------------------------------------------------------------- S6
def s6_taxas():
    """
    Purpose:
        Draw Figure S6 growth rates.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    r = rd("temporal_rates.csv")
    cfg = (("a", "O_ocupacao", ("Occupancy growth\nrate", r"pp day$^{-1}$"), 100.0),
           ("b", "L_skel_px", ("Length growth\nrate", r"px day$^{-1}$"), 1.0))
    for letra, var, (nome, uni), esc in cfg:
        por = defaultdict(lambda: defaultdict(list))
        for x in r:
            if x["variavel"] != var:
                continue
            g = f(x["G_taxa"])
            if g is None:
                continue
            por[x["tratamento"]][(f(x["DAP_ini"]) + f(x["DAP_fim"])) / 2.0].append(g * esc)
        fig, ax = novo()
        for t in ORD_T:
            if t not in por:
                continue
            xs = sorted(por[t])
            ax.plot(xs, [np.mean(por[t][d]) for d in xs], color=E.COR_TRAT[t],
                    ls=E.LINHA_TRAT[t], marker=E.MARCA_TRAT[t], ms=MS, lw=LW,
                    label=LAB_T[t])
        ax.set_xlabel(E.rotulo("Days after planting", "DAP"))
        ax.set_ylabel(E.rotulo(nome, uni))
        grava(fig, ax, "S6_%s.pdf" % letra)
    faixa_legenda("S6_legenda.pdf", itens_tratamento())


# ---------------------------------------------------------------- S7
def s7_eletrica():
    """
    Purpose:
        Draw Figure S7 electrical trajectories.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    r = rd("electrical_features_by_rhizotron.csv")
    por = defaultdict(list)
    for x in r:
        s, d = f(x["sigma_a"]), f(x["DAP"])
        if s is not None and d is not None:
            por[x["rhizotron_id"]].append((d, s * 1000, x["tratamento"]))
    fig, ax = novo()
    vistos = set()
    for riz in sorted(por):
        p = sorted(por[riz]); t = p[0][2]
        lab = LAB_T[t] if t not in vistos else None
        vistos.add(t)
        ax.plot([a for a, _, _ in p], [b for _, b, _ in p], color=E.COR_TRAT[t],
                ls=E.LINHA_TRAT[t], marker=E.MARCA_TRAT[t], ms=MS - 1, lw=1.3, label=lab)
    ax.set_xlabel(E.rotulo("Days after planting", "DAP"))
    ax.set_ylabel(E.rotulo("Apparent conductivity\n" r"$\sigma_a$", r"mS m$^{-1}$"))
    grava(fig, ax, "S7_a.pdf")
    faixa_legenda("S7_legenda.pdf", itens_tratamento())

    ai = [f(x["a_implied_planilha_m"]) for x in r if f(x["a_implied_planilha_m"]) is not None]
    fig, ax = novo()
    ax.hist(ai, bins=16, color=E.COR_FONTE["electrical"], edgecolor=E.NEUTRO, linewidth=0.6)
    ax.axvline(0.16, color=E.NEUTRO, ls="-", lw=2.2)
    ax.axvline(np.median(ai), color=E.NEUTRO, ls="--", lw=LW)
    ax.set_xlabel(E.rotulo("Implied electrode spacing $a$", "m"))
    ax.set_ylabel("Readings")
    grava(fig, ax, "S7_b.pdf")


# ---------------------------------------------------------------- S8
def s8_horizonte():
    """
    Purpose:
        Draw Figure S8 horizon by model.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    r = rd("model_horizon.csv")
    alvos = (("a", "y_M_r", ("LORO MAE", "g")),
             ("b", "y_M_a", ("LORO MAE", "g")),
             ("c", "y_R_ar", ("LORO MAE", None)))
    mods = ["baseline_media", "Ridge", "Lasso", "PLS", "RandomForest", "SVR"]
    for letra, al, (nome, uni) in alvos:
        fig, ax = novo()
        for m in mods:
            k = "baseline" if m == "baseline_media" else m
            p = sorted([(int(x["horizonte_h"]), f(x["E_h_MAE"]))
                        for x in r if x["alvo"] == al and x["modelo"] == m])
            if not p:
                continue
            ax.plot([a for a, _ in p], [b for _, b in p], color=E.COR_ALGO[k],
                    ls=E.LINHA_ALGO[k], marker=E.MARCA_ALGO[k], ms=MS,
                    lw=2.2 if k == "baseline" else LW, label=E.LAB_ALGO[k])
        ax.set_xlabel(r"Horizon $h$")
        ax.set_ylabel(E.rotulo(nome, uni))
        grava(fig, ax, "S8_%s.pdf" % letra)
    faixa_legenda_linha("S8_legenda.pdf",
                        itens_algoritmo(["baseline" if m == "baseline_media" else m
                                         for m in mods]))


# ---------------------------------------------------------------- S9
def s9_parametros():
    """
    Purpose:
        Draw Figure S9 parameter diagnostics.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    cl = rd("combinado_limpo_parameters.csv")
    fr = rd("frangi_parameters.csv")

    fig, ax = novo()          # painel (a): unico com series -> leva a legenda
    for col, m in (("m1_frangi_pct", "M1"), ("m2_ext_pct", "M2"), ("m3_limpo_pct", "M3")):
        v = np.sort([f(x[col]) for x in cl])
        ax.plot(v, np.linspace(0, 1, len(v)), color=E.COR_MET[m], ls=E.LINHA_MET[m],
                lw=LW, label=LAB_MET[m])
    ax.set_xlabel(E.rotulo("Mask area", r"\% of frame"))
    ax.set_ylabel("Cumulative fraction")
    E.legenda_primeiro_painel(ax, "a", loc="lower right")
    grava(fig, ax, "S9_a.pdf")

    t = [f(x["threshold_T"]) for x in fr]
    fig, ax = novo()
    ax.hist(t, bins=18, color=E.COR_MET["M1"], edgecolor=E.NEUTRO, linewidth=0.6)
    ax.axvline(np.median(t), color=E.NEUTRO, ls="--", lw=LW)
    ax.set_xlabel(r"Adaptive threshold $\tau_V(I)$")
    ax.set_ylabel("Images")
    grava(fig, ax, "S9_b.pdf")

    a = [f(x["n_comp_m3"]) for x in cl]
    b = [f(x["n_comp_m3_limpo"]) for x in cl]
    fig, ax = novo()
    ax.scatter(a, b, s=60, color=E.COR_MET["M3"], edgecolor=E.NEUTRO, linewidth=0.5)
    lo, hi = min(a + b), max(a + b)
    ax.plot([lo, hi], [lo, hi], ls="--", color=E.NEUTRO, lw=1.4)
    ax.set_xlabel("Components before refinement")
    ax.set_ylabel("Components after refinement")
    grava(fig, ax, "S9_c.pdf")


if __name__ == "__main__":
    print("[fig_si] paineis do Supporting Information (um arquivo por painel)")
    for fn in (s1_treinamento, s2_prmi, s3_perfil, s4_raiz_sob_reflexo, s5_notas,
               s6_taxas, s7_eletrica, s8_horizonte, s9_parametros):
        try:
            fn()
        except Exception as exc:
            print("  !! %s falhou: %s" % (fn.__name__, exc))
