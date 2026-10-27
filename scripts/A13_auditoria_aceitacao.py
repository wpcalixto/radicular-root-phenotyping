#!/usr/bin/env python3
"""
Title:
    Acceptance audit and assessor panel
File type:
    Script
Purpose:
    Detects content-identical assessor files and compares acceptance under the marked() and
    accepted() reading rules for the assessor panels.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-30
Date:
    2026-07-30
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
    - metricas/A13_auditoria_aceitacao.csv
Dependencies:
    - local: config
Execution:
    python scripts/A13_auditoria_aceitacao.py (from a workspace prepared with
    tools/prepare_workspace.py)
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
A13 — Auditoria da coluna de aceitação e do painel de avaliadores.

Motivação (auditoria 2026-07-30): o diretório de avaliações contém dez arquivos, mas
apenas SEIS conjuntos distintos de julgamentos. `Avaliador 7.xlsx` e `avaliador1.xlsx`
reproduzem A1; `Avaliador 8.xlsx` e `Avaliador 9.xlsx` reproduzem A6. As análises
publicadas trataram nove arquivos como nove avaliadores independentes.

Este script:
  1. verifica a duplicidade por assinatura de conteúdo (MD5) e julgamento a julgamento;
  2. inventaria os valores brutos da coluna `aceita` e a regra de conversão;
  3. reporta válidos/ausentes, contagens por avaliador e método e o denominador final;
  4. reproduz a taxa de aceitação sob DUAS definições e DOIS painéis, isolando a causa
     de qualquer divergência com a tabela publicada.

Definições de aceitação comparadas:
  (a) INDIVIDUAL — fração das avaliações individuais com `aceita` verdadeiro
      (denominador = 82 x n_avaliadores); é a definição usada na tabela do manuscrito;
  (b) MAIORIA — fração das 82 imagens em que ao menos metade dos avaliadores aceitou;
      é a definição usada em `08F_estatistica.py`.

Regras de conversão comparadas:
  - `marcado()`  : verdadeiro apenas para "x";
  - `aceito()`   : verdadeiro para "x", "sim", "1", "yes", "true", "s".

Saída: metricas/A13_auditoria_aceitacao.csv  (+ relatório no stdout)
"""
import os
import sys
import csv
import glob
import hashlib
import importlib.util
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

_spec = importlib.util.spec_from_file_location("sel08d", C.SCRIPTS / "08D_selecao.py")
sel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sel)

NOTAS_DIR = C.METRICAS / "notas_recebidas"
KEY = C.METRICAS / "review_key.csv"
OUT = C.METRICAS / "A13_auditoria_aceitacao.csv"
MAPA = {"Frangi": "M1", "Ext": "M2", "Comb": "M3"}
CANONICOS = ["A1", "A2", "A3", "A4", "A5", "A6"]
ORDEM = ["M3", "M1", "M2"]


def md5(p):
    """
    Purpose:
        MD5 checksum of a file.
    Parameters:
        p: file path
    Returns:
        str
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def ler_arquivo(f):
    """
    Purpose:
        Read an assessor sheet with the 08D readers.
    Parameters:
        f: sheet path
    Returns:
        list of dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return sel.ler_xlsx(f) if f.lower().endswith(".xlsx") else sel.ler_csv(f)


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
    gab = {}
    with open(KEY, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            gab[(r["image_id"], r["codigo"])] = MAPA.get(r["metodo_real"], r["metodo_real"])

    arquivos = sorted(glob.glob(str(NOTAS_DIR / "*.xlsx")) + glob.glob(str(NOTAS_DIR / "*.csv")))

    print("=" * 78)
    print("1. INVENTÁRIO E DUPLICIDADE")
    print("=" * 78)
    por_hash = defaultdict(list)
    for f in arquivos:
        por_hash[md5(f)].append(os.path.basename(f))
    print(f"  arquivos encontrados: {len(arquivos)} | assinaturas distintas: {len(por_hash)}")
    for h, nomes in sorted(por_hash.items(), key=lambda kv: kv[1][0]):
        marca = "  <-- REDUNDANTE" if len(nomes) > 1 else ""
        print(f"    {h[:12]}  {', '.join(nomes)}{marca}")

    # --- carga bruta por arquivo ---
    bruto = {}
    for f in arquivos:
        aval = sel.nome_avaliador(f)
        bruto.setdefault(aval, []).append((os.path.basename(f), ler_arquivo(f)))

    # comparação julgamento a julgamento entre avaliadores nomeados
    def chaveada(rows):
        d = {}
        for r in rows:
            q = sel.q_global(r)
            if q is None:
                continue
            img = str(r.get("image_id", "")).strip()
            cod = str(r.get("codigo", "")).strip()
            met = gab.get((img, cod))
            if met is None:
                continue
            d[(img, met)] = (q, str(r.get("aceita")).strip())
        return d

    dados = {a: chaveada(v[0][1]) for a, v in bruto.items()}
    avals = sorted(dados)
    print("\n  pares de avaliadores com julgamentos integralmente idênticos:")
    achou = False
    for i in range(len(avals)):
        for j in range(i + 1, len(avals)):
            a, b = avals[i], avals[j]
            com = set(dados[a]) & set(dados[b])
            if com and all(dados[a][k] == dados[b][k] for k in com):
                print(f"    {a} == {b}   ({len(com)} julgamentos)")
                achou = True
    if not achou:
        print("    (nenhum)")

    print("\n" + "=" * 78)
    print("2. VALORES BRUTOS DA COLUNA `aceita`")
    print("=" * 78)
    valores = Counter()
    for a in avals:
        for f, rows in bruto[a]:
            for r in rows:
                if sel.q_global(r) is None:
                    continue
                valores[repr(r.get("aceita"))] += 1
    for v, n in valores.most_common():
        conv_m = sel.marcado(eval(v) if v != "None" else None)
        conv_a = sel.aceito(eval(v) if v != "None" else None)
        print(f"    {v:<22s} n={n:<6d}  marcado()={conv_m!s:<5s} aceito()={conv_a}")
    print("\n  Regra `marcado()`: verdadeiro somente para \"x\".")
    print("  Regra `aceito()` : verdadeiro para \"x\", \"sim\", \"1\", \"yes\", \"true\", \"s\".")

    print("\n" + "=" * 78)
    print("3. COMPLETUDE POR AVALIADOR E MÉTODO")
    print("=" * 78)
    print(f"    {'aval':<6s} " + " ".join(f"{m:>6s}" for m in ORDEM) + "   total")
    for a in avals:
        c = Counter(m for (_, m) in dados[a])
        print(f"    {a:<6s} " + " ".join(f"{c[m]:>6d}" for m in ORDEM) + f"   {sum(c.values()):>5d}")

    print("\n" + "=" * 78)
    print("4. TAXA DE ACEITAÇÃO — 2 PAINÉIS x 2 REGRAS x 2 DEFINIÇÕES")
    print("=" * 78)
    linhas = []
    for rot_painel, painel in [("A1-A9 (como publicado)", avals),
                               ("6 canônicos", CANONICOS)]:
        for rot_regra, regra in [("marcado()", sel.marcado), ("aceito()", sel.aceito)]:
            ind = defaultdict(lambda: [0, 0])
            porimg = defaultdict(lambda: defaultdict(list))
            for a in painel:
                for (img, met), (_q, ac) in dados[a].items():
                    ok = 1 if regra(ac) else 0
                    ind[met][0] += ok
                    ind[met][1] += 1
                    porimg[img][met].append(ok)
            maioria = {m: 0 for m in ORDEM}
            n_img = len(porimg)
            for img, d in porimg.items():
                for m in ORDEM:
                    if d[m] and sum(d[m]) >= len(d[m]) / 2.0:
                        maioria[m] += 1
            print(f"\n  painel={rot_painel:<24s} regra={rot_regra}")
            for m in ORDEM:
                n, N = ind[m]
                print(f"    {m}: individual {n:>4d}/{N:<4d} = {100*n/N:>4.0f}%   "
                      f"| maioria {maioria[m]:>3d}/{n_img} = {100*maioria[m]/n_img:>4.0f}%")
                linhas.append({"painel": rot_painel, "regra": rot_regra, "metodo": m,
                               "aceita_individual_n": n, "aceita_individual_N": N,
                               "aceita_individual_pct": round(100 * n / N, 1),
                               "aceita_maioria_n": maioria[m], "aceita_maioria_N": n_img,
                               "aceita_maioria_pct": round(100 * maioria[m] / n_img, 1)})

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"\n[A13] {OUT.name} gravado.")
    print("\n  Publicado no manuscrito (tab_resultado_01): M3 341/738=46%, "
          "M1 190/738=26%, M2 266/738=36%.")


if __name__ == "__main__":
    main()
