#!/usr/bin/env python3
"""
Title:
    Electrical variables
File type:
    Script
Purpose:
    Maps the Wenner spreadsheets to rhizotrons, recomputes apparent resistivity with the electrode
    spacing a = 0.16 m and derives apparent conductivity and standardised values per collection.
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
    - none detected by static analysis
Outputs:
    - metricas/electrical_by_treatment_dap.csv
    - metricas/electrical_features_by_rhizotron.csv
Dependencies:
    - openpyxl
    - local: config
Execution:
    python scripts/10_eletricas.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 10 — Processamento das planilhas elétricas.

As planilhas (`tabdatas/`) têm 4 colunas = tratamentos (TR, T1, T2, T3) × 3 linhas =
réplicas → mapeadas para os 12 rizotrons: TR→R01-03, T1→R04-06, T2→R07-09, T3→R10-12
(réplica 1,2,3 = R{t*3+r}). Há 6 datas elétricas (23/05 a 28/06; a coleta 7, 05/07, não
tem medição elétrica).

Fórmulas (metodologia): R (dado); ρ_a = 2πa·R (Wenner); σ_a = 1/ρ_a; z* = (z-μ)/σ, com
|z*| > 3 sinalizado. A resistividade e a condutividade das planilhas são internamente
consistentes com R (ρ/R ≈ 2πa constante; σ ≈ 1/ρ) — usamos R e ρ das planilhas e
σ_a = 1/ρ_a (a Condutividade é lida só para conferência de qualidade).

Saídas:
  metricas/electrical_features_by_rhizotron.csv  (rhizotron_id, collection_date, DAP,
      R, rho_a, sigma_a, a_implied_m, source_file, quality_flag)
  metricas/electrical_by_treatment_dap.csv       (médias por tratamento × DAP)
"""
import os
import sys
import csv
import glob
import math
import statistics as st
from collections import defaultdict

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

TAB = C.ROOT.parent  # .../Progama_Radicular  → mas as planilhas estão em Nova_versao/tabdatas
TABDATAS = C.TABDATAS
COLS_TRAT = ["TR", "T1", "T2", "T3"]      # ordem das colunas nas planilhas
DATAS_ELE = C.COLETAS[:6]                 # 6 datas com elétrica (sem 05/07)
SUPER = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6",
         "⁷": "7", "⁸": "8", "⁹": "9", "¯": "-", "⁻": "-"}


def parse_cond(s):
    """'1,13·10¯³' -> 1.13e-3 (conferência). Retorna None se não parsear."""
    try:
        s = str(s).replace(" ", "")
        if "·10" not in s:
            return float(s.replace(",", "."))
        mant, exp = s.split("·10")
        mant = float(mant.replace(",", "."))
        exp = "".join(SUPER.get(ch, ch) for ch in exp)
        return mant * (10 ** int(exp))
    except Exception:
        return None


def achar(prefixos, data):
    """Acha o arquivo cujo nome começa com um dos prefixos e contém a data (dd_mm_[yy]yy)."""
    d, m, y = data.split("_")
    for pre in prefixos:
        for cand in [f"{pre}{d}_{m}_{y}", f"{pre}{d}_{m}_{y[2:]}"]:
            fs = glob.glob(str(TABDATAS / f"{cand}*.xlsx"))
            if fs:
                return fs[0]
    return None


def ler_matriz(path):
    """Lê a matriz 3×4 (réplicas × tratamentos) de valores numéricos (linhas 2-4)."""
    ws = openpyxl.load_workbook(path, data_only=True).active
    hdr = [str(ws.cell(1, c).value).strip().upper() if ws.cell(1, c).value else "" for c in range(1, 5)]
    col = {t: hdr.index(t) + 1 for t in COLS_TRAT if t in hdr}
    M = {}
    for rep in (1, 2, 3):
        for t in COLS_TRAT:
            if t in col:
                M[(rep, t)] = ws.cell(1 + rep, col[t]).value
    return M


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
    C.METRICAS.mkdir(parents=True, exist_ok=True)
    rows = []
    for data in DATAS_ELE:
        fR = achar(["Resistencia_"], data)
        fRho = achar(["Resistividade_"], data)
        fSig = achar(["Condutividade_Eletrica_", "Condutividade_"], data)
        if not (fR and fRho):
            print(f"  [pula] {data}: falta Resistencia/Resistividade"); continue
        MR, MRho = ler_matriz(fR), ler_matriz(fRho)
        MSig = ler_matriz(fSig) if fSig else {}
        dt = C.parse_data_pasta(data)
        for ti, t in enumerate(COLS_TRAT):
            for rep in (1, 2, 3):
                R = MR.get((rep, t)); rho = MRho.get((rep, t))
                if R in (None, "") or rho in (None, ""):
                    continue
                R = float(R); rho_planilha = float(rho)
                # rho_a e sigma_a são RECALCULADOS a partir da resistência medida com o
                # espaçamento físico do arranjo (C.WENNER_A). O valor da planilha é
                # mantido apenas para auditoria: foi obtido com a = 0,2667 m, que supõe
                # as hastes de borda a borda e ignora as margens de 14,5 cm.
                rho = 2.0 * math.pi * C.WENNER_A * R
                sigma = 1.0 / rho if rho else None
                a_impl = (rho_planilha / R) / (2 * math.pi) if R else None
                riz = f"R{ti * 3 + rep:02d}"
                # conferência com a Condutividade da planilha
                sig_plan = parse_cond(MSig.get((rep, t))) if MSig else None
                cq = "ok"
                # a planilha de condutividade usa o 'a' incorreto: divergência de escala
                # esperada (fator C.WENNER_A_PLANILHA / C.WENNER_A); sinaliza-se apenas
                # desvio ADICIONAL a essa escala.
                if sig_plan and sigma:
                    esperado = sigma * C.WENNER_A / C.WENNER_A_PLANILHA
                    if abs(sig_plan - esperado) / esperado > 0.10:
                        cq = "cond_divergente"
                rows.append({
                    "rhizotron_id": riz, "tratamento": C.tratamento(riz)[0],
                    "collection_date": data, "DAP": C.dap(dt),
                    "R_ohm": round(R, 4), "rho_a": round(rho, 4),
                    "sigma_a": round(sigma, 8) if sigma else "",
                    "rho_a_planilha": round(rho_planilha, 4),
                    "a_usado_m": C.WENNER_A,
                    "a_implied_planilha_m": round(a_impl, 4) if a_impl else "",
                    "source_file": os.path.basename(fR), "quality_flag": cq,
                })

    if not rows:
        print("[Fase 10] Nenhuma medição lida."); return

    # z-score por variável + flag |z*|>3
    for var in ("R_ohm", "rho_a", "sigma_a"):
        vals = [r[var] for r in rows if isinstance(r[var], (int, float))]
        mu, sd = st.mean(vals), (st.pstdev(vals) or 1e-9)
        for r in rows:
            if isinstance(r[var], (int, float)):
                z = (r[var] - mu) / sd
                r[f"z_{var}"] = round(z, 3)
                if abs(z) > 3 and r["quality_flag"] == "ok":
                    r["quality_flag"] = f"outlier_{var}"

    campos = ["rhizotron_id", "tratamento", "collection_date", "DAP", "R_ohm", "rho_a",
              "sigma_a", "rho_a_planilha", "a_usado_m", "a_implied_planilha_m",
              "z_R_ohm", "z_rho_a", "z_sigma_a",
              "source_file", "quality_flag"]
    with open(C.METRICAS / "electrical_features_by_rhizotron.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos); w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in campos})

    # médias por tratamento × DAP
    agg = defaultdict(list)
    for r in rows:
        agg[(r["tratamento"], r["DAP"], r["collection_date"])].append(r)
    trat_rows = []
    for (t, dap, data), rs in sorted(agg.items(), key=lambda k: (k[0][0], k[0][1])):
        linha = {"tratamento": t, "DAP": dap, "collection_date": data, "n": len(rs)}
        for var in ("R_ohm", "rho_a", "sigma_a"):
            vals = [x[var] for x in rs if isinstance(x[var], (int, float))]
            linha[var + "_media"] = round(st.mean(vals), 6) if vals else ""
            linha[var + "_dp"] = round(st.pstdev(vals), 6) if len(vals) > 1 else 0
        trat_rows.append(linha)
    with open(C.METRICAS / "electrical_by_treatment_dap.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(trat_rows[0].keys())); w.writeheader(); w.writerows(trat_rows)

    flags = [r["quality_flag"] for r in rows if r["quality_flag"] != "ok"]
    print(f"[Fase 10] {len(rows)} medições (6 datas × 12 rizotrons) -> electrical_features_by_rhizotron.csv")
    print(f"   a (Wenner) adotado: {C.WENNER_A:.4f} m | implícito nas planilhas: "
          f"{st.mean([r['a_implied_planilha_m'] for r in rows if isinstance(r['a_implied_planilha_m'], (int, float))]):.4f} m")
    print(f"   flags de qualidade: {len(flags)} ({set(flags) or 'nenhum'})")
    print(f"   médias por tratamento×DAP: metricas/electrical_by_treatment_dap.csv")


if __name__ == "__main__":
    main()
