#!/usr/bin/env python3
"""
Title:
    Chronology and days after planting
File type:
    Script
Purpose:
    Validates the experimental chronology using the sowing date as time zero; computes DAP, the
    interval between consecutive collections and its deviation from 7 days, and checks fertilisation
    timing.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-06
Date:
    2026-07-06
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
    - config/cronograma_experimento.csv
Outputs:
    - config/cronologia_dap.csv
Dependencies:
    - local: config
Execution:
    python scripts/02_cronologia_dap.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Not re-executed in the v1.0.0 verification. Environment of the verification: Python 3.9.6
    (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Fase 02 — Validação cronológica e reconstrução dos dias após plantio (DAP).

Adota a data de plantio como origem temporal. Para cada coleta calcula DAP,
o intervalo Δt entre coletas consecutivas e o desvio ε em relação ao esperado
(7 dias). Valida a cronologia da adubação (δ = DAP_real − DAP_previsto).

Entrada:  config/cronograma_experimento.csv (datas confirmadas)
Saída:    config/cronologia_dap.csv (eventos + DAP)  e  relatório no console.
"""
import os
import sys
import csv
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

def d(s):  # 'YYYY-MM-DD' -> date
    """
    Purpose:
        Parse an ISO date string.
    Parameters:
        s: ISO date (YYYY-MM-DD)
    Returns:
        datetime.date
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return datetime.date.fromisoformat(s)

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
    C.CONFIG.mkdir(parents=True, exist_ok=True)
    src = C.CONFIG / "cronograma_experimento.csv"
    eventos = []
    with open(src, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            eventos.append(row)

    saida = []
    # 1) Eventos pontuais (plantio, adubação, germinação) com DAP
    for r in eventos:
        if r["evento"] in {"plantio", "adubacao", "germinacao"} and r["data"]:
            try:
                data = d(r["data"])
            except ValueError:
                continue
            dap_ev = C.dap(data)
            # mapear tratamento textual -> codigo
            tcod = ""
            tt = r["tratamento"]
            if "1" in tt: tcod = "T1"
            elif "2" in tt: tcod = "T2"
            elif "3" in tt: tcod = "T3"
            elif "Refer" in tt or "Testemunha" in tt: tcod = "REF"
            prev = C.ADUBACAO_PREVISTA.get(tcod, None)
            delta = (dap_ev - prev) if (r["evento"] == "adubacao" and prev is not None) else ""
            saida.append({
                "evento": r["evento"], "data": r["data"], "DAP": dap_ev,
                "tratamento": tcod, "delta_t": "", "epsilon": "",
                "dap_previsto": prev if prev is not None else "",
                "desvio_delta": delta,
            })

    # 2) Coletas com DAP, Δt e ε
    dap_ant = None
    for k, pasta in enumerate(C.COLETAS, start=1):
        data = C.parse_data_pasta(pasta)
        dap_k = C.dap(data)
        dt = "" if dap_ant is None else dap_k - dap_ant
        eps = "" if dt == "" else dt - C.DELTA_T_REF
        saida.append({
            "evento": f"coleta_{k}", "data": data.isoformat(), "DAP": dap_k,
            "tratamento": "", "delta_t": dt, "epsilon": eps,
            "dap_previsto": "", "desvio_delta": "",
        })
        dap_ant = dap_k

    out = C.CONFIG / "cronologia_dap.csv"
    campos = ["evento", "data", "DAP", "tratamento", "delta_t", "epsilon",
              "dap_previsto", "desvio_delta"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(saida)

    # Relatório
    print(f"[Fase 02] Cronologia + DAP  ->  {out.relative_to(C.ROOT)}")
    print(f"   Plantio (DAP=0): {C.DATA_PLANTIO.isoformat()}")
    print("   Adubação:")
    for r in saida:
        if r["evento"] == "adubacao":
            print(f"     {r['tratamento']}: {r['data']} (DAP {r['DAP']}, "
                  f"previsto {r['dap_previsto']}, desvio {r['desvio_delta']} d)")
    print("   Coletas (DAP / Δt / ε vs 7d):")
    for r in saida:
        if r["evento"].startswith("coleta"):
            print(f"     {r['evento']}: {r['data']}  DAP={r['DAP']}  "
                  f"Δt={r['delta_t']}  ε={r['epsilon']}")

if __name__ == "__main__":
    main()
