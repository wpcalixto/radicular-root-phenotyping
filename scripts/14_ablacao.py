#!/usr/bin/env python3
"""
Title:
    Ablation studies
File type:
    Script
Purpose:
    Quantifies the contribution of modalities, morphological groups and collections by controlled
    removal and comparison of leave-one-rhizotron-out MAE against the full Ridge model.
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
    - metricas/ablation_collection.csv
    - metricas/ablation_fusion.csv
    - metricas/ablation_group.csv
    - metricas/ablation_modality.csv
Dependencies:
    - numpy
    - sklearn
    - local: config
Execution:
    python scripts/14_ablacao.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 14 — Estudos de ablação.

Quantifica a contribuição de modalidades, grupos morfológicos e coletas na predição dos
desfechos finais, por remoção controlada de componentes e comparação do erro (MAE via
Leave-One-Rhizotron-Out, modelo Ridge) contra o modelo completo.

Grupos de features (agregados sobre todas as coletas = horizonte completo):
  IMAGEM  → área {A_px, ocupação} · topo {L_skel_px, N_br}
  ELÉTRICA→ {R, ρ, σ}
  TEMPO   → inclinações (β) de L_skel, ocupação, σ
  MANEJO  → tratamento (ordinal)
(Dmax_norm/Wmax_norm e F_hull foram excluídos: saturam em ≈1 ou reproduzem a ocupação — ver Fase 09/Bloco D.)

Δg = E_{-g} − E_full  (positivo ⇒ grupo relevante);  RC_g = Δg/E_full × 100.
Ganho da fusão: G_fusion = E_img − E_img+elec.

Entrada: metricas/multimodal_long.csv
Saídas:
  metricas/ablation_modality.csv     (cenários por modalidade: MAE, R2)
  metricas/ablation_group.csv        (remoção de grupo: Δ, RC)
  metricas/ablation_collection.csv   (remoção de cada coleta: Δ)
  metricas/ablation_fusion.csv       (ganho óptico-elétrico)
"""
import os
import sys
import csv
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

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

# Grupos por FONTE (mutuamente exclusivos, exaustivos) — cada feature tem uma única fonte.
OPT = ["O_ocupacao_m", "L_skel_px_m", "N_br_m", "O_ocupacao_s", "L_skel_px_s"]
ELEC = ["sigma_a_m", "sigma_a_s"]
MAN = ["trat_T1", "trat_T2", "trat_T3"]
FULL = OPT + ELEC + MAN
# Eixo ortogonal — TIPO de informação: nível (médias _m) vs dinâmica (inclinações _s).
LEVEL = [k for k in FULL if k.endswith("_m")]
DYN = [k for k in FULL if k.endswith("_s")]
# ablação por fonte e por tipo (grupos removidos do modelo completo)
G = {"optical": OPT, "electrical": ELEC, "management": MAN, "dynamics": DYN, "level": LEVEL}


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


def construir(serie, excluir_coleta=None):
    """Feature dict de um rizotron; opcionalmente exclui uma coleta (para ablação temporal)."""
    pts = [(int(ck), dap, s) for (ck, dap, s) in serie if ck != "" and int(ck) <= 6]
    if excluir_coleta is not None:
        pts = [p for p in pts if p[0] != excluir_coleta]
    feat = {}
    for v in MEANS:
        xs = [s[v] for _, _, s in pts if s[v] is not None]
        feat[f"{v}_m"] = float(np.mean(xs)) if xs else 0.0
    for v in SLOPES:
        xy = [(dap, s[v]) for _, dap, s in pts if s[v] is not None]
        feat[f"{v}_s"] = float(np.polyfit([a for a, _ in xy], [b for _, b in xy], 1)[0]) if len(xy) >= 2 else 0.0
    return feat


def loro_mae(feats, y, keys):
    """MAE e R2 por LORO (Ridge) usando só as colunas 'keys'."""
    X = np.array([[f[k] for k in keys] for f in feats], float)
    y = np.array(y, float)
    yp = np.empty(len(y))
    for i in range(len(y)):
        tr = [j for j in range(len(y)) if j != i]
        sc = StandardScaler().fit(X[tr])
        m = Ridge(alpha=10.0).fit(sc.transform(X[tr]), y[tr])
        yp[i] = m.predict(sc.transform(X[i:i + 1]))[0]
    err = y - yp
    mae = float(np.mean(np.abs(err)))
    ss = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - float(np.sum(err ** 2)) / ss if ss > 0 else float("nan")
    return mae, r2


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
        f = construir(serie[riz]); f.update(trat_contrastes(trat[riz]))
        feats.append(f)

    mod_rows, grp_rows, col_rows, fus_rows = [], [], [], []
    for a in ALVOS:
        y = [alvo[riz][a] for riz in rizs]
        E_full, R_full = loro_mae(feats, y, FULL)
        # --- cenários por FONTE (tabela de ablação com MAE absoluto) ---
        cenarios = {"optical": OPT, "electrical": ELEC, "optical+electrical": OPT + ELEC, "full": FULL}
        E = {}
        for nome, keys in cenarios.items():
            mae, r2 = loro_mae(feats, y, keys)
            E[nome] = mae
            mod_rows.append({"alvo": a, "cenario": nome, "n_features": len(keys),
                             "MAE": round(mae, 3), "R2": round(r2, 3)})
        # --- ablação por grupo (full − grupo): fonte (optical/electrical/management) e tipo (level/dynamics) ---
        for gname, gkeys in G.items():
            rem = [k for k in FULL if k not in gkeys]
            mae, _ = loro_mae(feats, y, rem) if rem else (float("nan"), float("nan"))
            d = mae - E_full
            grp_rows.append({"alvo": a, "grupo_removido": gname,
                             "E_sem_grupo": round(mae, 3), "E_full": round(E_full, 3),
                             "delta": round(d, 3), "RC_pct": round(100 * d / E_full, 1)})
        # --- fusão óptico-elétrica ---
        Gf = E["optical"] - E["optical+electrical"]
        fus_rows.append({"alvo": a, "E_img": round(E["optical"], 3), "E_img_elec": round(E["optical+electrical"], 3),
                         "G_fusion": round(Gf, 3), "RG_fusion_pct": round(100 * Gf / E["optical"], 1)})
        # --- ablação por coleta ---
        coletas = sorted({int(ck) for ck, _, _ in sum(serie.values(), []) if ck != "" and int(ck) <= 6})
        for ck in coletas:
            feats_k = []
            for riz in rizs:
                f = construir(serie[riz], excluir_coleta=ck); f.update(trat_contrastes(trat[riz]))
                feats_k.append(f)
            mae, _ = loro_mae(feats_k, y, FULL)
            col_rows.append({"alvo": a, "coleta_removida": ck,
                             "E_sem_coleta": round(mae, 3), "delta": round(mae - E_full, 3)})

    for nome, dados in [("ablation_modality", mod_rows), ("ablation_group", grp_rows),
                        ("ablation_collection", col_rows), ("ablation_fusion", fus_rows)]:
        with open(C.METRICAS / f"{nome}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(dados[0].keys())); w.writeheader(); w.writerows(dados)

    print("[Fase 14] ablação (LORO Ridge, MAE). Cenários por modalidade:")
    for a in ALVOS:
        print(f"  {a}:")
        for r in [x for x in mod_rows if x["alvo"] == a]:
            print(f"     {r['cenario']:10s} MAE={r['MAE']:.3f} R2={r['R2']:+.3f}")
        fu = [x for x in fus_rows if x["alvo"] == a][0]
        print(f"     -> fusão óptico-elétrica: G={fu['G_fusion']:.3f} ({fu['RG_fusion_pct']:+.1f}%)")
    print("   Grupos mais relevantes (maior Δ = pior sem ele):")
    for a in ALVOS:
        top = sorted([x for x in grp_rows if x["alvo"] == a], key=lambda r: -r["delta"])[:3]
        print(f"     {a}: " + ", ".join(f"{r['grupo_removido']}(Δ{r['delta']:+.2f})" for r in top))
    print("   Saídas: ablation_modality/group/collection/fusion.csv")


if __name__ == "__main__":
    main()
