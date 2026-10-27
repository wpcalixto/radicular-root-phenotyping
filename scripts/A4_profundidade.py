#!/usr/bin/env python3
"""
Title:
    Vertical-distribution descriptors
File type:
    Script
Purpose:
    Computes D50, D90, deep-region fraction and branching density from the final M3 masks excluding
    reconstructed pixels.
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
    - metricas/root_features_by_image.csv
    - saidas/05A_tratadas/_mascaras
    - saidas/08_combinado_limpo/masks
Outputs:
    - metricas/A4_profundidade.csv
Dependencies:
    - cv2
    - numpy
    - local: config
Execution:
    python scripts/A4_profundidade.py (from a workspace prepared with tools/prepare_workspace.py)
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
Resultado adicional A4 — descritores de distribuição vertical (substituem Dmax/Wmax saturados).
Por imagem, da máscara final M3 (excluindo a região reconstruída):
  D50  profundidade normalizada que contém 50% dos pixels radiculares (mediana vertical);
  D90  profundidade que contém 90%;
  F_prof  fração de pixels radiculares abaixo de 0,60 da profundidade normalizada;
  B_d  densidade de ramificação = N_br / L_skel (nós por kpx).
Pré-registrados (4 descritores). Saída: metricas/A4_profundidade.csv + resumo por tratamento (C1-C6).
"""
import os, sys, csv
import statistics as st
from collections import defaultdict
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

MASK = C.SAIDAS / "08_combinado_limpo" / "masks"
INP = C.SAIDAS / "05A_tratadas" / "_mascaras"
FEAT = C.METRICAS / "root_features_by_image.csv"
TRATS = ["REF", "T1", "T2", "T3"]


def vert(mask):
    """D50, D90, F_prof a partir do perfil vertical (linha = profundidade)."""
    H = mask.shape[0]
    perfil = mask.sum(axis=1).astype(float)     # pixels radiculares por linha
    tot = perfil.sum()
    if tot == 0:
        return None
    cum = np.cumsum(perfil) / tot
    d50 = np.searchsorted(cum, 0.5) / H
    d90 = np.searchsorted(cum, 0.9) / H
    lim = int(0.60 * H)
    f_prof = perfil[lim:].sum() / tot
    return round(d50, 4), round(d90, 4), round(f_prof, 4)


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
    feat = {r["image_id"]: r for r in csv.DictReader(open(FEAT, encoding="utf-8"))}
    rows = []
    for p in sorted(MASK.rglob("*.png")):
        rel = p.relative_to(MASK)
        M = cv2.imread(str(p), 0) > 127
        ipp = INP / rel
        ip = (cv2.imread(str(ipp), 0) > 127) if ipp.exists() else np.zeros_like(M)
        if ip.shape != M.shape:
            ip = cv2.resize(ip.astype(np.uint8), (M.shape[1], M.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
        Mv = M & ~ip
        v = vert(Mv)
        if v is None:
            continue
        img = p.stem; fr = feat.get(img, {})
        nbr = float(fr.get("N_br", 0)); lsk = float(fr.get("L_skel_px", 1)) or 1
        rows.append({"image_id": img, "rizotron": img.split("_")[0], "tratamento": C.tratamento(img.split("_")[0])[0],
                     "coleta": fr.get("coleta", ""), "D50": v[0], "D90": v[1], "F_prof": v[2],
                     "B_d": round(nbr / lsk * 1000, 4)})
    with open(C.METRICAS / "A4_profundidade.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    # resumo por tratamento: seis coletas comuns C1-C6, rizotron-first, média±dp
    common = [r for r in rows if r["coleta"] and int(r["coleta"]) <= 6]
    by_riz = defaultdict(list)
    for r in common:
        by_riz[r["rizotron"]].append(r)
    print(f"[A4] {len(rows)} imagens. Descritores verticais por tratamento (C1-C6, rizotron-first, média±dp):")
    print("  Trat   D50            D90            F_prof         B_d (nós/kpx)")
    for t in TRATS:
        rizs = [rz for rz in by_riz if C.tratamento(rz)[0] == t]
        cols = {}
        for k in ("D50", "D90", "F_prof", "B_d"):
            vals = [st.mean(x[k] for x in by_riz[rz]) for rz in rizs]
            cols[k] = (st.mean(vals), st.stdev(vals) if len(vals) > 1 else 0)
        print(f"  {t:4s}  {cols['D50'][0]:.3f}±{cols['D50'][1]:.3f}  {cols['D90'][0]:.3f}±{cols['D90'][1]:.3f}  "
              f"{cols['F_prof'][0]:.3f}±{cols['F_prof'][1]:.3f}  {cols['B_d'][0]:.1f}±{cols['B_d'][1]:.1f}")
    print("  -> metricas/A4_profundidade.csv")


if __name__ == "__main__":
    main()
