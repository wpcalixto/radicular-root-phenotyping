#!/usr/bin/env python3
"""
Title:
    Classical segmentation M1 (Frangi)
File type:
    Script
Purpose:
    Applies photometric flat-field correction, residual-glare thresholding and multiscale Frangi
    vesselness with morphological post-processing to the conditioned images, producing M1 masks,
    glare masks and overlays.
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
    - saidas/05A_tratadas
Outputs:
    - metricas/frangi_parameters.csv
    - saidas/07_frangi
    - saidas/07_frangi/glare/<data>/R##.png
    - saidas/07_frangi/masks/<data>/R##.png
    - saidas/07_frangi/overlays/<data>/R##.png
Dependencies:
    - cv2
    - numpy
    - skimage
    - local: config
Execution:
    python scripts/07_frangi.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 07 — Correção fotométrica, tratamento do glare e segmentação clássica (Frangi).

Entrada: saidas/05A_tratadas/<data>/R##.png (registradas + SEM flash, Fase 05A).
IMPORTANTE: usa as MESMAS imagens tratadas que o modelo externo (Fase 06C), para que a
comparação entre métodos (Fase 08) seja justa. O flat-field abaixo é realce fotométrico
do método clássico (não remoção de flash — isso já foi feito na 05A).
Pipeline (por imagem):
  CIELAB L* -> normaliza L_n -> flat-field (campo gaussiano) -> CLAHE
  -> máscara de glare M_glare (região válida M_valid = 1 - M_glare)
  -> Frangi multiescala V -> limiar adaptativo T_i (Otsu/percentil)
  -> M_frangi = (V>=T_i) & M_valid -> remove componentes < A_MIN.

Saídas:
  saidas/07_frangi/masks/<data>/R##.png        (máscara binária M^Frangi)
  saidas/07_frangi/overlays/<data>/R##.png     (raiz em verde sobre a imagem)
  saidas/07_frangi/glare/<data>/R##.png        (máscara de glare)
  metricas/frangi_parameters.csv               (parâmetros + estatísticas por imagem)
"""
import os
import sys
import csv
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from skimage import io, img_as_float, img_as_ubyte
from skimage.color import rgb2lab
from skimage.filters import frangi, gaussian, threshold_otsu
from skimage.exposure import equalize_adapthist
from skimage.morphology import binary_opening, binary_closing, disk, remove_small_objects
from skimage.measure import label

IN_DIR = C.SAIDAS / "05A_tratadas"      # imagens tratadas (sem flash) — mesmas da Fase 06C
OUT = C.SAIDAS / "07_frangi"
CSV = C.METRICAS / "frangi_parameters.csv"
EPS = 1e-8


def segmentar(path):
    """
    Purpose:
        Segment one conditioned image with photometric correction, glare thresholding and Frangi filtering.
    Parameters:
        path: conditioned image
    Returns:
        tuple (rgb, M1 mask, glare mask)
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rgb = img_as_float(io.imread(path))[:, :, :3]
    L = rgb2lab(rgb)[:, :, 0]
    Ln = (L - L.min()) / (L.max() - L.min() + EPS)

    # correção de iluminação (flat-field)
    BL = gaussian(Ln, sigma=C.FLATFIELD_SIGMA)
    Lcorr = np.clip(Ln / (BL + EPS) * np.median(BL), 0, 1)

    # realce local
    Lclahe = equalize_adapthist(Lcorr, clip_limit=C.CLAHE_CLIP)

    # glare residual (o flash já foi removido na 05A; aqui tratamos o que sobrar)
    Mglare = Lclahe >= C.GLARE_TAU_L
    Mglare = binary_closing(binary_opening(Mglare, disk(3)), disk(3))

    # ramo de inpainting do glare LIMITADO (metodologia): se o glare é pequeno, reconstrói
    # a região (Telea) e ela passa a ser válida; se for extenso, trata como inválida.
    frac_glare = float(Mglare.mean())
    if 0 < frac_glare <= C.GLARE_INPAINT_MAX:
        Lu = (Lclahe * 255).astype(np.uint8)
        Lu = cv2.inpaint(Lu, (Mglare * 255).astype(np.uint8),
                         C.GLARE_INPAINT_RADIUS, cv2.INPAINT_TELEA)
        Lclahe = Lu.astype(np.float32) / 255.0
        Mvalid = np.ones_like(Mglare)
    else:
        Mvalid = ~Mglare

    # Frangi multiescala
    V = frangi(Lclahe, sigmas=C.FRANGI_SIGMAS, black_ridges=C.FRANGI_BLACK_RIDGES)
    V = V / (V.max() + EPS)

    # limiar adaptativo por imagem
    if C.THRESH_METHOD == "percentile":
        T = float(np.percentile(V, C.THRESH_PERCENTILE))
    else:
        try:
            T = float(threshold_otsu(V[V > 0]))
        except Exception:
            T = C.FRANGI_THRESHOLD

    M = (V >= T) & Mvalid
    # morfologia da máscara radicular final (metodologia): abertura -> fechamento.
    # A ABERTURA por erosão apaga raízes finas -> é feita por ÁREA (remove_small_objects);
    # o FECHAMENTO (disk pequeno) conecta lacunas curtas sem apagar raízes.
    if C.MORPH_OPEN_R:
        M = binary_opening(M, disk(C.MORPH_OPEN_R))
    M = remove_small_objects(M, min_size=C.A_MIN)      # "abertura por área" (preserva finas)
    if C.MORPH_CLOSE_R:
        M = binary_closing(M, disk(C.MORPH_CLOSE_R))

    n_comp = int(label(M).max())
    return rgb, M, Mglare, T, n_comp


def salvar(rel, rgb, M, Mglare):
    """
    Purpose:
        Write the M1 mask, glare mask and overlay of one image.
    Parameters:
        rel: relative path
        rgb: image
        M: M1 mask
        Mglare: glare mask
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    for sub in ("masks", "overlays", "glare"):
        (OUT / sub / rel.parent).mkdir(parents=True, exist_ok=True)
    io.imsave(OUT / "masks" / rel, img_as_ubyte(M), check_contrast=False)
    io.imsave(OUT / "glare" / rel, img_as_ubyte(Mglare), check_contrast=False)
    ov = (rgb * 255).astype(np.uint8).copy()
    ov[M, 1] = 255                       # raiz em verde
    io.imsave(OUT / "overlays" / rel, ov, check_contrast=False)


def main(limite=None):
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
    # só pastas de data (R##.png); ignora auxiliares como _mascaras/ e _previas/
    imgs = sorted(p for p in IN_DIR.rglob("*.png")
                  if not any(part.startswith("_") for part in p.relative_to(IN_DIR).parts))
    if limite:
        imgs = imgs[:limite]
    if not imgs:
        print("[Fase 07] Nenhuma imagem em saidas/05A_tratadas (rode a Fase 05A)."); return

    rows = []
    import time
    for k, p in enumerate(imgs, 1):
        rel = p.relative_to(IN_DIR)
        t = time.time()
        rgb, M, Mglare, T, n_comp = segmentar(p)
        salvar(rel, rgb, M, Mglare)
        H, W = M.shape
        root_px = int(M.sum()); glare_px = int(Mglare.sum())
        rows.append({
            "image_id": p.stem, "data": rel.parts[0] if len(rel.parts) > 1 else "",
            "threshold_T": round(T, 5), "root_px": root_px,
            "root_pct": round(100 * root_px / (H * W), 3),
            "glare_pct": round(100 * glare_px / (H * W), 3),
            "n_componentes": n_comp,
            "sigmas": str(list(C.FRANGI_SIGMAS)), "metodo_limiar": C.THRESH_METHOD,
            "A_min": C.A_MIN,
        })
        print(f"  [{k:2d}/{len(imgs)}] {rel}  root={rows[-1]['root_pct']:.2f}%  "
              f"glare={rows[-1]['glare_pct']:.2f}%  comp={n_comp}  ({time.time()-t:.1f}s)")

    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\n[Fase 07] {len(rows)} imagens segmentadas.")
    print(f"   Máscaras/overlays/glare: {OUT.relative_to(C.ROOT)}/")
    print(f"   Parâmetros: {CSV.relative_to(C.ROOT)}")


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(lim)
