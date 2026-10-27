#!/usr/bin/env python3
"""
Title:
    Assessment consolidation, method selection and agreement
File type:
    Script
Purpose:
    Reads all assessor sheets (xlsx or csv), derives the 0-4 quality score and acceptance, joins the
    answer key and produces method rankings, per-image winners, per-assessor means and inter-
    assessor agreement.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-08
Date:
    2026-07-08
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
    - metricas/notas_recebidas/*.xlsx
    - metricas/review_key.csv
Outputs:
    - metricas/08D_concordancia.csv
    - metricas/08D_metodos_agregado.csv
    - metricas/08D_por_avaliador.csv
    - metricas/08D_selecao_por_imagem.csv
Dependencies:
    - openpyxl
    - local: config
Execution:
    python scripts/08D_selecao.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 08D — Consolidação das notas dos especialistas, SELEÇÃO do método e CONCORDÂNCIA.

Lê as planilhas preenchidas (formato "marque x", .xlsx ou .csv) de vários avaliadores,
deriva Q_global (0–4) da caixa marcada, cruza com o gabarito (código→método real) e
produz ranking por método, vencedor por imagem e concordância entre avaliadores.

Métodos (rótulos do artigo):  M1 = Frangi (clássico)  ·  M2 = PRMI (modelo externo)  ·
                              M3 = M1 + M2 (combinado, união).

Nome do avaliador = NOME DO ARQUIVO (ex.: "Avaliador 3.csv" -> A3).

Entradas:
  metricas/notas_recebidas/*.xlsx|*.csv   (uma planilha por avaliador)
  metricas/review_key.csv                 (gabarito: image_id, codigo, metodo_real)
Saídas:
  metricas/08D_metodos_agregado.csv       (por método, todos os avaliadores)
  metricas/08D_selecao_por_imagem.csv     (vencedor por imagem)
  metricas/08D_por_avaliador.csv          (Q médio de cada método por avaliador)
  metricas/08D_concordancia.csv           (Fleiss' kappa e % de concordância)
"""
import os
import io
import re
import sys
import csv
import glob
import statistics as st
from collections import defaultdict

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

NOTAS_DIR = C.METRICAS / "notas_recebidas"
KEY = C.METRICAS / "review_key.csv"

NOTA_COLS = ["nota_0_rejeita", "nota_1_ruim", "nota_2_regular", "nota_3_boa", "nota_4_muito_boa"]
PROB_COLS = ["prob_falta_raiz", "prob_excesso_solo", "prob_glare", "prob_fragmentado"]
XLSX_ORDER = ["image_id", "data", "codigo"] + NOTA_COLS + ["aceita"] + PROB_COLS + ["observacoes"]

LABELS = {"Frangi": "M1", "Ext": "M2", "Comb": "M3"}
DESC = {"M1": "M1 = Frangi (clássico)", "M2": "M2 = PRMI (modelo externo)",
        "M3": "M3 = M1+M2 (combinado)"}
ORDEM = ["M1", "M2", "M3"]


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
    """Aceita? — vale 'x', 'sim', '1', 'yes' (tolera export pt-BR)."""
    return str(v).strip().lower() in ("x", "sim", "1", "yes", "true", "s")


def q_global(row):
    """
    Purpose:
        Return the 0-4 quality score of a judgement row from the marked score column.
    Parameters:
        row: judgement row (dict)
    Returns:
        int or None when no score is marked
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    for i, c in enumerate(NOTA_COLS):
        if marcado(row.get(c)):
            return i
    return None


def nome_avaliador(path):
    """
    Purpose:
        Derive the assessor label (A<n>) from the number in a sheet file name.
    Parameters:
        path: assessor sheet path
    Returns:
        str
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    base = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r"(\d+)", base)
    return f"A{m.group(1)}" if m else base


def ler_csv(f):
    """Robusto: detecta separador (',' ou ';'); aceita tanto o nosso cabeçalho interno
    (com image_id/prancha/avaliador) quanto o cabeçalho 'amigável' exportado do Excel
    (Imagem;Data;Método;0 rejeita;...) — neste caso mapeia por POSIÇÃO a XLSX_ORDER."""
    raw = open(f, encoding="utf-8-sig").read()
    linha0 = raw.splitlines()[0] if raw.splitlines() else ""
    delim = ";" if linha0.count(";") > linha0.count(",") else ","
    linhas = [r for r in csv.reader(io.StringIO(raw), delimiter=delim) if any(c.strip() for c in r)]
    if not linhas:
        return []
    header = [h.strip().lower() for h in linhas[0]]
    if "image_id" in header:                         # nosso formato interno
        keys = linhas[0]
        return [dict(zip(keys, row)) for row in linhas[1:]]
    # formato "amigável" (rótulos) -> posição
    out = []
    for row in linhas[1:]:
        out.append({XLSX_ORDER[i]: (row[i] if i < len(row) else "") for i in range(min(len(XLSX_ORDER), len(row)))})
    return out


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
    rows = []
    for r in ws.iter_rows(min_row=4, values_only=True):
        if not r or not r[0]:
            continue
        rows.append({XLSX_ORDER[i]: (r[i] if i < len(r) else "") for i in range(len(XLSX_ORDER))})
    return rows


def carregar():
    """
    Purpose:
        Load all assessor sheets with their quality scores.
    Parameters:
        none
    Returns:
        list of judgement rows
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    files = sorted(glob.glob(str(NOTAS_DIR / "*.xlsx")) + glob.glob(str(NOTAS_DIR / "*.csv")))
    rows = []
    for f in files:
        aval = nome_avaliador(f)
        got = ler_xlsx(f) if f.lower().endswith(".xlsx") else ler_csv(f)
        n = 0
        for r in got:
            r["avaliador"] = aval
            r["_Q"] = q_global(r)
            if r["_Q"] is not None:
                rows.append(r); n += 1
        print(f"   {aval:4s} <- {os.path.basename(f)}  ({n} notas)")
    return rows


def fleiss_kappa(item_counts, k):
    """item_counts: lista de listas [n_cat0, n_cat1, ...] por item; k = nº categorias."""
    items = [c for c in item_counts if sum(c) >= 2]
    if not items:
        return None
    N = len(items)
    total = sum(sum(c) for c in items)
    p_j = [sum(c[j] for c in items) / total for j in range(k)]
    Pe = sum(p * p for p in p_j)
    Pbar = 0.0
    for c in items:
        n = sum(c)
        Pbar += (sum(x * x for x in c) - n) / (n * (n - 1))
    Pbar /= N
    if Pe >= 1:
        return 1.0
    return (Pbar - Pe) / (1 - Pe)


def pct_concordancia(item_ratings):
    """% médio de pares de avaliadores que concordam, por item."""
    accs = []
    for vals in item_ratings:
        if len(vals) < 2:
            continue
        pares = concord = 0
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                pares += 1
                concord += (vals[i] == vals[j])
        accs.append(concord / pares)
    return st.mean(accs) if accs else None


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
    if not KEY.exists():
        print("[08D] Falta o gabarito review_key.csv (rode a Fase 08)."); return
    key = {(r["image_id"], r["codigo"]): r["metodo_real"]
           for r in csv.DictReader(open(KEY, encoding="utf-8"))}

    print("[08D] Carregando planilhas:")
    validas = carregar()
    if not validas:
        print("[08D] Nenhuma nota. Ponha as planilhas em "
              f"{NOTAS_DIR.relative_to(C.ROOT)}/ e rode de novo."); return
    for r in validas:
        r["M"] = LABELS.get(key.get((r["image_id"], r.get("codigo")), "?"), "?")

    avaliadores = sorted(set(r["avaliador"] for r in validas))

    # ---------- agregado por método (pool de todos) ----------
    por_m = defaultdict(list)
    for r in validas:
        por_m[r["M"]].append(r)
    agg = []
    for m in ORDEM:
        rs = por_m.get(m, [])
        if not rs:
            continue
        qs = [r["_Q"] for r in rs]
        acc = [1 if aceito(r.get("aceita")) else 0 for r in rs]
        linha = {"metodo": m, "descricao": DESC[m], "n": len(rs),
                 "Q_media": round(st.mean(qs), 3), "Q_dp": round(st.pstdev(qs), 3),
                 "taxa_aceitacao": round(st.mean(acc), 3)}
        for c in PROB_COLS:
            linha[c] = round(st.mean([1 if marcado(r.get(c)) else 0 for r in rs]), 3)
        agg.append(linha)
    agg.sort(key=lambda x: x["Q_media"], reverse=True)
    if not agg:
        print("[08D] Nenhuma nota casou com o gabarito (códigos image_id×codigo não batem "
              "com review_key.csv). Verifique se as planilhas são as do pacote gerado.")
        return
    with open(C.METRICAS / "08D_metodos_agregado.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(agg[0].keys())); w.writeheader(); w.writerows(agg)

    # ---------- Q por método por avaliador (viés) ----------
    pa_rows = []
    for aval in avaliadores:
        linha = {"avaliador": aval}
        for m in ORDEM:
            qs = [r["_Q"] for r in validas if r["avaliador"] == aval and r["M"] == m]
            linha[m] = round(st.mean(qs), 2) if qs else ""
        pa_rows.append(linha)
    with open(C.METRICAS / "08D_por_avaliador.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pa_rows[0].keys())); w.writeheader(); w.writerows(pa_rows)

    # ---------- vencedor por imagem (média de Q entre avaliadores) ----------
    por_img = defaultdict(lambda: defaultdict(list))
    for r in validas:
        por_img[(r["image_id"], r.get("data", ""))][r["M"]].append(r["_Q"])
    sel_rows, vit = [], defaultdict(int)
    for (iid, data), mets in sorted(por_img.items()):
        medias = {m: st.mean(v) for m, v in mets.items() if v and m in ORDEM}
        if not medias:                     # nenhuma nota casou p/ esta imagem
            continue
        venc = max(medias, key=medias.get)
        vit[venc] += 1
        linha = {"image_id": iid, "data": data, "vencedor": venc, "Q_vencedor": round(medias[venc], 2)}
        for m in ORDEM:
            linha[m] = round(medias[m], 2) if m in medias else ""
        sel_rows.append(linha)
    with open(C.METRICAS / "08D_selecao_por_imagem.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sel_rows[0].keys())); w.writeheader(); w.writerows(sel_rows)

    # ---------- concordância entre avaliadores ----------
    # item = (image_id, codigo)  ->  {avaliador: Q, avaliador: aceita}
    itemsQ = defaultdict(dict); itemsA = defaultdict(dict)
    for r in validas:
        it = (r["image_id"], r.get("codigo"))
        itemsQ[it][r["avaliador"]] = r["_Q"]
        itemsA[it][r["avaliador"]] = 1 if aceito(r.get("aceita")) else 0
    # Fleiss em Q (5 cat), aceita (2 cat) e Q "boa" (>=3) vs "não" (2 cat)
    countsQ = [[sum(1 for v in d.values() if v == j) for j in range(5)] for d in itemsQ.values()]
    countsA = [[sum(1 for v in d.values() if v == j) for j in range(2)] for d in itemsA.values()]
    countsB = [[sum(1 for v in d.values() if (v >= 3) == b) for b in (False, True)] for d in itemsQ.values()]
    conc = [
        {"metrica": "Fleiss_kappa_Q_0a4", "valor": round(fleiss_kappa(countsQ, 5), 3)},
        {"metrica": "Fleiss_kappa_Q_boa(>=3)", "valor": round(fleiss_kappa(countsB, 2), 3)},
        {"metrica": "Fleiss_kappa_aceita", "valor": round(fleiss_kappa(countsA, 2), 3)},
        {"metrica": "pct_concordancia_Q", "valor": round(pct_concordancia([list(d.values()) for d in itemsQ.values()]), 3)},
        {"metrica": "pct_concordancia_aceita", "valor": round(pct_concordancia([list(d.values()) for d in itemsA.values()]), 3)},
        {"metrica": "n_avaliadores", "valor": len(avaliadores)},
        {"metrica": "n_itens", "valor": len(itemsQ)},
    ]
    with open(C.METRICAS / "08D_concordancia.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["metrica", "valor"]); w.writeheader(); w.writerows(conc)

    # ---------- resumo ----------
    print(f"\n[08D] {len(validas)} avaliações | avaliadores: {avaliadores}")
    print("\n  Ranking por método (Q_global médio 0–4, pool dos avaliadores):")
    for a in agg:
        print(f"    {a['descricao']:26s} Q={a['Q_media']:.2f}±{a['Q_dp']:.2f}  aceita={a['taxa_aceitacao']:.0%}  (n={a['n']})")
    print("\n  Vitórias por imagem:")
    for m in ORDEM:
        if vit.get(m):
            print(f"    {m}  {vit[m]}/{len(sel_rows)}")
    print("\n  Concordância entre avaliadores:")
    for c in conc[:5]:
        print(f"    {c['metrica']:26s} {c['valor']}")
    print(f"\n  → Melhor método (Q agregado): **{agg[0]['metodo']} = {agg[0]['descricao']}**")
    print("  Saídas: 08D_metodos_agregado.csv, 08D_selecao_por_imagem.csv, "
          "08D_por_avaliador.csv, 08D_concordancia.csv")


if __name__ == "__main__":
    main()
