#!/usr/bin/env python3
"""
Title:
    Composition of M3
File type:
    Script
Purpose:
    Decomposes each final M3 mask into M1-exclusive, M2-exclusive and common fractions and relates
    composition to quality-score differences and M3 issue flags.
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
    - metricas/08D_selecao_por_imagem.csv
    - metricas/notas_recebidas
    - metricas/review_key.csv
    - saidas/06C_inferencia/masks
    - saidas/07_frangi/masks
    - saidas/08_combinado_limpo/masks
Outputs:
    - metricas/A1_composicao_m3.csv
Dependencies:
    - cv2
    - numpy
    - openpyxl
    - scipy
    - skimage
    - local: config
Execution:
    python scripts/A1_composicao_m3.py (from a workspace prepared with tools/prepare_workspace.py)
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
Resultado adicional A1 — Composição e contribuição dos componentes da máscara M3.
Por imagem: P_M1 = |R(M1)\\M2|/|M3|, P_M2 = |M2\\R(M1)|/|M3|, P_int = |R(M1)∩M2|/|M3|,
com R(M1) = Frangi refinado (denoise do 08E) e M3 = fecho(R(M1)∪M2) (08_combinado_limpo).
Relaciona a composição a DeltaQ_31=Q_M3-Q_M1, DeltaQ_32=Q_M3-Q_M2 e aos sinalizadores de M3.
Saída: metricas/A1_composicao_m3.csv + impressão dos coeficientes.
"""
import os, sys, csv, io, re, glob
import statistics as st
from collections import defaultdict
import numpy as np, cv2
from scipy.stats import spearmanr
from skimage.measure import label, regionprops
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

FR = C.SAIDAS / "07_frangi" / "masks"
EX = C.SAIDAS / "06C_inferencia" / "masks"
M3D = C.SAIDAS / "08_combinado_limpo" / "masks"
PORIMG = C.METRICAS / "08D_selecao_por_imagem.csv"
NOTAS = C.METRICAS / "notas_recebidas"
KEY = C.METRICAS / "review_key.csv"
# parâmetros do denoise_frangi (08E) — replicados
AREA_GRANDE, ECC_MIN, AREA_FINA_MIN = 350, 0.90, 60


def denoise_frangi(m1):
    """
    Purpose:
        Remove small, rounded M1 components and keep elongated or large ones (refinement used for the final M3).
    Parameters:
        m1: M1 binary mask
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    lab = label(m1); keep = np.zeros_like(m1, dtype=bool)
    for p in regionprops(lab):
        if p.area >= AREA_GRANDE or (p.area >= AREA_FINA_MIN and p.eccentricity >= ECC_MIN):
            keep[lab == p.label] = True
    return keep


# --- sinalizadores de M3 por imagem (fração dos 9 avaliadores) ---
XO = ["image_id", "data", "codigo", "n0", "n1", "n2", "n3", "n4", "aceita", "falta", "solo", "glare", "frag", "obs"]
def _rows_xlsx(f):
    ws = openpyxl.load_workbook(f, data_only=True).active
    return [{XO[i]: (r[i] if i < len(r) else "") for i in range(len(XO))}
            for r in ws.iter_rows(min_row=4, values_only=True) if r and r[0]]
def _rows_csv(f):
    raw = open(f, encoding="utf-8-sig").read(); l0 = raw.splitlines()[0] if raw.splitlines() else ""
    d = ";" if l0.count(";") > l0.count(",") else ","
    L = [r for r in csv.reader(io.StringIO(raw), delimiter=d) if any(c.strip() for c in r)]
    return [{XO[i]: (row[i] if i < len(row) else "") for i in range(min(len(XO), len(row)))} for row in L[1:]]
def mark(v):
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


def flags_m3():
    """
    Purpose:
        Count M3 issue flags per image from the assessor sheets.
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
    agg = defaultdict(lambda: defaultdict(list))
    for f in sorted(glob.glob(str(NOTAS / "*.xlsx")) + glob.glob(str(NOTAS / "*.csv"))):
        got = _rows_xlsx(f) if f.lower().endswith(".xlsx") else _rows_csv(f)
        for r in got:
            if key.get((r["image_id"], r["codigo"])) == "Comb":     # M3
                for fl in ("falta", "solo", "frag"):
                    agg[r["image_id"]][fl].append(mark(r[fl]))
    return {img: {fl: st.mean(v[fl]) for fl in v} for img, v in agg.items()}


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
    Q = {r["image_id"]: r for r in csv.DictReader(open(PORIMG, encoding="utf-8"))}
    fl = flags_m3()
    rows = []
    for p in sorted(FR.rglob("*.png")):
        rel = p.relative_to(FR); pe = EX / rel; pm3 = M3D / rel
        if not (pe.exists() and pm3.exists()):
            continue
        m1 = cv2.imread(str(p), 0) > 127
        m2 = cv2.imread(str(pe), 0) > 127
        m3 = cv2.imread(str(pm3), 0) > 127
        rm1 = denoise_frangi(m1)
        a3 = int(m3.sum())
        if a3 == 0:
            continue
        f_only = int((rm1 & ~m2).sum()); e_only = int((m2 & ~rm1).sum()); inter = int((rm1 & m2).sum())
        img = p.stem; q = Q.get(img, {})
        r = {"image_id": img, "P_M1": round(f_only / a3, 4), "P_M2": round(e_only / a3, 4),
             "P_int": round(inter / a3, 4), "M3_px": a3,
             "Q_M1": float(q["M1"]) if q else "", "Q_M2": float(q["M2"]) if q else "", "Q_M3": float(q["M3"]) if q else ""}
        if q:
            r["dQ31"] = round(float(q["M3"]) - float(q["M1"]), 3)
            r["dQ32"] = round(float(q["M3"]) - float(q["M2"]), 3)
        r["flag_falta"] = round(fl.get(img, {}).get("falta", 0), 3)
        r["flag_solo"] = round(fl.get(img, {}).get("solo", 0), 3)
        r["flag_frag"] = round(fl.get(img, {}).get("frag", 0), 3)
        rows.append(r)

    with open(C.METRICAS / "A1_composicao_m3.csv", "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    pf = [r["P_M1"] for r in rows]; pe = [r["P_M2"] for r in rows]; pi = [r["P_int"] for r in rows]
    print(f"[A1] {len(rows)} imagens")
    print(f"  Composição de M3 (média±dp): P_M1(Frangi excl.)={st.mean(pf)*100:.1f}±{st.stdev(pf)*100:.1f}%  "
          f"P_M2(PRMI excl.)={st.mean(pe)*100:.1f}±{st.stdev(pe)*100:.1f}%  P_int={st.mean(pi)*100:.1f}±{st.stdev(pi)*100:.1f}%")
    print(f"  soma média = {(st.mean(pf)+st.mean(pe)+st.mean(pi))*100:.1f}% (resto = fecho morfológico)")
    d31 = [r["dQ31"] for r in rows if "dQ31" in r]; d32 = [r["dQ32"] for r in rows if "dQ32" in r]
    print(f"  ganho médio ΔQ(M3-M1)={st.mean(d31):+.2f}  ΔQ(M3-M2)={st.mean(d32):+.2f}")
    print("  --- correlações de Spearman (composição × ganho/sinalizadores) ---")
    for lab, x in [("P_M1", pf), ("P_M2", pe), ("P_int", pi)]:
        r31 = spearmanr(x, d31)[0]; r32 = spearmanr(x, d32)[0]
        print(f"    {lab}: vs ΔQ31 ρ={r31:+.2f} | vs ΔQ32 ρ={r32:+.2f}")
    for fk in ("flag_falta", "flag_solo", "flag_frag"):
        y = [r[fk] for r in rows]
        print(f"    {fk}: vs P_M1 ρ={spearmanr(pf,y)[0]:+.2f} | vs P_M2 ρ={spearmanr(pe,y)[0]:+.2f}")
    print("  -> metricas/A1_composicao_m3.csv")


if __name__ == "__main__":
    main()
