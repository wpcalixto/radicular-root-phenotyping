#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    Interval for the mixed-model beta
File type:
    Script
Purpose:
    Computes the rhizotron-clustered bootstrap interval of the standardised beta of the A2.3 mixed
    model.
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
    - metricas/A16_ic_beta_misto.csv
    - metricas/multimodal_long.csv
Outputs:
    - printed results only
Dependencies:
    - numpy
    - pandas
    - statsmodels
    - local: config
Execution:
    python scripts/A16b_ic_beta_misto.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Verification in v1.0.0: re-executed in an isolated workspace built
    from the Dataset; outputs byte-identical to the archived versions. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""IC95% do beta do modelo misto A2.3, por bootstrap agrupado no rizotron.

Reamostra os MESMOS dados e reajusta o MESMO modelo usado em A2_optico_eletrico.py:
    Y ~ sig_w + DAP + C(trat),  grupos = rizotron
com sig_w = sigma_a centrada dentro do proprio rizotron. Os coeficientes sao
padronizados a posteriori (beta * sd(sig_w)/sd(Y)) para ficarem comparaveis entre
descritores, como na tabela do artigo.
"""
import os, sys, csv, warnings
from collections import defaultdict
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
sys.path.insert(0, "scripts")
import config as C

LONG = C.METRICAS / "multimodal_long.csv"
OPT = {"O_ocupacao": "O", "L_skel_px": "L_skel", "N_br": "N_br"}
B = 2000
SEMENTE = 42


def fnum(x):
    """
    Purpose:
        Convert a CSV field to float, returning None for empty or non-numeric values.
    Parameters:
        x: value read from a CSV field
    Returns:
        float or None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    try:
        return float(x)
    except Exception:
        return None


def carregar():
    """
    Purpose:
        Load the longitudinal series used by the A2.3 mixed model.
    Parameters:
        none
    Returns:
        dict of series
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    ser = defaultdict(list)
    for r in csv.DictReader(open(LONG, encoding="utf-8")):
        if r["coleta"] == "" or fnum(r["sigma_a"]) is None:
            continue
        ser[r["rizotron"]].append({
            "riz": r["rizotron"], "trat": r["tratamento"], "DAP": fnum(r["DAP"]),
            "sigma": fnum(r["sigma_a"]) * 1000,
            **{nm: fnum(r[col]) for col, nm in OPT.items()}})
    return ser


def ajustar(ser_list):
    """ser_list: lista de (id_unico, registros). Devolve {nm: beta_padronizado}."""
    recs = []
    for uid, rs in ser_list:
        sm = np.mean([d["sigma"] for d in rs])
        for d in rs:
            recs.append({**d, "riz": uid, "sig_w": d["sigma"] - sm})
    df = pd.DataFrame(recs)
    out = {}
    for nm in OPT.values():
        d2 = df.dropna(subset=[nm])
        if d2["riz"].nunique() < 3 or len(d2) < 12:
            out[nm] = np.nan
            continue
        try:
            m = smf.mixedlm(f"{nm} ~ sig_w + DAP + C(trat)", d2, groups=d2["riz"]).fit(reml=False)
            b = m.params.get("sig_w", np.nan)
            sx, sy = d2["sig_w"].std(), d2[nm].std()
            out[nm] = float(b * sx / sy) if sy else np.nan
        except Exception:
            out[nm] = np.nan
    return out


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
    ser = carregar()
    rizs = sorted(ser)
    print(f"[A16b] {len(rizs)} rizotrons | B={B} | modelo misto reajustado a cada reamostra")
    ponto = ajustar([(r, ser[r]) for r in rizs])

    rng = np.random.default_rng(SEMENTE)
    dist = defaultdict(list)
    for i in range(B):
        esc = rng.choice(len(rizs), size=len(rizs), replace=True)
        amostra = [(f"{rizs[e]}#{j}", ser[rizs[e]]) for j, e in enumerate(esc)]
        for nm, v in ajustar(amostra).items():
            if np.isfinite(v):
                dist[nm].append(v)
        if (i + 1) % 250 == 0:
            print(f"    {i+1}/{B}", flush=True)

    linhas = []
    print("\n  %-10s %8s   %s" % ("descritor", "beta", "IC95%"))
    for nm in OPT.values():
        d = np.array(dist[nm])
        lo, hi = np.percentile(d, [2.5, 97.5])
        marca = "  *exclui 0" if lo * hi > 0 else "   inclui 0"
        print("  %-10s %+8.3f   [%+.3f, %+.3f]%s" % (nm, ponto[nm], lo, hi, marca))
        linhas.append({"estimando": "beta_intra_misto", "descritor": nm,
                       "ponto": round(float(ponto[nm]), 3),
                       "IC95_lo": round(float(lo), 3), "IC95_hi": round(float(hi), 3),
                       "B": B, "unidade_reamostragem": "rizotron", "n": len(rizs)})

    out = C.METRICAS / "A16_ic_beta_misto.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader(); w.writerows(linhas)
    print(f"\n[A16b] {out.name} gravado.")


if __name__ == "__main__":
    main()
