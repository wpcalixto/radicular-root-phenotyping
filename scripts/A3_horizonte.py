#!/usr/bin/env python3
"""
Title:
    Horizon performance relative to treatment reference
File type:
    Script
Purpose:
    Computes, for horizons 1-6, the ratio between model MAE and the treatment-reference MAE for
    optical, electrical, combined and full configurations.
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
    - metricas/multimodal_long.csv
Outputs:
    - metricas/A3_horizonte.csv
Dependencies:
    - numpy
    - sklearn
    - local: config
Execution:
    python scripts/A3_horizonte.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs
    byte-identical to the archived versions. Environment of the verification: Python 3.9.6 (macOS)
    with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
A3 (complementar) — desempenho por horizonte relativo à referência por tratamento.
Para h=1..6, MAE LORO (Ridge) das configurações óptica/elétrica/óptica+elétrica/completo com
features acumuladas até h, dividido pela MAE da referência condicionada ao tratamento (constante).
Razão <1 = supera a referência-tratamento. Saída: metricas/A3_horizonte.csv + figura 17.
"""
import os, sys, csv, warnings
import statistics as st
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings("ignore")

LONG = C.METRICAS / "multimodal_long.csv"
ALVOS = {"y_M_r": "M_R", "y_M_a": "M_PA"}
MEANS = ["O_ocupacao", "L_skel_px", "N_br", "sigma_a"]
SLOPES = ["O_ocupacao", "L_skel_px", "sigma_a"]
TRAT_NIVEIS = ["T1", "T2", "T3"]   # REF = categoria-base (contrastes binários)
def trat_contrastes(t):
    """
    Purpose:
        Encode a treatment label as one-hot indicator values for the non-reference treatment levels.
    Parameters:
        t: treatment label
    Returns:
        indicator values (list or dict keyed by trat_<level>)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return {"trat_%s" % n: (1.0 if t == n else 0.0) for n in TRAT_NIVEIS}
OPT = ["O_ocupacao_m", "L_skel_px_m", "N_br_m", "O_ocupacao_s", "L_skel_px_s"]
ELEC = ["sigma_a_m", "sigma_a_s"]
MAN = ["trat_T1", "trat_T2", "trat_T3"]
CONF = {"óptica": OPT, "elétrica": ELEC, "óptica+elétrica": OPT + ELEC, "completo": OPT + ELEC + MAN}


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
    try: return float(x)
    except (TypeError, ValueError): return None


def feat_h(serie, h):
    """
    Purpose:
        Build features accumulated up to horizon h.
    Parameters:
        serie: series
        h: horizon
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    pts = [(dap, s) for (ck, dap, s) in serie if ck != "" and int(ck) <= h]
    if not pts:
        return None
    f = {}
    for v in MEANS:
        xs = [s[v] for _, s in pts if s[v] is not None]
        f[v + "_m"] = float(np.mean(xs)) if xs else 0.0
    for v in SLOPES:
        xy = [(d, s[v]) for d, s in pts if s[v] is not None]
        f[v + "_s"] = float(np.polyfit([a for a, _ in xy], [b for _, b in xy], 1)[0]) if len(xy) >= 2 else 0.0
    return f


def loro_mae(feats, y, keys):
    """
    Purpose:
        Leave-one-rhizotron-out MAE of a Ridge model.
    Parameters:
        feats: feature dicts
        y: outcomes
        keys: feature names
    Returns:
        float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    X = np.array([[f[k] for k in keys] for f in feats], float); n = len(y); e = np.empty(n)
    for i in range(n):
        tr = [j for j in range(n) if j != i]
        sc = StandardScaler().fit(X[tr])
        m = Ridge(alpha=10.0).fit(sc.transform(X[tr]), [y[j] for j in tr])
        e[i] = abs(y[i] - float(m.predict(sc.transform(X[i:i+1]))[0]))
    return e.mean()


def mae_trat(y, trat):
    """
    Purpose:
        Leave-one-out MAE of the treatment-mean reference.
    Parameters:
        y: outcomes
        trat: treatments
    Returns:
        float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    n = len(y); e = np.empty(n)
    for i in range(n):
        same = [y[j] for j in range(n) if j != i and trat[j] == trat[i]]
        e[i] = abs(y[i] - (np.mean(same) if same else np.mean([y[j] for j in range(n) if j != i])))
    return e.mean()


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
    rows = list(csv.DictReader(open(LONG, encoding="utf-8")))
    serie = defaultdict(list); trat = {}; alvo = defaultdict(dict)
    for r in rows:
        s = {v: fnum(r.get(v)) for v in MEANS}
        serie[r["rizotron"]].append((r["coleta"], fnum(r["DAP"]), s))
        trat[r["rizotron"]] = r["tratamento"]
        for a in ALVOS:
            alvo[r["rizotron"]][a] = fnum(r.get(a))
    rizs = sorted(serie); tr = [trat[r] for r in rizs]
    out = []
    for a, nome in ALVOS.items():
        y = [alvo[r][a] for r in rizs]
        ref = mae_trat(y, tr)
        for h in range(1, 7):
            feats = [dict(feat_h(serie[r], h), **trat_contrastes(trat[r])) for r in rizs]
            for cfg, keys in CONF.items():
                mae = loro_mae(feats, y, keys)
                out.append({"alvo": nome, "config": cfg, "h": h, "MAE": round(mae, 3),
                            "MAE_ref_trat": round(ref, 3), "razao": round(mae / ref, 3)})
    with open(C.METRICAS / "A3_horizonte.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(f"[A3_horizonte] {len(out)} linhas -> A3_horizonte.csv")
    # menor razão observada por alvo (alguma janela supera a referência-tratamento?)
    for nome in ALVOS.values():
        rr = [o for o in out if o["alvo"] == nome]
        best = min(rr, key=lambda o: o["razao"])
        print(f"  {nome}: menor razão = {best['razao']} ({best['config']}, h={best['h']})  "
              f"-> {'supera' if best['razao'] < 1 else 'NÃO supera'} a referência-tratamento")


if __name__ == "__main__":
    main()
