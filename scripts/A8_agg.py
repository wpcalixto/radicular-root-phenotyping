#!/usr/bin/env python3
"""
Title:
    Aggregation of the PRMI benchmark
File type:
    Script
Purpose:
    Aggregates per-image PRMI benchmark metrics on complete cases with parental-unit clustered and
    species-stratified bootstrap.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-14
Date:
    2026-07-14
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
    - metricas/A8_por_especie.csv
    - metricas/A8_prmi_resumo.csv
Dependencies:
    - numpy
    - local: config
Execution:
    python scripts/A8_agg.py (from a workspace prepared with tools/prepare_workspace.py)
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
A8 — agregação do benchmark PRMI completo. Para cada métrica usa CASOS COMPLETOS (imagens em que
M1, M2 e M3 têm valor válido) de modo que média marginal e diferença pareada compartilhem o mesmo
conjunto (garante mean(M3)−mean(M2)=mean(M3−M2)). Bootstrap CLUSTERIZADO por unidade parental
(espécie_T###_L###) e ESTRATIFICADO por espécie. Saídas: metricas/A8_prmi_resumo.csv +
metricas/A8_por_especie.csv + impressão.
"""
import sys, os, csv
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

RNG = np.random.default_rng(42); NBOOT = 5000
METS = ["dice", "iou", "prec", "rec", "spec", "cldice", "skprec", "skrec"]


def parent_level(rows, met):
    """dict parent -> {sp, M1, M2, M3} = médias por parent em CASOS COMPLETOS da métrica."""
    by = defaultdict(lambda: {"M1": [], "M2": [], "M3": [], "sp": None})
    for r in rows:
        vals = {t: r[f"{met}_{t}"] for t in ("M1", "M2", "M3")}
        if any(v == "" for v in vals.values()):
            continue
        p = by[r["parent"]]; p["sp"] = r["especie"]
        for t in ("M1", "M2", "M3"): p[t].append(float(vals[t]))
    out = {}
    n_img = 0
    for parent, d in by.items():
        if d["M1"]:
            out[parent] = {"sp": d["sp"], "M1": np.mean(d["M1"]), "M2": np.mean(d["M2"]), "M3": np.mean(d["M3"])}
            n_img += len(d["M1"])
    return out, n_img


def strat_boot(pl, func):
    """Média + IC95% por bootstrap de parents ESTRATIFICADO por espécie."""
    by_sp = defaultdict(list)
    for d in pl.values():
        by_sp[d["sp"]].append(func(d))
    allv = np.array([v for vs in by_sp.values() for v in vs])
    arrs = {sp: np.array(vs) for sp, vs in by_sp.items()}
    boots = np.empty(NBOOT)
    for b in range(NBOOT):
        boots[b] = np.concatenate([a[RNG.integers(0, len(a), len(a))] for a in arrs.values()]).mean()
    return float(allv.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)), len(allv)


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
    rows = list(csv.DictReader(open(C.METRICAS / "A8_prmi_por_imagem.csv", encoding="utf-8")))
    n_parent = len({r["parent"] for r in rows}); n_sp = len({r["especie"] for r in rows})
    print(f"[A8-agg] {len(rows)} imagens | {n_parent} unidades parentais | {n_sp} espécies")

    out = []
    print("\n[A8] Médias por método [IC95% cluster+estratificado] (casos completos):")
    pls = {}
    for met in METS:
        pl, n_img = parent_level(rows, met); pls[met] = pl
        line = f"   {met:7s} (nI={n_img:5d}, nP={len(pl):4d})"
        for tag in ("M1", "M2", "M3"):
            m, lo, hi, _ = strat_boot(pl, lambda d, t=tag: d[t])
            line += f" | {tag}={m:.3f}[{lo:.3f},{hi:.3f}]"
            out.append({"tipo": "media", "metrica": met, "metodo": tag, "n_img": n_img, "n_parent": len(pl),
                        "valor": round(m, 4), "lo": round(lo, 4), "hi": round(hi, 4)})
        print(line)
    print("\n[A8] Diferença pareada [IC95% cluster+estratificado] (mesmos casos completos):")
    for met in ["dice", "iou", "prec", "rec", "spec", "cldice", "skrec"]:
        pl = pls[met]
        for b in ("M2", "M1"):
            m, lo, hi, _ = strat_boot(pl, lambda d, bb=b: d["M3"] - d[bb])
            star = "*" if (lo > 0 or hi < 0) else ""
            print(f"   Δ{met:7s} M3−{b} = {m:+.4f} [{lo:+.4f},{hi:+.4f}] {star}")
            out.append({"tipo": "diff", "metrica": f"{met}_M3-{b}", "metodo": "diff",
                        "n_img": "", "n_parent": len(pl), "valor": round(m, 4), "lo": round(lo, 4), "hi": round(hi, 4)})
    with open(C.METRICAS / "A8_prmi_resumo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["tipo", "metrica", "metodo", "n_img", "n_parent", "valor", "lo", "hi"])
        w.writeheader(); w.writerows(out)

    # tabela por espécie (Dice/prec/rec por método + ΔDice M3−M2), no conjunto completo de Dice
    pl = pls["dice"]; by_sp = defaultdict(list)
    for d in pl.values(): by_sp[d["sp"]].append(d)
    esp_rows = []
    print("\n[A8] Por espécie (Dice; casos completos de Dice):")
    print(f"   {'espécie':26s} nP   DiceM1 DiceM2 DiceM3  ΔDice(M3-M2)")
    for sp in sorted(by_sp):
        ds = by_sp[sp]
        d1 = np.mean([d["M1"] for d in ds]); d2 = np.mean([d["M2"] for d in ds]); d3 = np.mean([d["M3"] for d in ds])
        # prec/rec por espécie (casos completos de prec/rec = todas)
        plp = pls["prec"]; plr = pls["rec"]
        p2 = np.mean([v["M2"] for v in plp.values() if v["sp"] == sp]); p3 = np.mean([v["M3"] for v in plp.values() if v["sp"] == sp])
        r2 = np.mean([v["M2"] for v in plr.values() if v["sp"] == sp]); r3 = np.mean([v["M3"] for v in plr.values() if v["sp"] == sp])
        esp_rows.append({"especie": sp, "n_parent": len(ds),
                         "dice_M1": round(d1, 3), "dice_M2": round(d2, 3), "dice_M3": round(d3, 3),
                         "prec_M2": round(p2, 3), "prec_M3": round(p3, 3), "rec_M2": round(r2, 3), "rec_M3": round(r3, 3),
                         "dDice_M3_M2": round(d3 - d2, 3)})
        print(f"   {sp:26s} {len(ds):3d}  {d1:.3f}  {d2:.3f}  {d3:.3f}   {d3-d2:+.3f}")
    with open(C.METRICAS / "A8_por_especie.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(esp_rows[0].keys())); w.writeheader(); w.writerows(esp_rows)
    print(f"\n[A8-agg] -> A8_prmi_resumo.csv + A8_por_especie.csv")


if __name__ == "__main__":
    main()
