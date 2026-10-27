#!/usr/bin/env python3
"""
Title:
    Representative and failure cases
File type:
    Script
Purpose:
    Selects six images by objective rules and writes four-panel figures and the per-case metric
    table (score, acceptance, flags, M3 composition).
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
    - metricas/A1_composicao_m3.csv
    - metricas/notas_recebidas
    - metricas/pretratamento_05A.csv
    - metricas/review_key.csv
Outputs:
    - metricas/A5_casos.csv
Dependencies:
    - cv2
    - matplotlib
    - numpy
    - openpyxl
    - local: config
Execution:
    python scripts/A5_casos.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: re-executed (with run_A5_sem_render.py and with rendering); A5_casos.csv
    byte-identical; regenerated PDFs pixel-identical (72 dpi) to the RSOS files. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Resultado adicional A5 — casos representativos e diagnósticos de falha.
Seleciona 6 imagens por REGRAS OBJETIVAS (maior/menor nota de M3; maior discordância entre
avaliadores; maior excesso de solo; maior falta de raiz; maior fração reconstruída) e gera,
para cada uma, quatro painéis (condicionada, M1, M2, M3, raízes em verde), além de uma tabela
de métricas por caso (nota, aceitação, sinalizadores, composição de M3).
Saídas: metricas/A5_casos.csv + 18_figura_resultado_<i><a-d>.pdf (i=1..6).
"""
import os, sys, csv, io, re, glob
import statistics as st
from collections import defaultdict
import numpy as np, cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

NOTAS = C.METRICAS / "notas_recebidas"
KEY = C.METRICAS / "review_key.csv"
DEFLASH = C.METRICAS / "pretratamento_05A.csv"
COMPO = C.METRICAS / "A1_composicao_m3.csv"
OUT = C.ROOT / "Artigo_revista"
BASE = C.SAIDAS
XO = ["image_id", "data", "codigo", "n0", "n1", "n2", "n3", "n4", "aceita", "falta", "solo", "glare", "frag", "obs"]


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
    for i in range(5):
        if str(r["n%d" % i]).strip().lower() == "x":
            return i
    return None
def mk(v):
    """
    Purpose:
        Return 1 when a spreadsheet cell is marked with x, otherwise 0.
    Parameters:
        v: cell value
    Returns:
        int
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return 1 if str(v).strip().lower() == "x" else 0
def ac(v):
    """
    Purpose:
        Return 1 when an acceptance cell records acceptance (x, sim, 1, yes or s), otherwise 0.
    Parameters:
        v: cell value
    Returns:
        int
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return 1 if str(v).strip().lower() in ("x", "sim", "1", "yes", "s") else 0
def rd_xlsx(f):
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
    return [{XO[i]: (r[i] if i < len(r) else "") for i in range(len(XO))}
            for r in ws.iter_rows(min_row=4, values_only=True) if r and r[0]]
def rd_csv(f):
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


def per_image_m3():
    """
    Purpose:
        Aggregate M3 judgements per image.
    Parameters:
        none
    Returns:
        dict
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    key = {(r["image_id"], r["codigo"]): r["metodo_real"] for r in csv.DictReader(open(KEY, encoding="utf-8"))}
    agg = defaultdict(lambda: {"Q": [], "ac": [], "falta": [], "solo": [], "frag": [], "n": 0, "data": ""})
    for f in sorted(glob.glob(str(NOTAS / "*.xlsx")) + glob.glob(str(NOTAS / "*.csv"))):
        got = rd_xlsx(f) if f.lower().endswith(".xlsx") else rd_csv(f)
        for r in got:
            if key.get((r["image_id"], r["codigo"])) == "Comb":
                q = qg(r); a = agg[r["image_id"]]
                if q is not None:
                    a["Q"].append(q); a["ac"].append(ac(r["aceita"]))
                    a["falta"].append(mk(r["falta"])); a["solo"].append(mk(r["solo"])); a["frag"].append(mk(r["frag"]))
                    a["n"] += 1; a["data"] = r["data"]
    out = {}
    for img, a in agg.items():
        if a["Q"]:
            out[img] = {"Q_mean": st.mean(a["Q"]), "Q_std": st.pstdev(a["Q"]) if len(a["Q"]) > 1 else 0,
                        "n": a["n"], "n_ac": sum(a["ac"]), "n_falta": sum(a["falta"]),
                        "n_solo": sum(a["solo"]), "n_frag": sum(a["frag"]),
                        "aceita": st.mean(a["ac"]), "falta": st.mean(a["falta"]), "solo": st.mean(a["solo"]),
                        "frag": st.mean(a["frag"]), "data": a["data"]}
    return out


def overlay(rgb, mask, cor):
    """
    Purpose:
        Overlay a binary mask on an RGB image with a given colour.
    Parameters:
        rgb: RGB image
        mask: binary mask
        cor: RGB colour
    Returns:
        image array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    img = rgb.copy()
    if mask is not None:
        img[mask] = cor
    h, w = img.shape[:2]
    fig = plt.figure(figsize=(4, 4 * h / w)); ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img); ax.set_axis_off()
    return fig


def render(img, data, idx):
    """
    Purpose:
        Write the four-panel figure of one case.
    Parameters:
        img: image identifier
        data: date
        idx: case index
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    G = [0.15, 0.85, 0.15]
    paths = {"a": (BASE / "05A_tratadas" / "masks" if False else BASE / "05A_tratadas") / data / (img + ".png"),
             "cond": BASE / "05A_tratadas" / data / (img + ".png"),
             "b": BASE / "07_frangi" / "masks" / data / (img + ".png"),
             "c": BASE / "06C_inferencia" / "masks" / data / (img + ".png"),
             "d": BASE / "08_combinado_limpo" / "masks" / data / (img + ".png")}
    rgb = np.asarray(plt.imread(str(paths["cond"])))[:, :, :3].astype(float)
    if rgb.max() > 1: rgb /= 255.0
    for lab, mp in [("a", None), ("b", paths["b"]), ("c", paths["c"]), ("d", paths["d"])]:
        m = None
        if mp is not None:
            m = cv2.imread(str(mp), 0) > 127
            if m.shape != rgb.shape[:2]:
                m = cv2.resize(m.astype(np.uint8), (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
        fig = overlay(rgb, m, G)
        fig.savefig(str(OUT / f"18_figura_resultado_{idx}{lab}.pdf"), format="pdf", dpi=300)
        plt.close(fig)


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
    m3 = per_image_m3()
    infl = {r["image_id"]: float(r["pct_inpintado"]) for r in csv.DictReader(open(DEFLASH, encoding="utf-8"))}
    compo = {r["image_id"]: r for r in csv.DictReader(open(COMPO, encoding="utf-8"))}
    imgs = list(m3)
    regras = [
        ("maior nota M3", max, lambda i: m3[i]["Q_mean"]),
        ("menor nota M3", min, lambda i: m3[i]["Q_mean"]),
        ("maior discordância", max, lambda i: m3[i]["Q_std"]),
        ("maior excesso de solo", max, lambda i: m3[i]["solo"]),
        ("maior falta de raiz", max, lambda i: m3[i]["falta"]),
        ("maior fração reconstruída", max, lambda i: infl.get(i, 0)),
    ]
    escolhidos, sel = [], set()
    for nome, agg, key in regras:
        cand = sorted([i for i in imgs if i not in sel], key=key, reverse=(agg is max))
        i = cand[0]; sel.add(i); escolhidos.append((nome, i))
    rows = []
    print("[A5] casos selecionados:")
    for idx, (nome, img) in enumerate(escolhidos, 1):
        d = m3[img]; cp = compo.get(img, {})
        render(img, d["data"], idx)
        r = {"caso": idx, "regra": nome, "image_id": img,
             "Q_M3": round(d["Q_mean"], 2), "Q_std": round(d["Q_std"], 2), "n_eval": d["n"],
             "n_ac": d["n_ac"], "n_solo": d["n_solo"], "n_falta": d["n_falta"], "n_frag": d["n_frag"],
             "aceita": round(d["aceita"], 2),
             "falta": round(d["falta"], 2), "solo": round(d["solo"], 2), "frag": round(d["frag"], 2),
             "inpint_pct": round(infl.get(img, 0), 1),
             "P_M1": cp.get("P_M1", ""), "P_M2": cp.get("P_M2", ""), "P_int": cp.get("P_int", "")}
        rows.append(r)
        print(f"  {idx}. {nome:26s} {img}  Q={r['Q_M3']}±{r['Q_std']} aceita={r['aceita']} "
              f"solo={r['solo']} falta={r['falta']} inp={r['inpint_pct']}%")
    with open(C.METRICAS / "A5_casos.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("  -> metricas/A5_casos.csv + 18_figura_resultado_<1-6><a-d>.pdf")


if __name__ == "__main__":
    main()
