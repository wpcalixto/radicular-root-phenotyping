#!/usr/bin/env python3
"""
Title:
    Rhizotron-level reanalysis and ordinal agreement
File type:
    Script
Purpose:
    Aggregates the blinded scores at rhizotron level (n=12) with paired tests and rhizotron
    bootstrap intervals and computes Krippendorff ordinal alpha and ICC(2,1)/ICC(3,1).
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
    - metricas/notas_recebidas
    - metricas/review_key.csv
Outputs:
    - metricas/08G_reanalise.csv
Dependencies:
    - numpy
    - openpyxl
    - scipy
    - local: config
Execution:
    python scripts/08G_reanalise.py (from a workspace prepared with tools/prepare_workspace.py)
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
Reanálise da avaliação cega (auditoria V2 e V3):
  V2 — dependência: agrega ao nível do RIZOTRON (unidade independente, n=12) e testa a
       preferência por M3 com Wilcoxon pareado + IC 95% por bootstrap de rizotron.
  V3 — concordância ORDINAL: alfa de Krippendorff (ordinal) e ICC(2,1)/ICC(3,1) das notas Q.
Reusa o parsing das fichas (9 avaliadores) e o gabarito review_key.
Saída: metricas/08G_reanalise.csv + impressão.
"""
import os, sys, csv, io, re, glob
import statistics as st
from collections import defaultdict
import numpy as np
from scipy.stats import wilcoxon
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

NOTAS = C.METRICAS / "notas_recebidas"
KEY = C.METRICAS / "review_key.csv"
NOTA_COLS = ["n0", "n1", "n2", "n3", "n4"]
XLSX_ORDER = ["image_id", "data", "codigo"] + NOTA_COLS + ["aceita", "p1", "p2", "p3", "p4", "obs"]
LAB = {"Frangi": "M1", "Ext": "M2", "Comb": "M3"}
RNG = np.random.default_rng(42)


def marcado(v):
    """
    Purpose:
        Test whether a spreadsheet cell is marked with x.
    Parameters:
        v: cell value
    Returns:
        bool
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return str(v).strip().lower() == "x"
def aceito(v):
    """
    Purpose:
        Test whether an acceptance cell records acceptance (x, sim, 1, yes, true or s).
    Parameters:
        v: cell value
    Returns:
        bool
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return str(v).strip().lower() in ("x", "sim", "1", "yes", "true", "s")
def qg(row):
    """
    Purpose:
        Return the 0-4 quality score of a judgement row from the marked score column.
    Parameters:
        row or r: judgement row (dict)
    Returns:
        int or None when no score is marked
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    for i, c in enumerate(NOTA_COLS):
        if marcado(row.get(c)): return i
    return None
def aval_nome(p):
    """
    Purpose:
        Derive the assessor label (A<n>) from the number in a sheet file name.
    Parameters:
        p: assessor sheet path
    Returns:
        str
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    m = re.search(r"(\d+)", os.path.splitext(os.path.basename(p))[0]); return f"A{m.group(1)}" if m else p


def ler_csv(f):
    """
    Purpose:
        Read an assessor sheet exported as CSV (comma or semicolon) into judgement rows.
    Parameters:
        f: path to the .csv sheet
    Returns:
        list of dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    raw = open(f, encoding="utf-8-sig").read()
    l0 = raw.splitlines()[0] if raw.splitlines() else ""
    delim = ";" if l0.count(";") > l0.count(",") else ","
    linhas = [r for r in csv.reader(io.StringIO(raw), delimiter=delim) if any(c.strip() for c in r)]
    return [{XLSX_ORDER[i]: (row[i] if i < len(row) else "") for i in range(min(len(XLSX_ORDER), len(row)))}
            for row in linhas[1:]]


def ler_xlsx(f):
    """
    Purpose:
        Read an assessor mark-x workbook into judgement rows mapped by column position.
    Parameters:
        f: path to the .xlsx sheet
    Returns:
        list of dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    ws = openpyxl.load_workbook(f, data_only=True).active
    out = []
    for r in ws.iter_rows(min_row=4, values_only=True):
        if not r or not r[0]: continue
        out.append({XLSX_ORDER[i]: (r[i] if i < len(r) else "") for i in range(len(XLSX_ORDER))})
    return out


def carregar_long():
    """
    Purpose:
        Load all judgements in long format joined with the answer key.
    Parameters:
        none
    Returns:
        list of dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    key = {(r["image_id"], r["codigo"]): LAB[r["metodo_real"]] for r in csv.DictReader(open(KEY, encoding="utf-8"))}
    files = sorted(glob.glob(str(NOTAS / "*.xlsx")) + glob.glob(str(NOTAS / "*.csv")))
    rows = []
    for f in files:
        av = aval_nome(f)
        got = ler_xlsx(f) if f.lower().endswith(".xlsx") else ler_csv(f)
        for r in got:
            q = qg(r); met = key.get((r["image_id"], r["codigo"]))
            if q is not None and met:
                rows.append({"aval": av, "img": r["image_id"], "riz": r["image_id"].split("_")[0],
                             "met": met, "Q": q, "aceita": 1 if aceito(r.get("aceita")) else 0})
    return rows


def krippendorff_ordinal(matrix):
    """matrix: dict item -> list de notas (0-4), permitindo m<k. Alfa ordinal (5 categorias)."""
    K = 5
    o = np.zeros((K, K))
    for vals in matrix.values():
        m = len(vals)
        if m < 2: continue
        for i in range(m):
            for j in range(m):
                if i != j:
                    o[vals[i]][vals[j]] += 1.0 / (m - 1)
    nc = o.sum(axis=1); n = nc.sum()
    if n < 2: return None
    def delta2(c, k):
        if c == k: return 0.0
        a, b = min(c, k), max(c, k)
        s = nc[a] / 2 + nc[b] / 2 + sum(nc[g] for g in range(a + 1, b))
        return s * s
    Do = sum(o[c][k] * delta2(c, k) for c in range(K) for k in range(K)) / n
    De = sum(nc[c] * nc[k] * delta2(c, k) for c in range(K) for k in range(K)) / (n * (n - 1))
    return 1 - Do / De if De > 0 else None


def icc(mat):
    """mat: array items×raters (completo). Retorna ICC(2,1) abs e ICC(3,1) consist."""
    Y = np.asarray(mat, float); n, k = Y.shape
    gm = Y.mean()
    MSR = k * ((Y.mean(1) - gm) ** 2).sum() / (n - 1)
    MSC = n * ((Y.mean(0) - gm) ** 2).sum() / (k - 1)
    SSE = ((Y - Y.mean(1, keepdims=True) - Y.mean(0, keepdims=True) + gm) ** 2).sum()
    MSE = SSE / ((n - 1) * (k - 1))
    icc21 = (MSR - MSE) / (MSR + (k - 1) * MSE + k * (MSC - MSE) / n)
    icc31 = (MSR - MSE) / (MSR + (k - 1) * MSE)
    return icc21, icc31


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
    L = carregar_long()
    avs = sorted(set(r["aval"] for r in L)); rizs = sorted(set(r["riz"] for r in L))
    print(f"[08G] {len(L)} julgamentos | {len(avs)} avaliadores | {len(rizs)} rizotrons")

    # ---- V2: nível do rizotron ----
    # Q por (img,met) = média dos avaliadores; depois média por (riz,met)
    by_im = defaultdict(lambda: defaultdict(list))
    ac_im = defaultdict(lambda: defaultdict(list))
    for r in L:
        by_im[(r["img"], r["met"])]["Q"].append(r["Q"]); ac_im[(r["img"], r["met"])]["a"].append(r["aceita"])
    imgQ = {k: st.mean(v["Q"]) for k, v in by_im.items()}
    imgA = {k: st.mean(v["a"]) for k, v in ac_im.items()}
    rizQ = defaultdict(dict); rizA = defaultdict(dict)
    imgs_of = defaultdict(set)
    for (img, met) in imgQ: imgs_of[met].add(img)
    for met in ("M1", "M2", "M3"):
        for riz in rizs:
            qs = [imgQ[(im, met)] for im in imgs_of[met] if im.split("_")[0] == riz]
            as_ = [imgA[(im, met)] for im in imgs_of[met] if im.split("_")[0] == riz]
            rizQ[riz][met] = st.mean(qs); rizA[riz][met] = st.mean(as_)
    out = []
    print("\nV2 — nível do rizotron (n=12), Q médio por método:")
    for met in ("M1", "M2", "M3"):
        vals = [rizQ[r][met] for r in rizs]
        print(f"    {met}: {st.mean(vals):.3f} ± {st.stdev(vals):.3f}")
    for a, b in [("M3", "M1"), ("M3", "M2"), ("M1", "M2")]:
        d = np.array([rizQ[r][a] - rizQ[r][b] for r in rizs])
        W, p = wilcoxon(d)
        bs = np.array([d[RNG.integers(0, len(d), len(d))].mean() for _ in range(10000)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        sig = "" if lo <= 0 <= hi else "  *IC exclui 0"
        print(f"    {a}-{b}: Δ={d.mean():+.3f} IC95[{lo:+.3f},{hi:+.3f}] Wilcoxon p={p:.4f}{sig}")
        out.append({"analise": "V2_rizotron", "contraste": f"{a}-{b}", "delta_Q": round(d.mean(), 3),
                    "IC_lo": round(lo, 3), "IC_hi": round(hi, 3), "wilcoxon_p": round(p, 4)})
    # aceitação por rizotron
    for a, b in [("M3", "M1"), ("M3", "M2")]:
        d = np.array([rizA[r][a] - rizA[r][b] for r in rizs])
        W, p = wilcoxon(d)
        print(f"    aceitação {a}-{b}: Δ={d.mean():+.3f} Wilcoxon p={p:.4f}")
        out.append({"analise": "V2_aceita", "contraste": f"{a}-{b}", "delta_Q": round(d.mean(), 3),
                    "IC_lo": "", "IC_hi": "", "wilcoxon_p": round(p, 4)})

    # ---- V3: concordância ordinal ----
    mat = defaultdict(dict)                       # item (img,met) -> {aval: Q}
    for r in L: mat[(r["img"], r["met"])][r["aval"]] = r["Q"]
    kmat = {k: list(v.values()) for k, v in mat.items()}
    alpha = krippendorff_ordinal(kmat)
    completos = [[v[a] for a in avs] for v in mat.values() if all(a in v for a in avs)]
    icc21, icc31 = icc(completos) if len(completos) > 2 else (None, None)
    print(f"\nV3 — concordância ordinal:")
    print(f"    Krippendorff alpha (ordinal) = {alpha:.3f}")
    print(f"    ICC(2,1) concordância absoluta = {icc21:.3f} | ICC(3,1) consistência = {icc31:.3f}  (itens completos={len(completos)})")
    out += [{"analise": "V3", "contraste": "krippendorff_ordinal", "delta_Q": round(alpha, 3), "IC_lo": "", "IC_hi": "", "wilcoxon_p": ""},
            {"analise": "V3", "contraste": "ICC(2,1)_abs", "delta_Q": round(icc21, 3), "IC_lo": "", "IC_hi": "", "wilcoxon_p": ""},
            {"analise": "V3", "contraste": "ICC(3,1)_consist", "delta_Q": round(icc31, 3), "IC_lo": "", "IC_hi": "", "wilcoxon_p": ""}]

    with open(C.METRICAS / "08G_reanalise.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print("\n-> metricas/08G_reanalise.csv")


if __name__ == "__main__":
    main()
