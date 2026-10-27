#!/usr/bin/env python3
"""
Title:
    Stability of M3 advantage across image conditions
File type:
    Script
Purpose:
    Contrasts M3 against M1 and M2 within image-defined strata at rhizotron level and fits mixed-
    effects acceptance models with method-by-condition interactions and clustered intervals.
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
    - metricas/image_qc.csv
    - metricas/notas_recebidas
    - metricas/pretratamento_05A.csv
    - metricas/review_key.csv
    - metricas/root_features_by_image.csv
Outputs:
    - metricas/A7_logistico.csv
    - metricas/A7_resiliencia.csv
    - metricas/A7_tratamento.csv
Dependencies:
    - numpy
    - openpyxl
    - pandas
    - scipy
    - statsmodels
    - local: config
Execution:
    python scripts/A7_resiliencia.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Verification in v1.0.0: re-executed; A7_resiliencia.csv and
    A7_tratamento.csv byte-identical; A7_logistico.csv differs by at most 1.05e-4 (relative) in GLMM
    estimates, with no difference at the published precision. Environment of the verification:
    Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Resultado adicional A7 — estabilidade da vantagem de M3 entre condições de imagem.
Pergunta: a preferência por M3 (nota Q e aceitação) permanece após estratificar por condições
INDEPENDENTES DA SEGMENTAÇÃO (reflexo G_c, DAP, brilho, contraste, nitidez) e após controlar a
dependência entre avaliadores, imagens e rizotrons? Usa os 2214 julgamentos cegos.

A7.1 (PRIMÁRIO) — contraste pareado M3−M1 e M3−M2 no nível do RIZOTRON (n=12, unidade
     independente), global e por estrato de condição de aquisição, com cluster bootstrap (IC95%).
A7.2 (CONFIRMATÓRIO) — logístico misto da aceitação (BinomialBayesMixedGLM) com interceptos
     aleatórios de avaliador, imagem, RIZOTRON e avaliador:imagem (pareamento dos 3 métodos).
     OR ajustados (M1,M2 vs M3) + interações método×condição predefinidas, com incerteza
     CLUSTERIZADA por rizotron (bootstrap refit) e correção de multiplicidade (Holm).
SECUNDÁRIO/diagnóstico — estrato e interação pela OCUPAÇÃO ESTIMADA POR M3 (derivada do próprio
     método → circular; teto inferencial menor, apresentado junto de A1/A5).
SUPLEMENTO — estratos por tratamento (n=3 rizotrons/grupo; descritivo, com pontos individuais).
Saídas: A7_resiliencia.csv (contrastes/condição) + A7_logistico.csv (OR+IC+p+Holm) + A7_tratamento.csv.
"""
import os, sys, csv, io, re, glob, warnings
import statistics as st
from collections import defaultdict
import numpy as np, pandas as pd
from scipy.stats import norm
import statsmodels.api as sm
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

NOTAS = C.METRICAS / "notas_recebidas"
KEY = C.METRICAS / "review_key.csv"
NOTA_COLS = ["n0", "n1", "n2", "n3", "n4"]
XO = ["image_id", "data", "codigo"] + NOTA_COLS + ["aceita", "p1", "p2", "p3", "p4", "obs"]
LAB = {"Frangi": "M1", "Ext": "M2", "Comb": "M3"}
RNG = np.random.default_rng(42)
NBOOT = 5000
NBOOT_INT = 1000


def marc(v):
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
def qg(r):
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
        if marc(r.get(c)): return i
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
    raw = open(f, encoding="utf-8-sig").read(); l0 = raw.splitlines()[0] if raw.splitlines() else ""
    d = ";" if l0.count(";") > l0.count(",") else ","
    L = [r for r in csv.reader(io.StringIO(raw), delimiter=d) if any(c.strip() for c in r)]
    return [{XO[i]: (row[i] if i < len(row) else "") for i in range(min(len(XO), len(row)))} for row in L[1:]]
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
    import openpyxl
    ws = openpyxl.load_workbook(f, data_only=True).active
    return [{XO[i]: (r[i] if i < len(r) else "") for i in range(len(XO))}
            for r in ws.iter_rows(min_row=4, values_only=True) if r and r[0]]


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
    rows = []
    for f in sorted(glob.glob(str(NOTAS / "*.xlsx")) + glob.glob(str(NOTAS / "*.csv"))):
        av = aval_nome(f)
        for r in (ler_xlsx(f) if f.lower().endswith(".xlsx") else ler_csv(f)):
            q = qg(r); met = key.get((r["image_id"], r["codigo"]))
            if q is not None and met:
                rows.append({"aval": av, "img": r["image_id"], "riz": r["image_id"].split("_")[0],
                             "met": met, "Q": q, "aceita": 1 if aceito(r.get("aceita")) else 0})
    return rows


def covariaveis():
    """
    Purpose:
        Load image covariates (G_c, DAP, brightness, contrast, sharpness, M3 occupancy).
    Parameters:
        none
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    qc = {r["image_id"]: r for r in csv.DictReader(open(C.METRICAS / "image_qc.csv", encoding="utf-8"))}
    pre = {r["image_id"]: r for r in csv.DictReader(open(C.METRICAS / "pretratamento_05A.csv", encoding="utf-8"))}
    rf = {r["image_id"]: r for r in csv.DictReader(open(C.METRICAS / "root_features_by_image.csv", encoding="utf-8"))}
    cov = {}
    for k in qc:
        if k in pre and k in rf:
            cov[k] = {"Gc": float(qc[k]["G_c"]), "brilho": float(qc[k]["R_c"]), "contraste": float(qc[k]["sigma_L"]),
                      "nitidez": float(qc[k]["B"]), "DAP": float(rf[k]["DAP"]),
                      "ocupM3": float(rf[k]["O_ocupacao"]), "trat": rf[k]["tratamento"]}
    return cov


def cluster_boot(riz_vals):
    """
    Purpose:
        Rhizotron bootstrap of a mean.
    Parameters:
        riz_vals: per-rhizotron values
    Returns:
        tuple (mean, low, high, n)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    v = np.array([x for x in riz_vals if x is not None])
    if len(v) < 2: return (np.nan, np.nan, np.nan, len(v))
    idx = RNG.integers(0, len(v), size=(NBOOT, len(v)))
    boot = v[idx].mean(axis=1)
    return (float(v.mean()), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)), len(v))


def contraste_por_riz(L, imgs_ok, campo, alvo, ref):
    """
    Purpose:
        Per-rhizotron contrast between methods within an image subset.
    Parameters:
        L: judgements
        imgs_ok: image subset
        campo: score or acceptance
        alvo: method
        ref: reference method
    Returns:
        list
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    by = defaultdict(lambda: defaultdict(list))
    for r in L:
        if r["img"] in imgs_ok:
            by[r["riz"]][r["met"]].append(r[campo])
    return [st.mean(d[alvo]) - st.mean(d[ref]) for d in by.values() if alvo in d and ref in d]


def holm(pvals):
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
    order = sorted(range(len(pvals)), key=lambda i: pvals[i]); m = len(pvals); adj = [0.0] * m
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * pvals[i]); adj[i] = min(1.0, run)
    return adj


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
    cov = covariaveis()
    imgs = sorted(cov)
    nriz_tot = len(set(r["riz"] for r in L))
    print(f"[A7] {len(L)} julgamentos | {len(imgs)} imagens | {nriz_tot} rizotrons")

    med = {c: st.median([cov[i][c] for i in imgs]) for c in ("Gc", "DAP", "brilho", "contraste", "nitidez", "ocupM3")}
    print("[A7] limiares (mediana): " + ", ".join(f"{c}={med[c]:.4g}" for c in med))

    # estratos: PRIMÁRIO (independentes da segmentação) + SECUNDÁRIO (ocupação de M3)
    prim = [("Global", set(imgs)),
            ("Reflexo G_c alto", {i for i in imgs if cov[i]["Gc"] > med["Gc"]}),
            ("Reflexo G_c baixo", {i for i in imgs if cov[i]["Gc"] <= med["Gc"]}),
            ("DAP tardio", {i for i in imgs if cov[i]["DAP"] > med["DAP"]}),
            ("DAP inicial", {i for i in imgs if cov[i]["DAP"] <= med["DAP"]}),
            ("Brilho alto", {i for i in imgs if cov[i]["brilho"] > med["brilho"]}),
            ("Brilho baixo", {i for i in imgs if cov[i]["brilho"] <= med["brilho"]}),
            ("Contraste alto", {i for i in imgs if cov[i]["contraste"] > med["contraste"]}),
            ("Contraste baixo", {i for i in imgs if cov[i]["contraste"] <= med["contraste"]}),
            ("Nitidez alta", {i for i in imgs if cov[i]["nitidez"] > med["nitidez"]}),
            ("Nitidez baixa", {i for i in imgs if cov[i]["nitidez"] <= med["nitidez"]})]
    sec = [("Ocup. M3 alta [sec]", {i for i in imgs if cov[i]["ocupM3"] > med["ocupM3"]}),
           ("Ocup. M3 baixa [sec]", {i for i in imgs if cov[i]["ocupM3"] <= med["ocupM3"]})]

    def bloco(estratos):
        out = []
        for nome, S in estratos:
            if not S: continue
            r = {"condicao": nome, "n_img": len(S), "n_riz": len({i.split("_")[0] for i in S})}
            for campo, tag in [("Q", "Q"), ("aceita", "acc")]:
                for ref in ("M1", "M2"):
                    m, lo, hi, nr = cluster_boot(contraste_por_riz(L, S, campo, "M3", ref))
                    r[f"d{tag}_M3_{ref}"] = round(m, 3); r[f"d{tag}_M3_{ref}_lo"] = round(lo, 3); r[f"d{tag}_M3_{ref}_hi"] = round(hi, 3)
            out.append(r)
            print(f"  {nome:20s} nI={r['n_img']:2d} nR={r['n_riz']:2d} | "
                  f"ΔQ M3-M1={r['dQ_M3_M1']:+.2f}[{r['dQ_M3_M1_lo']:+.2f},{r['dQ_M3_M1_hi']:+.2f}] "
                  f"M3-M2={r['dQ_M3_M2']:+.2f}[{r['dQ_M3_M2_lo']:+.2f},{r['dQ_M3_M2_hi']:+.2f}] | "
                  f"Δacc M3-M1={r['dacc_M3_M1']:+.2f}[{r['dacc_M3_M1_lo']:+.2f},{r['dacc_M3_M1_hi']:+.2f}] "
                  f"M3-M2={r['dacc_M3_M2']:+.2f}[{r['dacc_M3_M2_lo']:+.2f},{r['dacc_M3_M2_hi']:+.2f}]")
        return out

    print("\n[A7.1] Contraste pareado M3−outro, nível do rizotron, IC95% cluster bootstrap — PRIMÁRIO")
    rows_out = bloco(prim)
    print("\n[A7.1-sec] Estrato pela ocupação estimada por M3 (SECUNDÁRIO/diagnóstico — circular)")
    rows_out += bloco(sec)
    with open(C.METRICAS / "A7_resiliencia.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys())); w.writeheader(); w.writerows(rows_out)

    # estratos por tratamento -> suplemento (descritivo, pontos individuais por rizotron)
    print("\n[A7-supp] Tratamento (n=3 rizotrons/grupo; DESCRITIVO, pontos individuais)")
    trat_rows = []
    for t in ("REF", "T1", "T2", "T3"):
        S = {i for i in imgs if cov[i]["trat"] == t}
        for ref in ("M1", "M2"):
            vals = contraste_por_riz(L, S, "Q", "M3", ref)
            trat_rows.append({"trat": t, "contraste": f"M3-{ref}", "n_riz": len(vals),
                              "valores_por_rizotron": ";".join(f"{v:+.2f}" for v in sorted(vals)),
                              "media": round(st.mean(vals), 3) if vals else ""})
            print(f"  {t} M3-{ref}: {[round(v,2) for v in sorted(vals)]}")
    with open(C.METRICAS / "A7_tratamento.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(trat_rows[0].keys())); w.writeheader(); w.writerows(trat_rows)

    # ---- A7.2 logístico misto (aceitação) ----
    df = pd.DataFrame(L)
    for c in ("Gc", "DAP", "brilho", "contraste", "nitidez", "ocupM3"):
        df[c] = df["img"].map(lambda i: cov[i][c])
        df["z_" + c] = (df[c] - df[c].mean()) / df[c].std()
    df["avalimg"] = df["aval"] + ":" + df["img"]
    df["met"] = pd.Categorical(df["met"], categories=["M3", "M1", "M2"])
    vc = {"aval": "0 + C(aval)", "img": "0 + C(img)", "riz": "0 + C(riz)", "avalimg": "0 + C(avalimg)"}

    def glmm(formula, label):
        res = sm.BinomialBayesMixedGLM.from_formula(formula, vc, df).fit_vb()
        print(f"\n[A7.2] {label}")
        out = []
        for name, mean, sd in zip(res.model.exog_names, res.fe_mean, res.fe_sd):
            if name == "Intercept": continue
            z = mean / sd; p = 2 * norm.sf(abs(z))
            lo, hi = mean - 1.96 * sd, mean + 1.96 * sd
            out.append({"modelo": label, "termo": name, "OR": float(np.exp(mean)),
                        "OR_lo": float(np.exp(lo)), "OR_hi": float(np.exp(hi)), "p": float(p)})
            print(f"   {name:26s} OR={np.exp(mean):5.3f} [{np.exp(lo):5.3f},{np.exp(hi):5.3f}] p={p:.3g}")
        return out

    logit_rows = glmm("aceita ~ C(met) + z_Gc + z_DAP + z_brilho + z_contraste + z_nitidez",
                      "Estabilidade ajustada (M1,M2 vs M3; covariáveis p/ M3)")
    inter = []
    inter += glmm("aceita ~ C(met) * z_Gc", "Interação método×reflexo(G_c)")
    inter += glmm("aceita ~ C(met) * z_DAP", "Interação método×DAP")
    inter += glmm("aceita ~ C(met) * z_ocupM3", "Interação método×ocupação-M3 [secundário]")

    # Holm sobre os 6 termos de interação (2 contrastes × 3 condições)
    it = [r for r in inter if ":" in r["termo"]]
    padj = holm([r["p"] for r in it])
    for r, pa in zip(it, padj): r["p_holm"] = pa
    print("\n[A7.2] Interações após Holm (6 testes):")
    for r in it:
        print(f"   {r['modelo'].split('×')[1]:22s} {r['termo']:26s} OR={r['OR']:.3f} "
              f"[{r['OR_lo']:.3f},{r['OR_hi']:.3f}] p={r['p']:.3g} Holm={r['p_holm']:.3g}"
              f"{'  *' if r['p_holm']<0.05 else ''}")

    # incerteza CLUSTERIZADA por rizotron para as interações (bootstrap refit logit FE)
    print("\n[A7.2] IC95% clusterizado por rizotron (bootstrap refit, logit FE) p/ termos de interação:")
    # NB: fórmula sem C() — 'met' já é Categorical; C colide com o módulo config importado como C.
    rizs = sorted(df["riz"].unique())
    for zc, cond in [("z_Gc", "reflexo(G_c)"), ("z_DAP", "DAP"), ("z_ocupM3", "ocupação-M3")]:
        boots = {"M1": [], "M2": []}
        for _ in range(NBOOT_INT):
            take = RNG.choice(rizs, size=len(rizs), replace=True)
            sub = pd.concat([df[df["riz"] == rz] for rz in take], ignore_index=True)
            try:
                r = smf.logit(f"aceita ~ met * {zc}", data=sub).fit(disp=0, maxiter=50)
                for tag in ("M1", "M2"):
                    k = f"met[T.{tag}]:{zc}"
                    if k in r.params.index: boots[tag].append(r.params[k])
            except Exception:
                continue
        for tag in ("M1", "M2"):
            b = boots[tag]
            if len(b) > 50:
                lo, hi = np.percentile(b, [2.5, 97.5]); m = np.median(b)
                print(f"   {cond:16s} met[T.{tag}]:{zc:9s} OR_med={np.exp(m):.3f} "
                      f"[{np.exp(lo):.3f},{np.exp(hi):.3f}]{'  *' if (lo>0 or hi<0) else ''}")
                for rr in it:
                    if rr["termo"] == f"C(met)[T.{tag}]:{zc}":
                        rr["OR_clusterboot_lo"] = round(float(np.exp(lo)), 4)
                        rr["OR_clusterboot_hi"] = round(float(np.exp(hi)), 4)

    with open(C.METRICAS / "A7_logistico.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["modelo", "termo", "OR", "OR_lo", "OR_hi", "p", "p_holm", "OR_clusterboot_lo", "OR_clusterboot_hi"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(logit_rows + inter)
    print("\n[A7] -> A7_resiliencia.csv + A7_logistico.csv + A7_tratamento.csv")
    m1 = next(r for r in logit_rows if r["termo"] == "C(met)[T.M1]"); m2 = next(r for r in logit_rows if r["termo"] == "C(met)[T.M2]")
    print(f"      M3 vs M1: chances de M1 = {m1['OR']:.3f} das de M3 (≈{1/m1['OR']:.1f}× a favor de M3); "
          f"M3 vs M2: {m2['OR']:.3f} (≈{1/m2['OR']:.1f}×).")


if __name__ == "__main__":
    main()
