#!/usr/bin/env python3
"""
Title:
    Permutation importance and model summary
File type:
    Script
Purpose:
    Computes signed permutation importance by variable and joint permutation by source in the full
    Ridge model, coherence summaries and copies model_performance.csv to model_comparison.csv.
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
    - metricas/ablation_group.csv
    - metricas/multimodal_long.csv
Outputs:
    - metricas/explainability_by_group.csv
    - metricas/explainability_coherence.csv
    - metricas/explainability_results.csv
    - metricas/model_comparison.csv
    - metricas/model_performance.csv
    - metricas/model_predictions.csv
    - metricas/predictions_by_rhizotron.csv
Dependencies:
    - numpy
    - scipy
    - sklearn
    - local: config
Execution:
    python scripts/15_explicabilidade.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 15 (parte A) — Explicabilidade e interpretação.

Importância por PERMUTAÇÃO no modelo completo (Ridge, comum aos alvos, escolhido pela
estabilidade/interpretabilidade — não necessariamente o de menor MAE de cada alvo):
  - por VARIÁVEL: PI assinado (aumento de MAE ao permutar; negativo = instabilidade/ruído);
  - por FONTE (óptica/elétrica/manejo): permutação CONJUNTA do grupo (preserva a correlação
    interna de features redundantes, p.ex. R/ρ/σ), evitando o viés de somar |PI| de grupos
    com nº desigual de variáveis.
Importância calculada IN-SAMPLE nos 12 rizotrons (leitura otimista; diagnóstica).
Coerência: corr(Δ_fonte da ablação, I_fonte da permutação conjunta) — poucas fontes, descritivo.

Entrada: metricas/multimodal_long.csv, metricas/ablation_group.csv
Saídas:
  metricas/explainability_results.csv    (PI assinado por variável, por alvo)
  metricas/explainability_by_group.csv   (I por fonte: permutação conjunta)
  metricas/explainability_coherence.csv  (corr Δ_fonte × I_fonte por alvo)
  metricas/model_comparison.csv          (consolidação do desempenho, Fase 13)
  metricas/predictions_by_rhizotron.csv  (predições finais por rizotron, Fase 13)
"""
import os
import sys
import csv
import shutil
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from scipy.stats import spearmanr

LONG = C.METRICAS / "multimodal_long.csv"
ALVOS = ["y_M_r", "y_M_a"]
# CONJUNTO CANÔNICO (idêntico em 13/14/15): sem A (colinear com O), sem R/rho_a (redundantes com sigma).
MEANS = ["O_ocupacao", "L_skel_px", "N_br", "sigma_a"]
SLOPES = ["O_ocupacao", "L_skel_px", "sigma_a"]
# Grupo experimental como FATOR CATEGÓRICO: três contrastes binários com REF como
# categoria-base (ver 13_modelagem.py). A codificação ordinal anterior impunha
# relação linear entre REF, T1, T2 e T3, sem justificativa experimental.
TRAT_NIVEIS = ["T1", "T2", "T3"]
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

# fontes mutuamente exclusivas (cada feature = uma única fonte)
SOURCE = {
    "optical": ["O_ocupacao_m", "L_skel_px_m", "N_br_m", "O_ocupacao_s", "L_skel_px_s"],
    "electrical": ["sigma_a_m", "sigma_a_s"],
    "management": ["trat_T1", "trat_T2", "trat_T3"],
}
KEYS = SOURCE["optical"] + SOURCE["electrical"] + SOURCE["management"]
FONTE = {k: s for s, ks in SOURCE.items() for k in ks}
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
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


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


def mae(y, yhat):
    """
    Purpose:
        Mean absolute error.
    Parameters:
        y: observed
        yhat: predicted
    Returns:
        float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(yhat))))


def group_perm_importance(model, X, y, idx, n_repeats=100):
    """Permuta CONJUNTAMENTE as colunas 'idx' (mesma permutação de linhas) e retorna o
    aumento médio (assinado) de MAE e o desvio."""
    base = mae(y, model.predict(X))
    incs = []
    for _ in range(n_repeats):
        Xp = X.copy()
        perm = RNG.permutation(len(y))
        Xp[:, idx] = X[np.ix_(perm, idx)]
        incs.append(mae(y, model.predict(Xp)) - base)
    return float(np.mean(incs)), float(np.std(incs))


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
    feats = []
    for riz in rizs:
        f = construir(serie[riz]); f.update(trat_contrastes(trat[riz])); feats.append(f)
    X = np.array([[f[k] for k in KEYS] for f in feats], float)
    Xs = StandardScaler().fit_transform(X)

    pi_rows, grp_rows, coer_rows = [], [], []
    # ablação por fonte (Fase 14) p/ coerência
    abl = defaultdict(dict)
    for r in csv.DictReader(open(C.METRICAS / "ablation_group.csv", encoding="utf-8")):
        abl[r["alvo"]][r["grupo_removido"]] = float(r["delta"])

    for a in ALVOS:
        y = np.array([alvo[riz][a] for riz in rizs], float)
        model = Ridge(alpha=10.0).fit(Xs, y)
        # por variável: PI ASSINADO (não |PI|)
        r = permutation_importance(model, Xs, y, scoring="neg_mean_absolute_error",
                                   n_repeats=100, random_state=42)
        for k, pi, sd in zip(KEYS, r.importances_mean, r.importances_std):
            pi_rows.append({"alvo": a, "variavel": k, "fonte": FONTE[k],
                            "PI": round(float(pi), 4), "PI_std": round(float(sd), 4)})
        # por FONTE: permutação conjunta do grupo (assinada)
        I_src = {}
        for s, ks in SOURCE.items():
            idx = [KEYS.index(k) for k in ks]
            I, Isd = group_perm_importance(model, Xs, y, idx)
            I_src[s] = I
            grp_rows.append({"alvo": a, "tipo": "fonte", "grupo": s,
                             "I": round(I, 4), "I_std": round(Isd, 4)})
        # coerência: corr(Δ_fonte, I_fonte) sobre as 3 fontes
        fontes = ["optical", "electrical", "management"]
        dg = [abl[a].get(g, 0) for g in fontes]
        ig = [I_src.get(g, 0) for g in fontes]
        rho, p = spearmanr(dg, ig)
        coer_rows.append({"alvo": a, "fontes": "/".join(fontes),
                          "corr_delta_vs_I": round(float(rho), 3) if rho == rho else "",
                          "p": round(float(p), 3) if p == p else ""})

    with open(C.METRICAS / "explainability_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pi_rows[0].keys())); w.writeheader(); w.writerows(pi_rows)
    with open(C.METRICAS / "explainability_by_group.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(grp_rows[0].keys())); w.writeheader(); w.writerows(grp_rows)
    with open(C.METRICAS / "explainability_coherence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(coer_rows[0].keys())); w.writeheader(); w.writerows(coer_rows)

    shutil.copyfile(C.METRICAS / "model_performance.csv", C.METRICAS / "model_comparison.csv")
    shutil.copyfile(C.METRICAS / "model_predictions.csv", C.METRICAS / "predictions_by_rhizotron.csv")

    print("[Fase 15A] Importância por permutação (Ridge comum; in-sample, n=12):")
    for a in ALVOS:
        top = sorted([r for r in pi_rows if r["alvo"] == a], key=lambda r: -r["PI"])[:4]
        print(f"  {a}: " + ", ".join(f"{r['variavel']}({r['fonte']},PI={r['PI']:+.3f})" for r in top))
        src = {r["grupo"]: r["I"] for r in grp_rows if r["alvo"] == a}
        print(f"     importância por fonte (permutação conjunta): "
              + " ".join(f"{k}={v:+.3f}" for k, v in sorted(src.items(), key=lambda x: -x[1])))
        c = [r for r in coer_rows if r["alvo"] == a][0]
        print(f"     coerência ablação×importância (3 fontes): rho={c['corr_delta_vs_I']}")
    print("   Saídas: explainability_results/by_group/coherence.csv, model_comparison.csv, predictions_by_rhizotron.csv")


if __name__ == "__main__":
    main()
