#!/usr/bin/env python3
"""
Title:
    Rigour audits of optical-electrical analyses
File type:
    Script
Purpose:
    Runs increment analyses with rhizotron bootstrap, trajectory tests with blocked permutation and
    Holm correction, and intra-rhizotron level models.
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
    - printed results only
Dependencies:
    - numpy
    - pandas
    - scipy
    - statsmodels
    - local: config
Execution:
    python scripts/A2_auditoria.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Verification in v1.0.0: re-executed without error (printed results
    only). Environment of the verification: Python 3.9.6 (macOS) with the versions listed in
    requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
A2 — auditorias de rigor (a pedido do orientador):
  A2.1  incrementos: janela balanceada C1-C6 (contemp n=60, defasada n=48) + sensib. C7 (n=58).
        Bootstrap reamostra RIZOTRONS inteiros (cluster).
  A2.2  trajetórias: Spearman bruto E centrado-dentro-do-tratamento; p por PERMUTAÇÃO BLOQUEADA
        dentro de tratamento (exata, (3!)^4=1296); Holm(3); estabilidade leave-one-rhizotron-out.
  A2.3  níveis intra-rizotron: coleta CATEGÓRICA (não DAP linear) + tratamento; β padronizado;
        IC95% por CLUSTER bootstrap (rizotron); leave-one-rhizotron-out; Holm(3).
Sempre σ_a canônica.
"""
import os, sys, csv, warnings, itertools
import statistics as st
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr, theilslopes
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


def load():
    """
    Purpose:
        Load the multimodal longitudinal table into per-rhizotron series.
    Parameters:
        none
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rows = list(csv.DictReader(open(LONG, encoding="utf-8")))
    ser = defaultdict(list)
    for r in rows:
        if r["coleta"] == "":
            continue
        ser[r["rizotron"]].append(r)
    for riz in ser:
        ser[riz] = sorted(ser[riz], key=lambda r: int(r["coleta"]))
    return ser


def holm(ps):
    """
    Purpose:
        Apply the Holm step-down adjustment to a list of p-values.
    Parameters:
        ps or pvals: p-values
    Returns:
        list of adjusted p-values
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    idx = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); m = len(ps); prev = 0
    for rank, i in enumerate(idx):
        v = min(1.0, (m - rank) * ps[i]); prev = max(prev, v); adj[i] = prev
    return adj


# ---------- A2.1 incrementos ----------
def a21(ser):
    """
    Purpose:
        Run the increment analyses with rhizotron bootstrap.
    Parameters:
        ser: series
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    print("=== A2.1 incrementos (bootstrap = rizotrons inteiros) ===")
    for lag, nome, maxk in [(0, "contemporânea (C1-C6)", 6), (1, "defasada balanceada (C1-C6)", 6),
                            (1, "defasada + C7 (sensib.)", 7)]:
        for col, nm in OPT.items():
            pairs = []  # (riz, dSigma, dY)
            for riz, rs in ser.items():
                for a, b in zip(rs[:-1], rs[1:]):
                    if int(b["coleta"]) > 6:      # Δσ exige janela elétrica
                        continue
                    ds = fnum(b["sigma_a"]); dsa = fnum(a["sigma_a"])
                    if ds is None or dsa is None:
                        continue
                    dS = (ds - dsa) * 1000
                    tgt = b if lag == 0 else next((c for c, d in zip(rs, rs[1:]) if int(c["coleta"]) == int(b["coleta"]) and False), None)
                    # alvo defasado: intervalo seguinte (coleta = int(b)+1)
                    if lag == 1:
                        nxt = [(rs[i], rs[i+1]) for i in range(len(rs)-1) if int(rs[i]["coleta"]) == int(b["coleta"])]
                        if not nxt:
                            continue
                        pa, pb = nxt[0]
                        if int(pb["coleta"]) > maxk:
                            continue
                        va, vb = fnum(pa[col]), fnum(pb[col])
                    else:
                        va, vb = fnum(a[col]), fnum(b[col])
                    if va is None or vb is None:
                        continue
                    pairs.append((riz, dS, vb - va))
            r = _rmcorr(pairs); lo, hi = _cluster_ci(pairs)
            if nm == "O":  # imprime cabeçalho por bloco
                print(f"  [{nome}]  n={len(pairs)}")
            print(f"     Δ{nm:8s} r={r:+.3f}  IC95%[{lo:+.2f},{hi:+.2f}]")


def _rmcorr(pairs):
    by = defaultdict(list)
    for riz, x, y in pairs:
        by[riz].append((x, y))
    xs, ys = [], []
    for pts in by.values():
        if len(pts) < 2:
            continue
        mx = st.mean(p[0] for p in pts); my = st.mean(p[1] for p in pts)
        for x, y in pts:
            xs.append(x - mx); ys.append(y - my)
    from scipy.stats import pearsonr
    return pearsonr(xs, ys)[0] if len(xs) > 2 else float("nan")


def _cluster_ci(pairs):
    rizs = sorted(set(p[0] for p in pairs)); by = defaultdict(list)
    for p in pairs:
        by[p[0]].append(p)
    bs = []
    for _ in range(5000):
        samp = []
        for r in RNG.choice(rizs, len(rizs), replace=True):
            samp += by[r]
        v = _rmcorr(samp)
        if v == v:
            bs.append(v)
    return np.percentile(bs, [2.5, 97.5])


# ---------- A2.2 trajetórias ----------
def theil(ser, key, scale=1.0):
    """
    Purpose:
        Theil-Sen slopes per rhizotron for one variable.
    Parameters:
        ser: series
        key: variable
        scale: scaling factor
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    out = {}
    for riz, rs in ser.items():
        pts = [(fnum(d["DAP"]), fnum(d[key])) for d in rs
               if int(d["coleta"]) <= 6 and fnum(d[key]) is not None and fnum(d["sigma_a"]) is not None]
        if len(pts) >= 3:
            out[riz] = theilslopes([p[1] * scale for p in pts], [p[0] for p in pts])[0]
    return out


def a22(ser):
    """
    Purpose:
        Run the trajectory analyses with blocked permutation.
    Parameters:
        ser: series
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    print("\n=== A2.2 trajetórias (Theil-Sen por rizotron, n=12) ===")
    trat = {riz: rs[0]["tratamento"] for riz, rs in ser.items()}
    ssig = theil(ser, "sigma_a", 1000)
    ps_raw, ps_within = [], []
    detail = []
    for col, nm in OPT.items():
        sy = theil(ser, col)
        rizs = [r for r in ssig if r in sy]
        x = np.array([ssig[r] for r in rizs]); y = np.array([sy[r] for r in rizs]); tt = [trat[r] for r in rizs]
        rho_raw = spearmanr(x, y)[0]
        # centrar dentro do tratamento
        tm_x = defaultdict(list); tm_y = defaultdict(list)
        for xi, yi, t in zip(x, y, tt):
            tm_x[t].append(xi); tm_y[t].append(yi)
        mx = {t: st.mean(v) for t, v in tm_x.items()}; my = {t: st.mean(v) for t, v in tm_y.items()}
        xw = np.array([xi - mx[t] for xi, t in zip(x, tt)]); yw = np.array([yi - my[t] for yi, t in zip(y, tt)])
        rho_w = spearmanr(xw, yw)[0]
        # permutação bloqueada dentro do tratamento (exata)
        groups = defaultdict(list)
        for i, t in enumerate(tt):
            groups[t].append(i)
        obs = rho_w; count = 1; total = 1
        perms_by_g = {t: list(itertools.permutations(range(len(ix)))) for t, ix in groups.items()}
        for combo in itertools.product(*[perms_by_g[t] for t in groups]):
            yp = y.copy()
            for (t, ix), perm in zip(groups.items(), combo):
                yp[ix] = y[[ix[j] for j in perm]]
            ypw = np.array([yp[i] - {tt2: st.mean(yp[[k for k in range(len(tt)) if tt[k] == tt2]]) for tt2 in set(tt)}[tt[i]] for i in range(len(tt))])
            rp = spearmanr(xw, ypw)[0]
            total += 1
            if abs(rp) >= abs(obs) - 1e-9:
                count += 1
        p_perm = count / total
        # LORO estabilidade (ρ bruto)
        loo = [spearmanr(np.delete(x, i), np.delete(y, i))[0] for i in range(len(rizs))]
        ps_raw.append(spearmanr(x, y)[1]); ps_within.append(p_perm)
        detail.append((nm, rho_raw, rho_w, p_perm, min(loo), max(loo), len(rizs)))
    hw = holm([d[3] for d in detail])
    print("  Y        ρ_bruto  ρ_intra-trat  p_perm(bloq)  p_Holm   LORO ρ[min,max]")
    for (nm, rr, rw, pp, lo, hi, n), ph in zip(detail, hw):
        print(f"  s_{nm:7s} {rr:+.2f}     {rw:+.2f}         {pp:.3f}        {ph:.3f}    [{lo:+.2f},{hi:+.2f}]")


# ---------- A2.3 níveis ----------
def a23(ser):
    """
    Purpose:
        Run the intra-rhizotron level models.
    Parameters:
        ser: series
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    print("\n=== A2.3 níveis intra-rizotron (coleta categórica; β padronizado; cluster bootstrap) ===")
    import pandas as pd
    recs = []
    for riz, rs in ser.items():
        vals = [(d) for d in rs if int(d["coleta"]) <= 6 and fnum(d["sigma_a"]) is not None]
        sm = st.mean(fnum(d["sigma_a"]) * 1000 for d in vals)
        for d in vals:
            recs.append({"riz": riz, "trat": d["tratamento"], "coleta": int(d["coleta"]),
                         "sig_w": fnum(d["sigma_a"]) * 1000 - sm,
                         **{nm: fnum(d[col]) for col, nm in OPT.items()}})
    df = pd.DataFrame(recs)
    detail = []
    for col, nm in OPT.items():
        d2 = df.dropna(subset=[nm]).copy()
        # padroniza sig_w e Y (z-score) para β comparável
        d2["xz"] = (d2["sig_w"] - d2["sig_w"].mean()) / d2["sig_w"].std()
        d2["yz"] = (d2[nm] - d2[nm].mean()) / d2[nm].std()
        def fit(dd):
            m = smf.mixedlm("yz ~ xz + C(coleta) + C(trat)", dd, groups=dd["riz"]).fit(reirml=False)
            return m.params.get("xz", float("nan")), m.pvalues.get("xz", float("nan"))
        b, p = fit(d2)
        rizs = sorted(d2["riz"].unique())
        bs = []
        for _ in range(3000):
            samp = pd.concat([d2[d2["riz"] == r] for r in RNG.choice(rizs, len(rizs), replace=True)])
            try: bs.append(fit(samp)[0])
            except Exception: pass
        lo, hi = np.nanpercentile(bs, [2.5, 97.5])
        loo = []
        for r in rizs:
            try: loo.append(fit(d2[d2["riz"] != r])[0])
            except Exception: pass
        detail.append((nm, b, lo, hi, p, min(loo), max(loo)))
    hw = holm([d[4] for d in detail])
    print("  Y        β_pad   IC95%(cluster)     p      p_Holm  LORO β[min,max]")
    for (nm, b, lo, hi, p, mn, mx), ph in zip(detail, hw):
        sig = "  *" if hi < 0 or lo > 0 else ""
        print(f"  {nm:8s} {b:+.3f}  [{lo:+.2f},{hi:+.2f}]   {p:.3f}   {ph:.3f}   [{mn:+.2f},{mx:+.2f}]{sig}")


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
    ser = load()
    a21(ser); a22(ser); a23(ser)


if __name__ == "__main__":
    main()
