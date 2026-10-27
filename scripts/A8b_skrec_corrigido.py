#!/usr/bin/env python3
"""
Title:
    Corrected skeleton sensitivity
File type:
    Script
Purpose:
    Recomputes skeleton sensitivity without prediction-dependent exclusion of images, with
    stratified bootstrap.
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
    - metricas/A8_prmi_por_imagem.csv
Outputs:
    - metricas/A8b_skrec_corrigido.csv
Dependencies:
    - numpy
    - local: config
Execution:
    python scripts/A8b_skrec_corrigido.py (from a workspace prepared with
    tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Not re-executed in the v1.0.0 verification. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not
    redistributed in these packages.
"""
# Original module notes (Portuguese) are preserved below.
"""
A8b — Sensibilidade de esqueleto recalculada sem exclusão dependente da predição.

Motivação (auditoria): a sensibilidade de esqueleto vinha sendo calculada apenas nos casos
em que os TRÊS métodos produziram esqueleto não vazio, o que descartava 47,4% das imagens.
Como a exclusão depende do desempenho do próprio método, ela favorece o método que falha
com mais frequência: das 6.687 ausências de M2, 349 correspondem a imagens cuja REFERÊNCIA
tem esqueleto e cuja predição foi vazia — casos em que a sensibilidade é zero, e não
indefinida.

Regra corrigida: a métrica é definida em toda imagem cuja REFERÊNCIA produz esqueleto não
vazio; quando a predição é vazia, a sensibilidade vale zero. Imagens com referência vazia
(6.338) permanecem fora, por indefinição legítima.

Incerteza: mesma do agregador canônico — reamostragem agrupada por unidade parental,
estratificada pelos subconjuntos de espécie x configuração de aquisição.

Saída: metricas/A8b_skrec_corrigido.csv
"""
import os
import sys
import csv
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

SRC = C.METRICAS / "A8_prmi_por_imagem.csv"
OUT = C.METRICAS / "A8b_skrec_corrigido.csv"
B = 2000
SEMENTE = 42
TAGS = ("M1", "M2", "M3")


def carregar():
    """
    Purpose:
        Load per-image benchmark rows and validity flags.
    Parameters:
        none
    Returns:
        tuple
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    validas, ref_vazia = [], 0
    for r in rows:
        vazios = [t for t in TAGS if r[f"skrec_{t}"] in ("", "nan")]
        if len(vazios) == 3:            # referência sem esqueleto -> indefinido p/ todos
            ref_vazia += 1
            continue
        validas.append(r)
    return rows, validas, ref_vazia


def por_parent(validas):
    """Média por unidade parental, com predição vazia contando zero."""
    by = defaultdict(lambda: {t: [] for t in TAGS} | {"sp": None})
    for r in validas:
        p = by[r["parent"]]
        p["sp"] = r["especie"]
        for t in TAGS:
            v = r[f"skrec_{t}"]
            p[t].append(0.0 if v in ("", "nan") else float(v))
    return {k: {"sp": d["sp"], **{t: float(np.mean(d[t])) for t in TAGS}} for k, d in by.items()}


def strat_boot(pl, f, rng):
    """
    Purpose:
        Species-stratified bootstrap of a statistic.
    Parameters:
        pl: rows
        f: statistic
        rng: numpy Generator
    Returns:
        tuple
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    por_sp = defaultdict(list)
    for k, d in pl.items():
        por_sp[d["sp"]].append(d)
    est = []
    for _ in range(B):
        vals = []
        for sp, ds in por_sp.items():
            idx = rng.integers(0, len(ds), len(ds))
            vals += [f(ds[i]) for i in idx]
        est.append(np.mean(vals))
    return float(np.percentile(est, 2.5)), float(np.percentile(est, 97.5))


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
    rows, validas, ref_vazia = carregar()
    n_pred_vazia = sum(1 for r in validas for t in TAGS if r[f"skrec_{t}"] in ("", "nan"))
    print(f"[A8b] {len(rows)} imagens | referência sem esqueleto: {ref_vazia} (excluídas)")
    print(f"[A8b] denominador válido: {len(validas)} imagens | predições vazias contadas como zero: {n_pred_vazia}")

    pl = por_parent(validas)
    rng = np.random.default_rng(SEMENTE)
    linhas, medias = [], {}
    print(f"\n  sensibilidade de esqueleto (n={len(validas)} imagens, {len(pl)} unidades parentais):")
    for t in TAGS:
        m = float(np.mean([d[t] for d in pl.values()]))
        lo, hi = strat_boot(pl, lambda d, tt=t: d[tt], rng)
        medias[t] = m
        print("    %s = %.3f [%.3f; %.3f]" % (t, m, lo, hi))
        linhas.append({"tipo": "media", "metodo": t, "valor": round(m, 4),
                       "lo": round(lo, 4), "hi": round(hi, 4),
                       "n_img": len(validas), "n_parent": len(pl)})

    print("\n  contrastes pareados:")
    for a, b in (("M3", "M2"), ("M3", "M1")):
        d = float(np.mean([pl[k][a] - pl[k][b] for k in pl]))
        lo, hi = strat_boot(pl, lambda x, aa=a, bb=b: x[aa] - x[bb], rng)
        print("    %s - %s = %+.4f [%+.4f; %+.4f]" % (a, b, d, lo, hi))
        linhas.append({"tipo": "contraste", "metodo": f"{a}-{b}", "valor": round(d, 4),
                       "lo": round(lo, 4), "hi": round(hi, 4),
                       "n_img": len(validas), "n_parent": len(pl)})

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader(); w.writerows(linhas)
    print(f"\n[A8b] {OUT.name} gravado.")


if __name__ == "__main__":
    main()
