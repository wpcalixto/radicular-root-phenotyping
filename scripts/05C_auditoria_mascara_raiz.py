#!/usr/bin/env python3
"""
Title:
    Root-mask overlap with reconstructed regions
File type:
    Script
Purpose:
    Crosses each inpainting mask with the final M3 root mask and reports the fraction of detected
    root pixels inside the reconstructed region and root density inside versus outside it.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-12
Date:
    2026-07-12
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
    - saidas/05A_tratadas/_mascaras
    - saidas/05A_tratadas/_mascaras/<data>/R##.png
    - saidas/08_combinado_limpo/masks
    - saidas/08_combinado_limpo/masks/<data>/R##.png
Outputs:
    - metricas/deflash_root_overlap.csv
Dependencies:
    - cv2
    - numpy
    - local: config
Execution:
    python scripts/05C_auditoria_mascara_raiz.py (from a workspace prepared with
    tools/prepare_workspace.py)
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
Fase 05C — Auditoria QUANTITATIVA das máscaras do deflash (sem nova rodada humana).

Cruza, por imagem, a máscara de inpainting (05A) com a máscara radicular final M3
(Fase 08, segmentada sobre a imagem 05A tratada). Responde às perguntas do parecer:
  - Quanto do sinal radicular DETECTADO caiu DENTRO da região reconstruída?
    (frac_root_in_mask = raiz∩inpaint / raiz_total) — proxy de "a máscara pegou raiz".
  - A região reconstruída é mais ou menos "radicular" que o restante?
    (dens_in = raiz∩inpaint / inpaint ; dens_out = raiz_fora / area_valida ; razao)
Se frac_root_in_mask é pequena e dens_in << dens_out, a máscara incidiu sobre zonas de
reflexo pobres em raiz e o LaMa não fabricou textura radicular — pouca perda de sinal real.

Entrada:
  saidas/05A_tratadas/_mascaras/<data>/R##.png   (inpaint)
  saidas/08_combinado_limpo/masks/<data>/R##.png (M3, detecção sobre 05A)
Saída:
  metricas/deflash_root_overlap.csv   (1 linha por imagem) + resumo no stdout
"""
import os
import sys
import csv
import statistics as st

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

IP_DIR = C.SAIDAS / "05A_tratadas" / "_mascaras"
M3_DIR = C.SAIDAS / "08_combinado_limpo" / "masks"
OUT = C.METRICAS / "deflash_root_overlap.csv"


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
    m3s = sorted(M3_DIR.rglob("*.png"))
    rows = []
    for p in m3s:
        rel = p.relative_to(M3_DIR)
        ipp = IP_DIR / rel
        if not ipp.exists():
            print(f"  [pula] {p.stem}: sem inpaint"); continue
        M3 = cv2.imread(str(p), 0) > 127
        IP = cv2.imread(str(ipp), 0) > 127
        if IP.shape != M3.shape:
            IP = cv2.resize(IP.astype(np.uint8), (M3.shape[1], M3.shape[0]),
                            interpolation=cv2.INTER_NEAREST) > 0
        H, W = M3.shape
        root_total = int(M3.sum())
        root_in = int((M3 & IP).sum())
        ip_px = int(IP.sum())
        valid = H * W - ip_px
        root_out = root_total - root_in
        dens_in = root_in / ip_px if ip_px else 0.0
        dens_out = root_out / valid if valid else 0.0
        rows.append({
            "image_id": p.stem, "data": rel.parts[0] if len(rel.parts) > 1 else "",
            "root_total_px": root_total, "root_in_mask_px": root_in,
            "frac_root_in_mask_pct": round(100 * root_in / root_total, 3) if root_total else 0,
            "inpaint_px": ip_px, "inpaint_pct": round(100 * ip_px / (H * W), 3),
            "dens_in": round(dens_in, 5), "dens_out": round(dens_out, 5),
            "razao_in_out": round(dens_in / dens_out, 3) if dens_out else 0,
        })

    C.METRICAS.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    fr = [r["frac_root_in_mask_pct"] for r in rows]
    di = [r["dens_in"] for r in rows]
    do = [r["dens_out"] for r in rows]
    ra = [r["razao_in_out"] for r in rows if r["razao_in_out"] > 0]
    qf = st.quantiles(fr, n=4)

    def line(name, v, dec=3):
        q = st.quantiles(v, n=4)
        return (f"{name}: mediana={st.median(v):.{dec}f} [Q1={q[0]:.{dec}f} Q3={q[2]:.{dec}f}] "
                f"min={min(v):.{dec}f} max={max(v):.{dec}f} media={st.mean(v):.{dec}f}")

    print(f"\n[05C] Auditoria quantitativa — {len(rows)} imagens -> {OUT.relative_to(C.ROOT)}")
    print("  " + line("frac_root_in_mask (%)", fr))
    print("  " + line("densidade DENTRO da mascara", di, 4))
    print("  " + line("densidade FORA (area valida)", do, 4))
    print("  " + line("razao dentro/fora", ra, 3))
    n_maior = sum(1 for r in rows if r["razao_in_out"] > 1)
    print(f"  imagens com densidade DENTRO > FORA: {n_maior}/{len(rows)}")
    print(f"  frac_root_in_mask: {sum(1 for x in fr if x < 5)}/{len(fr)} imagens abaixo de 5%")


if __name__ == "__main__":
    main()
