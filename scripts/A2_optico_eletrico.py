#!/usr/bin/env python3
"""
Title:
    Optical-electrical longitudinal association
File type:
    Script
Purpose:
    Tests contemporaneous and lagged associations between changes in apparent conductivity and
    optical descriptors with mixed models and repeated-measures correlation, and writes per-
    rhizotron slopes.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-13
Date:
    2026-07-13
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
    - metricas/A2_optico_eletrico.csv
    - metricas/A2_slopes_by_rizotron.csv
Dependencies:
    - numpy
    - pandas
    - scipy
    - statsmodels
    - local: config
Execution:
    python scripts/A2_optico_eletrico.py (from a workspace prepared with tools/prepare_workspace.py)
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
Resultado adicional A2 — Associação longitudinal entre as modalidades óptica e elétrica.
Diferenças entre coletas por rizotron: Δσ_a, ΔO, ΔL_skel, ΔN_br (janela elétrica C1–C6).
Testa associação CONTEMPORÂNEA (ΔY_k ~ Δσ_k) e DEFASADA (ΔY_{k+1} ~ Δσ_k), com:
  - modelo linear misto (rizotron = intercepto aleatório; controla tratamento);
  - correlação intra-rizotron (rmcorr = Pearson após centrar por rizotron) + IC95% bootstrap de rizotron.
Interpretação ASSOCIATIVA (σ responde também a água/sais/adubação).
Saída: metricas/A2_optico_eletrico.csv + impressão.
"""
import os, sys, csv, warnings
import statistics as st
from collections import defaultdict
import numpy as np
from scipy.stats import pearsonr, spearmanr, theilslopes
import statsmodels.formula.api as smf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
warnings.filterwarnings("ignore")

LONG = C.METRICAS / "multimodal_long.csv"
OPT = {"O_ocupacao": "O", "L_skel_px": "L_skel", "N_br": "N_br"}
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


def build_diffs():
    """Retorna lista de dicts: rizotron, tratamento, k (intervalo), DAP_mid, dSigma, dO, dL, dN."""
    rows = list(csv.DictReader(open(LONG, encoding="utf-8")))
    ser = defaultdict(list)
    for r in rows:
        if r["coleta"] == "":
            continue
        ser[r["rizotron"]].append(r)
    out = []
    for riz, rs in ser.items():
        rs = sorted(rs, key=lambda r: int(r["coleta"]))
        for a, b in zip(rs[:-1], rs[1:]):
            sa, sb = fnum(a["sigma_a"]), fnum(b["sigma_a"])
            d = {"rizotron": riz, "tratamento": a["tratamento"], "k": int(b["coleta"]),
                 "DAP_mid": (fnum(a["DAP"]) + fnum(b["DAP"])) / 2,
                 "dSigma": (sb - sa) * 1000 if (sa is not None and sb is not None) else None}
            for col, nm in OPT.items():
                va, vb = fnum(a[col]), fnum(b[col])
                d["d" + nm] = (vb - va) if (va is not None and vb is not None) else None
            out.append(d)
    return out


def rmcorr(pairs):
    """pairs: lista (riz, x, y). Centra x,y por rizotron e correlaciona (within-subject)."""
    by = defaultdict(list)
    for riz, x, y in pairs:
        by[riz].append((x, y))
    xs, ys = [], []
    for riz, pts in by.items():
        if len(pts) < 2:
            continue
        mx = st.mean(p[0] for p in pts); my = st.mean(p[1] for p in pts)
        for x, y in pts:
            xs.append(x - mx); ys.append(y - my)
    if len(xs) < 3:
        return None, None
    return pearsonr(xs, ys)[0], len(xs)


def boot_ci(pairs):
    """
    Purpose:
        Rhizotron-cluster bootstrap interval of a within-rhizotron correlation.
    Parameters:
        pairs: (rhizotron, x, y) tuples
    Returns:
        tuple (low, high)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rizs = sorted(set(p[0] for p in pairs))
    by = defaultdict(list)
    for p in pairs:
        by[p[0]].append(p)
    bs = []
    for _ in range(5000):
        samp = []
        for r in RNG.choice(rizs, len(rizs), replace=True):
            samp += by[r]
        r, _ = rmcorr(samp)
        if r is not None:
            bs.append(r)
    return np.percentile(bs, [2.5, 97.5])


def analise(diffs, lag):
    """lag=0 contemporâneo; lag=1 defasado (ΔY do intervalo seguinte ~ Δσ do intervalo atual)."""
    res = []
    byk = {(d["rizotron"], d["k"]): d for d in diffs}
    for col, nm in OPT.items():
        pairs, recs = [], []
        for d in diffs:
            if d["dSigma"] is None:
                continue
            tgt = d if lag == 0 else byk.get((d["rizotron"], d["k"] + 1))
            if tgt is None or tgt["d" + nm] is None:
                continue
            pairs.append((d["rizotron"], d["dSigma"], tgt["d" + nm]))
            recs.append({"riz": d["rizotron"], "trat": d["tratamento"], "dSigma": d["dSigma"],
                         "dY": tgt["d" + nm], "DAP": d["DAP_mid"]})
        r, n = rmcorr(pairs)
        lo, hi = boot_ci(pairs)
        # modelo misto: dY ~ dSigma + tratamento, rizotron aleatório
        import pandas as pd
        df = pd.DataFrame(recs)
        try:
            m = smf.mixedlm("dY ~ dSigma + C(trat)", df, groups=df["riz"]).fit(reirml=False)
            beta = m.params.get("dSigma", float("nan")); p = m.pvalues.get("dSigma", float("nan"))
        except Exception:
            beta, p = float("nan"), float("nan")
        sig = "" if (lo <= 0 <= hi) else "  *IC exclui 0"
        res.append((nm, r, lo, hi, n, beta, p, sig))
    return res


def levels():
    """Níveis por rizotron×coleta na janela elétrica (σ presente). Retorna dict riz->list."""
    rows = list(csv.DictReader(open(LONG, encoding="utf-8")))
    ser = defaultdict(list)
    for r in rows:
        if r["coleta"] == "" or fnum(r["sigma_a"]) is None:
            continue
        ser[r["rizotron"]].append({"riz": r["rizotron"], "trat": r["tratamento"], "DAP": fnum(r["DAP"]),
                                   "sigma": fnum(r["sigma_a"]) * 1000, "trend": r["tratamento"],
                                   **{nm: fnum(r[col]) for col, nm in OPT.items()}})
    return ser


def theil(riz_series, key):
    """inclinação Theil-Sen de key ~ DAP por rizotron. Retorna {riz: slope}."""
    out = {}
    for riz, rs in riz_series.items():
        pts = [(d["DAP"], d[key]) for d in rs if d[key] is not None]
        if len(pts) >= 3:
            out[riz] = theilslopes([p[1] for p in pts], [p[0] for p in pts])[0]
    return out


def a22(ser):
    """A2.2 — concordância direcional das trajetórias (inclinações Theil-Sen por rizotron)."""
    ssig = theil(ser, "sigma")
    print("\n=== A2.2 — concordância direcional das trajetórias (n=12 rizotrons) ===")
    print("  Y        Spearman(s_σ,s_Y)  IC95%            mesma direção  (++/+-/-+/--)")
    res = []
    for col, nm in OPT.items():
        sy = theil(ser, nm)
        rizs = [r for r in ssig if r in sy]
        xs = np.array([ssig[r] for r in rizs]); ys = np.array([sy[r] for r in rizs])
        rho, p = spearmanr(xs, ys)
        bs = [spearmanr(*zip(*[(xs[i], ys[i]) for i in RNG.integers(0, len(xs), len(xs))]))[0] for _ in range(5000)]
        lo, hi = np.nanpercentile(bs, [2.5, 97.5])
        pp = sum((xs > 0) & (ys > 0)); pm = sum((xs > 0) & (ys < 0))
        mp = sum((xs < 0) & (ys > 0)); mm = sum((xs < 0) & (ys < 0))
        same = (pp + mm) / len(rizs)
        print(f"  s_{nm:7s} {rho:+.3f}            [{lo:+.2f},{hi:+.2f}]   {same*100:.0f}%          ({pp}/{pm}/{mp}/{mm})")
        res.append({"assoc": "A2.2_direcao", "Y": nm, "rmcorr": round(rho, 3), "IC_lo": round(lo, 3),
                    "IC_hi": round(hi, 3), "n": len(rizs), "beta_misto": round(same, 3), "p_misto": ""})
    return res


def a23(ser):
    """A2.3 — associação intra-rizotron nos níveis, σ centrada por rizotron, controlando DAP e tratamento."""
    import pandas as pd
    recs = []
    smean = {riz: st.mean(d["sigma"] for d in rs) for riz, rs in ser.items()}
    for riz, rs in ser.items():
        for d in rs:
            recs.append({**d, "sig_w": d["sigma"] - smean[riz]})
    df = pd.DataFrame(recs)
    print("\n=== A2.3 — associação intra-rizotron nos níveis (σ centrada; controla DAP+tratamento) ===")
    print("  Y        β_within     p     (rizotron aleatório)")
    res = []
    for col, nm in OPT.items():
        d2 = df.dropna(subset=[nm])
        try:
            m = smf.mixedlm(f"{nm} ~ sig_w + DAP + C(trat)", d2, groups=d2["riz"]).fit(reirml=False)
            b = m.params.get("sig_w", float("nan")); p = m.pvalues.get("sig_w", float("nan"))
        except Exception:
            b, p = float("nan"), float("nan")
        sig = "  *" if p < 0.05 else ""
        print(f"  {nm:8s} {b:+.4g}     {p:.3f}{sig}")
        res.append({"assoc": "A2.3_niveis", "Y": nm, "rmcorr": "", "IC_lo": "", "IC_hi": "",
                    "n": len(d2), "beta_misto": round(b, 5), "p_misto": round(p, 4)})
    return res


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
    diffs = build_diffs()
    n_sig = sum(1 for d in diffs if d["dSigma"] is not None)
    print(f"[A2] {len(diffs)} intervalos entre coletas; {n_sig} com Δσ (janela elétrica).")
    out = []
    for lag, nome in [(0, "contemporânea"), (1, "defasada (Δσ_k → ΔY_{k+1})")]:
        print(f"\n=== Associação {nome} ===")
        print("  Y        rmcorr r  IC95%              n   β(misto)   p")
        for nm, r, lo, hi, n, beta, p, sig in analise(diffs, lag):
            print(f"  Δ{nm:8s} {r:+.3f}   [{lo:+.2f},{hi:+.2f}]   {n:3d}  {beta:+.4g}   {p:.3f}{sig}")
            out.append({"assoc": nome, "Y": nm, "rmcorr": round(r, 3),
                        "IC_lo": round(lo, 3), "IC_hi": round(hi, 3), "n": n,
                        "beta_misto": round(beta, 5), "p_misto": round(p, 4)})
    ser = levels()
    # inclinações Theil-Sen por rizotron (para a figura A2.2)
    ss = theil(ser, "sigma"); sO = theil(ser, "O"); sL = theil(ser, "L_skel"); sN = theil(ser, "N_br")
    trat = {riz: rs[0]["trat"] for riz, rs in ser.items()}
    with open(C.METRICAS / "A2_slopes_by_rizotron.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["rizotron", "tratamento", "s_sigma", "s_O", "s_L", "s_N"])
        for riz in sorted(ss):
            w.writerow([riz, trat[riz], ss[riz], sO.get(riz, ""), sL.get(riz, ""), sN.get(riz, "")])
    out += a22(ser)
    out += a23(ser)
    with open(C.METRICAS / "A2_optico_eletrico.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print("\n-> metricas/A2_optico_eletrico.csv")


if __name__ == "__main__":
    main()
