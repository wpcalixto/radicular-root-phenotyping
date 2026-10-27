#!/usr/bin/env python3
"""
Title:
    Predictive modelling of final outcomes
File type:
    Script
Purpose:
    Predicts final root and shoot mass and their ratio from features accumulated up to each horizon
    with leave-one-rhizotron-out validation for Ridge, Lasso, PLS, Random Forest, SVR and mean
    baselines.
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
    - metricas/model_horizon.csv
    - metricas/model_performance.csv
    - metricas/model_predictions.csv
Dependencies:
    - numpy
    - sklearn
    - local: config
Execution:
    python scripts/13_modelagem.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 13 — Modelagem preditiva dos desfechos radiculares finais.

Prevê os alvos finais (M_r massa radicular, M_a massa aérea, R_a/r razão) a partir de
features acumuladas até o horizonte temporal h (predição precoce). Validação por
**Leave-One-Rhizotron-Out** (n=12 unidades experimentais → sem vazamento entre coletas
do mesmo rizotron). Modelos tabulares para dados pequenos: Ridge, Lasso, PLS, Random
Forest, SVR + baseline (média). Métricas: MAE, RMSE, R², MAPE.

ATENÇÃO (honestidade): n=12 é MUITO pequeno; R² pode ser ≤ 0 (pior que a média). O valor
está no arcabouço (predição precoce por horizonte) e em identificar o alvo/horizonte mais
previsível — não em acurácia alta. Reportar com cautela.

Feature por (rizotron, h): para variáveis-chave (L_skel, ocupação, ramificação, σ),
média e inclinação sobre as coletas 1..h + tratamento (ordinal). Conjunto fixo (sem
seleção de features p/ evitar otimismo).

Entrada: metricas/multimodal_long.csv
Saídas:
  metricas/model_performance.csv     (alvo × horizonte × modelo: MAE, RMSE, R2, MAPE)
  metricas/model_predictions.csv     (melhor modelo por alvo no horizonte final: y, y_hat)
  metricas/model_horizon.csv         (E_h e reducao relativa RR_h por alvo/modelo)
"""
import os
import sys
import csv
import statistics as st
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from sklearn.linear_model import Ridge, Lasso
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from sklearn.preprocessing import StandardScaler

LONG = C.METRICAS / "multimodal_long.csv"
ALVOS = ["y_M_r", "y_M_a", "y_R_ar"]
# CONJUNTO CANÔNICO (idêntico em 13/14/15): óptica {O, L_skel, N_br}, elétrica {sigma},
# manejo {tratamento}. A (colinear com O), R e rho_a (redundantes com sigma) NÃO entram.
VARS = ["O_ocupacao", "L_skel_px", "N_br", "sigma_a"]   # variáveis para carregar a série
MEANS_F = ["O_ocupacao", "L_skel_px", "N_br", "sigma_a"]  # médias (nível)
SLOPES_F = ["O_ocupacao", "L_skel_px", "sigma_a"]         # inclinações (dinâmica)
# Grupo experimental como FATOR CATEGÓRICO: três contrastes binários com REF como
# categoria-base. A codificação ordinal anterior impunha relação linear e monotônica
# entre REF, T1, T2 e T3, sem justificativa: REF é ausência de adubação, enquanto os
# tratamentos diferem pela ÉPOCA de aplicação, não por uma dose crescente.
TRAT_NIVEIS = ["T1", "T2", "T3"]          # REF = categoria-base (todos os contrastes = 0)
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
    return [1.0 if t == n else 0.0 for n in TRAT_NIVEIS]
EPS = 1e-9


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


def modelos():
    """
    Purpose:
        Return the dictionary of candidate regressors.
    Parameters:
        none
    Returns:
        dict name -> estimator
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return {
        "baseline_media": DummyRegressor(strategy="mean"),
        "Ridge": Ridge(alpha=10.0),
        "Lasso": Lasso(alpha=0.5, max_iter=10000),
        "PLS": PLSRegression(n_components=2),
        "RandomForest": RandomForestRegressor(n_estimators=300, max_depth=3, random_state=42),
        "SVR": SVR(kernel="rbf", C=1.0, gamma="scale"),
    }


def features_horizonte(serie, h):
    """serie = lista (coleta, DAP, {var:val}) ordenada; usa coletas com num <= h.
    Constrói o MESMO vetor canônico de 14/15: médias de MEANS_F + inclinações de SLOPES_F
    (em h=1 não há inclinação estimável -> 0) + tratamento."""
    pts = [(dap, s) for (ck, dap, s) in serie if ck != "" and int(ck) <= h]
    if not pts:
        return None
    feat = []
    for v in MEANS_F:
        xs = [s[v] for _, s in pts if s[v] is not None]
        feat.append(float(np.mean(xs)) if xs else 0.0)
    for v in SLOPES_F:
        xy = [(d, s[v]) for d, s in pts if s[v] is not None]
        feat.append(float(np.polyfit([a for a, _ in xy], [b for _, b in xy], 1)[0]) if len(xy) >= 2 else 0.0)
    return feat


def loro(Xy, modelo):
    """Leave-one-out (n=12). Retorna y_true, y_pred alinhados."""
    X = np.array([x for x, _ in Xy]); y = np.array([t for _, t in Xy])
    yt, yp = [], []
    for i in range(len(y)):
        tr = [j for j in range(len(y)) if j != i]
        sc = StandardScaler().fit(X[tr])
        m = modelo.__class__(**modelo.get_params())
        m.fit(sc.transform(X[tr]), y[tr])
        pred = m.predict(sc.transform(X[i:i + 1]))
        yp.append(float(np.ravel(pred)[0])); yt.append(float(y[i]))
    return np.array(yt), np.array(yp)


def metricas(yt, yp):
    """
    Purpose:
        Compute MAE, RMSE, R2 and MAPE.
    Parameters:
        yt: observed values
        yp: predicted values
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    err = yt - yp
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    ss = float(np.sum((yt - yt.mean()) ** 2))
    r2 = 1 - float(np.sum(err ** 2)) / ss if ss > 0 else float("nan")
    mape = float(np.mean(np.abs(err / (yt + EPS)))) * 100
    return mae, rmse, r2, mape


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
        s = {v: fnum(r.get(v)) for v in VARS}
        serie[r["rizotron"]].append((r["coleta"], fnum(r["DAP"]), s))
        trat[r["rizotron"]] = r["tratamento"]
        for a in ALVOS:
            alvo[r["rizotron"]][a] = fnum(r.get(a))
    for riz in serie:
        serie[riz].sort(key=lambda t: (int(t[0]) if t[0] != "" else 99))

    rizs = sorted(serie)
    Hs = list(range(1, 7))   # janela multimodal comum C1-C6 (C7 é óptica-only; R1/R12 sem C7)
    perf_rows, hor_rows, pred_rows = [], [], []
    E1 = {}   # erro no horizonte 1 (p/ RR_h), por (alvo, modelo)

    for a in ALVOS:
        for h in Hs:
            Xy = []
            for riz in rizs:
                f = features_horizonte(serie[riz], h)
                yv = alvo[riz][a]
                if f is not None and yv is not None:
                    f = f + trat_contrastes(trat[riz])
                    Xy.append((f, yv))
            if len(Xy) < 8:
                continue
            for nome, mdl in modelos().items():
                yt, yp = loro(Xy, mdl)
                mae, rmse, r2, mape = metricas(yt, yp)
                perf_rows.append({"alvo": a, "horizonte_h": h, "modelo": nome,
                                  "n": len(yt), "MAE": round(mae, 3), "RMSE": round(rmse, 3),
                                  "R2": round(r2, 3), "MAPE": round(mape, 1)})
                # horizonte: usa MAE como perda; RR_h vs h=1
                key = (a, nome)
                if h == 1:
                    E1[key] = mae
                RR = 100 * (E1.get(key, mae) - mae) / (E1.get(key, mae) + EPS)
                hor_rows.append({"alvo": a, "modelo": nome, "horizonte_h": h,
                                 "E_h_MAE": round(mae, 3), "RR_h_pct": round(RR, 1)})
                # guarda predições do horizonte final (h=7) do melhor por R2 depois
                if h == max(Hs):
                    for riz, t, p in zip(rizs, yt, yp):
                        pred_rows.append({"alvo": a, "modelo": nome, "rizotron": riz,
                                          "y_true": round(t, 3), "y_pred": round(p, 3)})

    with open(C.METRICAS / "model_performance.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(perf_rows[0].keys())); w.writeheader(); w.writerows(perf_rows)
    with open(C.METRICAS / "model_horizon.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(hor_rows[0].keys())); w.writeheader(); w.writerows(hor_rows)
    with open(C.METRICAS / "model_predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pred_rows[0].keys())); w.writeheader(); w.writerows(pred_rows)

    # resumo: melhor modelo (maior R2) por alvo no horizonte final
    print("[Fase 13] LORO (n=12). Melhor modelo por alvo (horizonte final h=6, por R2):")
    for a in ALVOS:
        cand = [r for r in perf_rows if r["alvo"] == a and r["horizonte_h"] == max(Hs)
                and r["modelo"] != "baseline_media"]
        base = [r for r in perf_rows if r["alvo"] == a and r["horizonte_h"] == max(Hs)
                and r["modelo"] == "baseline_media"][0]
        best = max(cand, key=lambda r: (r["R2"] if r["R2"] == r["R2"] else -9))
        print(f"   {a:8s}: {best['modelo']:13s} R2={best['R2']:+.3f} MAE={best['MAE']} "
              f"MAPE={best['MAPE']}%  (baseline MAE={base['MAE']})")
    print("   Saídas: model_performance.csv, model_horizon.csv, model_predictions.csv")


if __name__ == "__main__":
    main()
