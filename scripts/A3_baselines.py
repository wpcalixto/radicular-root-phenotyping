#!/usr/bin/env python3
"""
Title:
    Treatment-dependent baselines
File type:
    Script
Purpose:
    Compares seven predictive configurations against treatment-conditioned references by leave-one-
    rhizotron-out validation with paired rhizotron-level differences and bootstrap intervals.
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
    - metricas/A3_baselines.csv
Dependencies:
    - numpy
    - scipy
    - sklearn
    - local: config
Execution:
    python scripts/A3_baselines.py (from a workspace prepared with tools/prepare_workspace.py)
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
Resultado adicional A3 — Referências dependentes do tratamento (rigor da modelagem).
Compara, por LORO (n=12, conjunto canônico C1-C6), sete configurações:
  1 média global (treino)   2 média do tratamento (treino, mesmo grupo)   3 modelo só-tratamento
  4 óptica   5 elétrica   6 óptica+elétrica   7 completo (Ridge).
Para cada rizotron: d_i = |erro_modelo| - |erro_referência(trat)|; média, IC95% bootstrap de rizotron,
Wilcoxon pareado. Pergunta: o multimodal supera a referência que JÁ conhece o grupo experimental?
Saída: metricas/A3_baselines.csv + impressão.
"""
import os, sys, csv
import statistics as st
from collections import defaultdict
import numpy as np
from scipy.stats import wilcoxon
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

LONG = C.METRICAS / "multimodal_long.csv"
ALVOS = {"y_M_r": "M_R (raiz)", "y_M_a": "M_PA (aérea)", "y_R_ar": "Q_PA/R"}
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
RNG = np.random.default_rng(42)


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
        f[v + "_m"] = float(np.mean(xs)) if xs else 0.0
    for v in SLOPES:
        xy = [(d, s[v]) for d, s in pts if s[v] is not None]
        f[v + "_s"] = float(np.polyfit([a for a, _ in xy], [b for _, b in xy], 1)[0]) if len(xy) >= 2 else 0.0
    return f


def loro_err(feats, y, trat, keys, kind):
    """Erros absolutos por rizotron. kind: 'ridge' usa keys; 'gmean'/'tmean' são referências."""
    n = len(y); e = np.empty(n)
    X = np.array([[f[k] for k in keys] for f in feats], float) if keys else None
    for i in range(n):
        tr = [j for j in range(n) if j != i]
        if kind == "gmean":
            pred = np.mean([y[j] for j in tr])
        elif kind == "tmean":
            same = [y[j] for j in tr if trat[j] == trat[i]]
            pred = np.mean(same) if same else np.mean([y[j] for j in tr])
        else:
            sc = StandardScaler().fit(X[tr])
            m = Ridge(alpha=10.0).fit(sc.transform(X[tr]), [y[j] for j in tr])
            pred = float(m.predict(sc.transform(X[i:i+1]))[0])
        e[i] = abs(y[i] - pred)
    return e


def boot_ci(d):
    """
    Purpose:
        Percentile bootstrap interval of a mean difference over rhizotrons.
    Parameters:
        d: per-rhizotron differences
    Returns:
        tuple (low, high)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    n = len(d)
    bs = [d[RNG.integers(0, n, n)].mean() for _ in range(10000)]
    return np.percentile(bs, [2.5, 97.5])


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
    rizs = sorted(serie)
    feats = [dict(construir(serie[r]), **trat_contrastes(trat[r])) for r in rizs]
    tr = [trat[r] for r in rizs]

    CONF = [("media_global", None, "gmean"), ("media_tratamento", None, "tmean"),
            ("so_tratamento", MAN, "ridge"), ("optica", OPT, "ridge"),
            ("eletrica", ELEC, "ridge"), ("optica+eletrica", OPT + ELEC, "ridge"),
            ("completo", OPT + ELEC + MAN, "ridge")]
    out = []
    for a, nome in ALVOS.items():
        y = [alvo[r][a] for r in rizs]
        err = {}
        print(f"\n=== {nome} ===")
        print("  configuração          MAE     ΔMAE vs média-trat   IC95%            Wilcoxon p")
        for cfg, keys, kind in CONF:
            err[cfg] = loro_err(feats, y, tr, keys, kind)
        for cfg, keys, kind in CONF:
            mae = err[cfg].mean()
            if cfg == "media_tratamento":
                print(f"  {cfg:20s} {mae:6.2f}     (referência)")
                out.append({"alvo": nome, "config": cfg, "MAE": round(mae, 3), "dMAE": "", "IC_lo": "", "IC_hi": "", "wilcoxon_p": ""})
                continue
            d = err[cfg] - err["media_tratamento"]
            lo, hi = boot_ci(d)
            try: p = wilcoxon(d)[1]
            except Exception: p = float("nan")
            sig = "  *" if (hi < 0 or lo > 0) else ""
            print(f"  {cfg:20s} {mae:6.2f}     {d.mean():+6.2f}             [{lo:+.2f},{hi:+.2f}]  {p:.3f}{sig}")
            out.append({"alvo": nome, "config": cfg, "MAE": round(mae, 3), "dMAE": round(d.mean(), 3),
                        "IC_lo": round(lo, 3), "IC_hi": round(hi, 3), "wilcoxon_p": round(p, 4)})
    with open(C.METRICAS / "A3_baselines.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print("\n(ΔMAE<0 e IC excluindo 0 = modelo MELHOR que a média-por-tratamento)")
    print("-> metricas/A3_baselines.csv")


if __name__ == "__main__":
    main()
