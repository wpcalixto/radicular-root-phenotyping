#!/usr/bin/env python3
"""
Title:
    Projected length of harvested roots
File type:
    Script
Purpose:
    Segments the washed-root photographs, measures skeleton length and vertical extent in pixels and
    estimates the cm-per-pixel scale from the ruler by Fourier analysis, accepting units only under
    geometric criteria.
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
    - entradas/Raizes
    - figures/09B_raiz_colhida
Outputs:
    - metricas/root_harvested.csv
Dependencies:
    - PIL
    - cv2
    - numpy
    - pillow_heif
    - skimage
    - local: config
Execution:
    python scripts/09B_raiz_colhida.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 09B (refinamento) — Comprimento radicular FINAL a partir da raiz colhida (`Raizes/`).

As 12 imagens (`entradas/Raizes/*.heic`) mostram o sistema radicular lavado sobre fundo
branco COM trena (escala em cm). Este script:
  1. segmenta a raiz (não-branco e não-trena-amarela; mantém a massa principal + fragmentos);
  2. mede o comprimento por esqueleto (px) e a extensão vertical (px);
  3. estima a escala cm/px pela periodicidade das marcações da trena (FFT), com verificação
     de sanidade; se incerta, marca `escala_incerta` e deixa o cm em branco.

RESSALVAS (honestas): raízes finas pálidas são subestimadas (baixo contraste); a leitura
automática da trena é aproximada. É uma referência complementar ao proxy in-situ (L_skel).

Saída: metricas/root_harvested.csv
  (rizotron, root_px, skel_len_px, extensao_vert_px, cm_por_px, L_r_skel_cm, altura_cm, escala_flag)
"""
import os
import re
import sys
import csv
import glob

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

import pillow_heif
pillow_heif.register_heif_opener()
from PIL import Image, ImageOps
from skimage.morphology import skeletonize

RAIZES = C.ENTRADAS / "Raizes"


def carregar(path):
    """
    Purpose:
        Read a HEIC/JPEG washed-root photograph applying the EXIF orientation.
    Parameters:
        path: image path
    Returns:
        BGR image array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def segmentar(bgr):
    """
    Purpose:
        Segment roots excluding the light background and the yellow ruler in HSV space.
    Parameters:
        bgr: image array
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    H, S, V = hsv[:, :, 0].astype(int), hsv[:, :, 1], hsv[:, :, 2]
    branco = (V > 165) & (S < 45)
    amarelo = (H >= 18) & (H <= 42) & (S > 80) & (V > 120)     # trena
    raiz = ((~branco) & (~amarelo)).astype(np.uint8)
    raiz = cv2.morphologyEx(raiz, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(raiz)
    keep = np.zeros_like(raiz)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 300:                     # mantém massa + fragmentos de raiz
            keep[lab == i] = 1
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return keep, amarelo.astype(np.uint8)


def escala_trena(amarelo, gray):
    """cm/px pela periodicidade dos traços de cm da trena (FFT do perfil de INTENSIDADE
    cinza DENTRO da trena; os traços numerados de cm são escuros sobre o amarelo)."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(amarelo)
    if n <= 1:
        return None, "sem_trena", 0
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    ys, xs = np.where(lab == big)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    if (y1 - y0) < 2 * (x1 - x0):
        return None, "trena_horizontal", 0
    tap = (lab[y0:y1, x0:x1] == big)
    g = gray[y0:y1, x0:x1].astype(float)
    g[~tap] = np.nan
    perfil = np.nanmean(g, axis=1)                             # brilho médio por linha (traços = quedas)
    perfil = np.nan_to_num(perfil, nan=np.nanmean(perfil))
    perfil = perfil - perfil.mean()
    F = np.abs(np.fft.rfft(perfil * np.hanning(len(perfil))))
    freqs = np.fft.rfftfreq(len(perfil))
    lo = (freqs > 1 / 80) & (freqs < 1 / 12)                   # período 12–80 px (traço de cm)
    if not lo.any() or F[lo].max() == 0:
        return None, "sem_pico", 0
    period = 1.0 / freqs[lo][int(np.argmax(F[lo]))]            # px por 1 cm
    cm_px = 1.0 / period
    altura_cm = (y1 - y0) * cm_px
    flag = "ok" if 20 <= altura_cm <= 120 else "escala_incerta"
    return (cm_px if flag == "ok" else None), flag, round(altura_cm, 1)


def comprimento_skel(S):
    """
    Purpose:
        Estimate skeleton length counting horizontal/vertical and diagonal neighbour links.
    Parameters:
        S: binary skeleton
    Returns:
        float
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    n_h = int((S[:, :-1] & S[:, 1:]).sum())
    n_v = int((S[:-1, :] & S[1:, :]).sum())
    n_d = int((S[:-1, :-1] & S[1:, 1:]).sum() + (S[:-1, 1:] & S[1:, :-1]).sum())
    return n_h + n_v + n_d * (2 ** 0.5)


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
    OUTFIG = C.FIGURES / "09B_raiz_colhida"; OUTFIG.mkdir(parents=True, exist_ok=True)
    fs = sorted(glob.glob(str(RAIZES / "*.heic")))
    if not fs:
        print("[09B] Sem imagens em entradas/Raizes/"); return
    rows = []
    for f in fs:
        m = re.search(r"R(\d+)", os.path.basename(f))
        riz = f"R{int(m.group(1)):02d}" if m else os.path.basename(f)
        bgr = carregar(f)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        raiz, amarelo = segmentar(bgr)
        S = skeletonize(raiz > 0)
        skel_px = comprimento_skel(S)
        ys = np.where(raiz.any(axis=1))[0]
        vert = int(ys.max() - ys.min()) if len(ys) else 0
        cm_px, flag, alt = escala_trena(amarelo, gray)
        cm_px = cm_px if cm_px else ""
        alt = alt if alt else ""
        Lr_cm = round(skel_px * cm_px, 1) if cm_px else ""
        rows.append({"rizotron": riz, "root_px": int((raiz > 0).sum()),
                     "skel_len_px": round(skel_px, 1), "extensao_vert_px": vert,
                     "cm_por_px": round(cm_px, 5) if cm_px else "",
                     "L_r_skel_cm": Lr_cm, "altura_trena_cm": alt, "escala_flag": flag})
        # overlay p/ auditoria
        ov = bgr.copy(); ov[raiz > 0] = (0, 255, 0)
        h = 700; w = int(bgr.shape[1] * h / bgr.shape[0])
        cv2.imwrite(str(OUTFIG / f"{riz}.jpg"),
                    cv2.resize(np.hstack([bgr, ov]), (2 * w, h)), [cv2.IMWRITE_JPEG_QUALITY, 85])
        print(f"  {riz}: skel={skel_px:.0f}px vert={vert}px cm/px={cm_px if cm_px else '-'} "
              f"L_r={Lr_cm}cm ({flag})")

    with open(C.METRICAS / "root_harvested.csv", "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    ok = sum(1 for r in rows if r["escala_flag"] == "ok")
    print(f"\n[09B] {len(rows)} raízes colhidas -> metricas/root_harvested.csv "
          f"(escala cm confiável em {ok}/{len(rows)}); overlays em figures/09B_raiz_colhida/")


if __name__ == "__main__":
    main()
