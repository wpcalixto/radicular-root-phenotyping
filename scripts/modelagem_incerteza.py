#!/usr/bin/env python3
"""
Title:
    Uncertainty of modelling and ablation
File type:
    Script
Purpose:
    Computes rhizotron-level bootstrap intervals for configuration MAEs and MAE differences and
    jackknife influence by rhizotron.
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
    - metricas/model_uncertainty.csv
Dependencies:
    - numpy
    - sklearn
    - local: config
Execution:
    python scripts/modelagem_incerteza.py (from a workspace prepared with
    tools/prepare_workspace.py)
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
"""
Incerteza da modelagem/ablação (auditoria V17): IC 95% por BOOTSTRAP no nível do rizotron
para o MAE de cada configuração e para os ΔMAE (fusão e contraste elétrica×óptica), além da
análise de influência (jackknife por rizotron). Conjunto canônico C1–C6, LORO.
Saída: metricas/model_uncertainty.csv + impressão.
"""
import os, sys, csv
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

LONG = C.METRICAS / "multimodal_long.csv"
MEANS = ["O_ocupacao", "L_skel_px", "N_br", "sigma_a"]
SLOPES = ["O_ocupacao", "L_skel_px", "sigma_a"]
OPT = ["O_ocupacao_m", "L_skel_px_m", "N_br_m", "O_ocupacao_s", "L_skel_px_s"]
ELEC = ["sigma_a_m", "sigma_a_s"]
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
MAN = ["trat_T1", "trat_T2", "trat_T3"]
FULL = OPT + ELEC + MAN
RNG = np.random.default_rng(42)
B = 5000


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


def construir(serie):
    """
    Purpose:
        Build per-rhizotron temporal features (area under the curve and slope) from collections C1-C6 of a series.
    Parameters:
        serie: list of (collection, DAP, value) tuples
    Returns:
        dict of features
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    pts = [(dap, s) for (ck, dap, s) in serie if ck != "" and int(ck) <= 6]
    f = {}
    for v in MEANS:
        xs = [s[v] for _, s in pts if s[v] is not None]
        f[f"{v}_m"] = float(np.mean(xs)) if xs else 0.0
    for v in SLOPES:
        xy = [(d, s[v]) for d, s in pts if s[v] is not None]
        f[f"{v}_s"] = float(np.polyfit([a for a, _ in xy], [b for _, b in xy], 1)[0]) if len(xy) >= 2 else 0.0
    return f


def loro_err(feats, y, keys, model):
    """Erros absolutos por rizotron (LORO)."""
    X = np.array([[f[k] for k in keys] for f in feats], float); y = np.array(y, float)
    e = np.empty(len(y))
    for i in range(len(y)):
        tr = [j for j in range(len(y)) if j != i]
        sc = StandardScaler().fit(X[tr])
        m = model.__class__(**model.get_params()).fit(sc.transform(X[tr]), y[tr])
        e[i] = abs(y[i] - float(np.ravel(m.predict(sc.transform(X[i:i+1])))[0]))
    return e


def ci(vals):
    """
    Purpose:
        Percentile 95% interval.
    Parameters:
        vals: bootstrap values
    Returns:
        tuple
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def boot_mae(err):
    """
    Purpose:
        Rhizotron bootstrap of MAE.
    Parameters:
        err: absolute errors
    Returns:
        numpy array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    n = len(err)
    bs = [err[RNG.integers(0, n, n)].mean() for _ in range(B)]
    return err.mean(), ci(bs)


def boot_dmae(e1, e2):
    """ΔMAE = mean(e1) - mean(e2) com bootstrap pareado."""
    d = e1 - e2; n = len(d)
    bs = [d[RNG.integers(0, n, n)].mean() for _ in range(B)]
    return d.mean(), ci(bs)


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
        for a in ("y_M_r", "y_M_a"):
            alvo[r["rizotron"]][a] = fnum(r.get(a))
    rizs = sorted(serie)
    feats = []
    for riz in rizs:
        f = construir(serie[riz]); f.update(trat_contrastes(trat[riz])); feats.append(f)

    out = []
    CONF = {"optical": OPT, "electrical": ELEC, "optical+electrical": OPT + ELEC, "full": FULL}
    BEST = {"y_M_r": ("Lasso", Lasso(alpha=0.5, max_iter=10000)),
            "y_M_a": ("SVR", SVR(kernel="rbf", C=1.0, gamma="scale"))}
    for a in ("y_M_r", "y_M_a"):
        y = [alvo[riz][a] for riz in rizs]
        print(f"\n=== {a} ===")
        # melhor modelo (best): IC do MAE
        e_best = loro_err(feats, y, FULL, BEST[a][1])
        mae, (lo, hi) = boot_mae(e_best)
        print(f"  {BEST[a][0]:6s} full  MAE={mae:.2f}  IC95[{lo:.2f}, {hi:.2f}]")
        out.append({"alvo": a, "config": f"best:{BEST[a][0]}", "MAE": round(mae, 3),
                    "IC_lo": round(lo, 3), "IC_hi": round(hi, 3)})
        # configs por fonte (Ridge)
        err = {}
        for nome, keys in CONF.items():
            e = loro_err(feats, y, keys, Ridge(alpha=10.0)); err[nome] = e
            mae, (lo, hi) = boot_mae(e)
            print(f"  Ridge {nome:18s} MAE={mae:.2f}  IC95[{lo:.2f}, {hi:.2f}]")
            out.append({"alvo": a, "config": f"Ridge:{nome}", "MAE": round(mae, 3),
                        "IC_lo": round(lo, 3), "IC_hi": round(hi, 3)})
        # ΔMAE: fusão (óptica − óptica+elétrica) e elétrica − óptica
        for nome, e1, e2 in [("fusao(opt-opt+ele)", err["optical"], err["optical+electrical"]),
                             ("eletrica-optica", err["electrical"], err["optical"])]:
            d, (lo, hi) = boot_dmae(e1, e2)
            sig = "" if lo <= 0 <= hi else "  *IC exclui 0"
            print(f"  ΔMAE {nome:22s} = {d:+.2f}  IC95[{lo:+.2f}, {hi:+.2f}]{sig}")
            out.append({"alvo": a, "config": f"dMAE:{nome}", "MAE": round(d, 3),
                        "IC_lo": round(lo, 3), "IC_hi": round(hi, 3)})
        # influência: jackknife por rizotron no MAE do melhor
        base = e_best.mean()
        infl = [abs(np.delete(e_best, i).mean() - base) for i in range(len(rizs))]
        j = int(np.argmax(infl))
        print(f"  influência: rizotron mais influente {rizs[j]} (Δ MAE ao removê-lo = {infl[j]:.2f})")
        out.append({"alvo": a, "config": "influencia_max", "MAE": round(max(infl), 3),
                    "IC_lo": rizs[j], "IC_hi": ""})

    with open(C.METRICAS / "model_uncertainty.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["alvo", "config", "MAE", "IC_lo", "IC_hi"])
        w.writeheader(); w.writerows(out)
    print("\n-> metricas/model_uncertainty.csv")


if __name__ == "__main__":
    main()
