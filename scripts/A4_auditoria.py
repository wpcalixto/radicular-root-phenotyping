#!/usr/bin/env python3
"""
Title:
    Audit of vertical-distribution descriptors
File type:
    Script
Purpose:
    Checks redundancy among D50, D90, F_prof and B_d and the sensitivity of B_d to small mask
    components.
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
    - metricas/A4_profundidade.csv
    - saidas/05A_tratadas/_mascaras
    - saidas/08_combinado_limpo/masks
Outputs:
    - printed results only
Dependencies:
    - cv2
    - numpy
    - scipy
    - skimage
    - local: config
Execution:
    python scripts/A4_auditoria.py (from a workspace prepared with tools/prepare_workspace.py)
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
A4 — auditorias (orientador):
  (1) Redundância entre D50, D90, F_prof, B_d (Spearman; 82 imagens e 12 resumos por rizotron).
  (2) Sensibilidade de B_d = 1000*N_br/L_skel a pequenos componentes: remove componentes da
      máscara M3 abaixo de limiares e recomputa N_br/L_skel/B_d; verifica se a ordenação
      REF/T1 (~16) vs T2/T3 (~17-18) persiste.
"""
import os, sys, csv, math
import statistics as st
from collections import defaultdict
import numpy as np, cv2
from scipy.stats import spearmanr
from scipy.ndimage import label, convolve
from skimage.morphology import skeletonize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

MASK = C.SAIDAS / "08_combinado_limpo" / "masks"
INP = C.SAIDAS / "05A_tratadas" / "_mascaras"
A4 = C.METRICAS / "A4_profundidade.csv"
TRATS = ["REF", "T1", "T2", "T3"]


def Lskel(S):
    """
    Purpose:
        Skeleton length with neighbour links.
    Parameters:
        S: skeleton
    Returns:
        float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    nh = np.logical_and(S[:, :-1], S[:, 1:]).sum(); nv = np.logical_and(S[:-1, :], S[1:, :]).sum()
    nd = np.logical_and(S[:-1, :-1], S[1:, 1:]).sum() + np.logical_and(S[:-1, 1:], S[1:, :-1]).sum()
    return nh + nv + nd * math.sqrt(2)


def nbr(S):
    """
    Purpose:
        Count branch nodes of a skeleton.
    Parameters:
        S: skeleton
    Returns:
        int
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    deg = convolve(S.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - S
    J = S & (deg >= 3)
    return int(label(J, structure=np.ones((3, 3)))[1])


def bd_thresh(Mv, minsz):
    """
    Purpose:
        Branching density after removing components below a size threshold.
    Parameters:
        Mv: valid mask
        minsz: minimum component size
    Returns:
        tuple
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    if minsz > 0:
        lab, n = label(Mv, structure=np.ones((3, 3)))
        sizes = np.bincount(lab.ravel())
        keep = np.isin(lab, np.where(sizes >= minsz)[0][1:] if n else [])
        Mv = keep
    if not Mv.any():
        return None
    S = skeletonize(Mv)
    L = Lskel(S)
    return 1000 * nbr(S) / L if L > 0 else 0


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
    rows = list(csv.DictReader(open(A4, encoding="utf-8")))
    for r in rows:
        for k in ("D50", "D90", "F_prof", "B_d"):
            r[k] = float(r[k])
    # (1) redundância
    print("=== (1) Redundância (Spearman) — 82 imagens ===")
    ks = ["D50", "D90", "F_prof", "B_d"]
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            rho = spearmanr([r[ks[i]] for r in rows], [r[ks[j]] for r in rows])[0]
            print(f"  {ks[i]:7s} x {ks[j]:7s}  ρ={rho:+.2f}")
    # 12 resumos por rizotron (C1-C6)
    byr = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["coleta"] and int(r["coleta"]) <= 6:
            for k in ks:
                byr[r["rizotron"]][k].append(r[k])
    riz = {rz: {k: st.mean(v[k]) for k in ks} for rz, v in byr.items()}
    print("=== (1b) Redundância — 12 resumos por rizotron ===")
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            rho = spearmanr([riz[rz][ks[i]] for rz in riz], [riz[rz][ks[j]] for rz in riz])[0]
            print(f"  {ks[i]:7s} x {ks[j]:7s}  ρ={rho:+.2f}")

    # (2) sensibilidade de B_d
    print("\n=== (2) B_d por tratamento após remover componentes < limiar (C1-C6, rizotron-first) ===")
    col = {r["image_id"]: (int(r["coleta"]) if r["coleta"] else 99) for r in rows}
    trat = {r["image_id"]: r["tratamento"] for r in rows}
    print("  limiar(px)   REF     T1      T2      T3    ordenação T2/T3>REF/T1?")
    for minsz in [0, 100, 300]:
        bd_img = {}
        for p in sorted(MASK.rglob("*.png")):
            img = p.stem
            if col.get(img, 99) > 6:
                continue
            rel = p.relative_to(MASK); M = cv2.imread(str(p), 0) > 127
            ipp = INP / rel; ip = (cv2.imread(str(ipp), 0) > 127) if ipp.exists() else np.zeros_like(M)
            if ip.shape != M.shape:
                ip = cv2.resize(ip.astype(np.uint8), (M.shape[1], M.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
            b = bd_thresh(M & ~ip, minsz)
            if b is not None:
                bd_img[img] = b
        byr2 = defaultdict(list)
        for img, b in bd_img.items():
            byr2[img.split("_")[0]].append(b)
        tm = {}
        for t in TRATS:
            rr = [st.mean(byr2[rz]) for rz in byr2 if C.tratamento(rz)[0] == t]
            tm[t] = st.mean(rr)
        ok = min(tm["T2"], tm["T3"]) > max(tm["REF"], tm["T1"])
        print(f"  {minsz:4d}       {tm['REF']:.1f}    {tm['T1']:.1f}    {tm['T2']:.1f}    {tm['T3']:.1f}   {'SIM' if ok else 'não estrita'}")


if __name__ == "__main__":
    main()
