#!/usr/bin/env python3
"""
Title:
    Specular-reflection conditioning by LaMa inpainting
File type:
    Script
Purpose:
    Detects specular reflection cores and reconstructs them by LaMa inpainting, producing the
    conditioned images used by all segmentation methods and the binary reconstruction masks; logs
    the reconstructed fraction per image.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-07
Date:
    2026-07-07
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
    - saidas/05_registradas
Outputs:
    - metricas/pretratamento_05A.csv
    - saidas/05A_tratadas
    - saidas/05A_tratadas/<data>/R##_<data>.png
    - saidas/05A_tratadas/_mascaras/<data>/R##_<data>.png
    - saidas/05A_tratadas/_previas/<image_id>_ANTES_DEPOIS.png
Dependencies:
    - PIL
    - cv2
    - numpy
    - simple_lama_inpainting
    - torch
    - local: config
Execution:
    python scripts/05A_pretratamento.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Not re-executed in the v1.0.0 verification. Environment of the verification: Python 3.9.6
    (macOS) with the versions listed in requirements.txt.
Warnings:
    LaMa weights are downloaded at run time by simple_lama_inpainting; their version and licence are
    not archived here.
"""
# Original module notes (Portuguese) are preserved below.
"""
Fase 05A — Pré-tratamento das imagens: remoção do flash / glare especular por
inpainting de Deep Learning (LaMa).

Etapa de PRÉ-PROCESSAMENTO, ANTES de qualquer método. A partir daqui, TODOS os
métodos usam AS MESMAS imagens tratadas:
  - Fase 07 (Frangi, clássico, local)
  - Fase 06C (modelo externo PRMI)
Comparar métodos exige que as imagens de entrada sejam idênticas.

Princípio (melhor visual SEM perder a ciência):
  * Só se aciona onde há NÚCLEO ESPECULAR GENUÍNO (quase-branco estourado,
    V >= DEFLASH_SEED_V) — raízes/solo brilhantes NÃO chegam a esse brilho e não
    viram semente. Evita apagar/fabricar raiz em imagem de baixo glare.
  * A partir do núcleo, cresce pelo "halo lavado" (glareness = excesso de brilho OU
    déficit de saturação vs. fundo de larga escala), CONFINADO a um disco ao redor do
    núcleo (impede disparar por raiz/solo) e fechado em FECHO CONVEXO (região compacta).
  * Raiz que cruza o glare é reconstruída pela LaMa (o sinal real ali já está perdido).
  * O halo difuso remanescente fica para o flat-field da Fase 07.
  * CIÊNCIA: a máscara é salva (auditoria) e a área inpintada (flash_pct) é registrada
    para ser EXCLUÍDA das estatísticas quantitativas de densidade radicular.

Método:
  1. fmask(): semente = núcleo especular saturado -> cresce pelo halo (glareness) dentro
     de um disco-limite -> fecho convexo -> dilatação de borda.
  2. deflash(): reduz a imagem (DEFLASH_MAX_SIDE) para rodar a LaMa na CPU sem OOM,
     roda o inpainting, volta a resolução cheia e recompõe SÓ a região do glare
     (mistura suave nas bordas) sobre a imagem original em resolução plena.

Entrada: saidas/05_registradas/<data>/R##_<data>.png   (registradas, com flash)
Saída:   saidas/05A_tratadas/<data>/R##_<data>.png       (tratadas, sem flash)
         saidas/05A_tratadas/_mascaras/<data>/R##_<data>.png   (máscara do glare, auditoria)
         saidas/05A_tratadas/_previas/<image_id>_ANTES_DEPOIS.png  (algumas prévias)
         metricas/pretratamento_05A.csv
"""
import os
import sys
import csv
import time

import numpy as np
import cv2

# LaMa (simple-lama-inpainting) foi serializada com backend CUDA; forçamos CPU no load.
import torch
_orig_jit_load = torch.jit.load
torch.jit.load = lambda f, *a, **k: _orig_jit_load(f, map_location="cpu")
from PIL import Image
from simple_lama_inpainting import SimpleLama

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

IN = C.SAIDAS / "05_registradas"
OUT = C.SAIDAS / "05A_tratadas"
MASKS = OUT / "_mascaras"
PREVIEWS = OUT / "_previas"
LOG = C.METRICAS / "pretratamento_05A.csv"

# imagens usadas nas prévias ANTES/DEPOIS (as 2 que o pesquisador inspecionou)
PREVIEW_IDS = {"R08_14_06_2025", "R02_05_07_2025"}

_lama = None
def _get_lama():
    global _lama
    if _lama is None:
        _lama = SimpleLama(device=torch.device("cpu"))
    return _lama


def fmask(bgr):
    """Máscara do glare (núcleo especular + halo saturado), confinada e auditável.
    Retorna (mask_uint8, n_nucleos)."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    S = hsv[:, :, 1] / 255.0
    V = hsv[:, :, 2] / 255.0
    Sbg = cv2.GaussianBlur(S, (0, 0), C.DEFLASH_BG_SIGMA)
    Vbg = cv2.GaussianBlur(V, (0, 0), C.DEFLASH_BG_SIGMA)
    excess = np.clip((V - Vbg) / 0.15, 0, 1)          # mais claro que o fundo
    deficit = np.clip((Sbg - S) / 0.20, 0, 1)         # mais "lavado" que o fundo
    glare = np.maximum(excess, deficit)
    cand = ((glare > C.DEFLASH_GLARE_THR) & (V > Vbg - 0.03)).astype(np.uint8)

    # sementes = núcleos especulares saturados (quase-brancos)
    seed = ((V >= C.DEFLASH_SEED_V) & (S <= C.DEFLASH_SEED_S)).astype(np.uint8)
    seed = cv2.morphologyEx(seed, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    ns, ls, sts, cents = cv2.connectedComponentsWithStats(seed)
    seed_ok = np.zeros_like(seed)
    centers = []
    for i in range(1, ns):
        if sts[i, cv2.CC_STAT_AREA] >= C.DEFLASH_SEED_AREA:
            seed_ok[ls == i] = 1
            r0 = np.sqrt(sts[i, cv2.CC_STAT_AREA] / np.pi)
            R = max(200, min(C.DEFLASH_DISC_CAP, C.DEFLASH_DISC_K * r0))
            centers.append((cents[i], R))
    if not centers:
        return np.zeros(V.shape, np.uint8), 0

    # disco-limite ao redor de cada núcleo (impede crescimento disparar)
    H, W = V.shape
    disc = np.zeros((H, W), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    for (cx, cy), R in centers:
        disc[(xx - cx) ** 2 + (yy - cy) ** 2 <= R * R] = 1
    cand = cand & disc

    # crescimento geodésico da semente dentro do candidato (já confinado ao disco)
    m = (seed_ok & cand).astype(np.uint8)
    if not m.any():
        m = (seed_ok & disc).astype(np.uint8)
    k3 = np.ones((3, 3), np.uint8)
    for _ in range(900):
        d = cv2.dilate(m, k3) & cand
        if np.array_equal(d, m):
            break
        m = d

    # fecho convexo por blob -> região compacta cobrindo núcleo+halo
    out = np.zeros_like(m)
    n2, l2, st2, _ = cv2.connectedComponentsWithStats(m)
    for i in range(1, n2):
        if st2[i, cv2.CC_STAT_AREA] < C.DEFLASH_HULL_AREA:
            continue
        pts = np.column_stack(np.where(l2 == i))[:, ::-1]   # (x, y)
        cv2.fillConvexPoly(out, cv2.convexHull(pts), 1)
    if not out.any():
        return np.zeros(V.shape, np.uint8), 0
    k = np.ones((C.DEFLASH_FINAL_DILATE, C.DEFLASH_FINAL_DILATE), np.uint8)
    return (cv2.dilate(out, k) * 255).astype(np.uint8), len(centers)


def deflash(bgr):
    """Remove o glare por inpainting LaMa (downscale -> LaMa -> recompõe em full-res).
    Retorna (tratada_bgr, mask_uint8, flash_pct, n_blobs)."""
    H, W = bgr.shape[:2]
    mask, n_blobs = fmask(bgr)
    if not mask.any():
        return bgr, mask, 0.0, 0
    sc = C.DEFLASH_MAX_SIDE / max(H, W)
    small = cv2.resize(bgr, (int(W * sc), int(H * sc)))
    msmall = cv2.resize(mask, (int(W * sc), int(H * sc)), interpolation=cv2.INTER_NEAREST)
    res = _get_lama()(Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB)),
                      Image.fromarray(msmall))
    filled = cv2.resize(cv2.cvtColor(np.array(res), cv2.COLOR_RGB2BGR), (W, H))
    alpha = cv2.GaussianBlur((mask > 0).astype(np.float32), (0, 0), C.DEFLASH_BLEND_SIGMA)[..., None]
    out = (bgr * (1 - alpha) + filled * alpha).astype(np.uint8)
    return out, mask, 100.0 * mask.mean() / 255.0, n_blobs


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
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    imgs = sorted(IN.rglob("*.png"))
    if limite:
        imgs = imgs[:limite]
    if not imgs:
        print("[05A] Nenhuma imagem em saidas/05_registradas (rode a Fase 05).")
        return

    rows = []
    for k, p in enumerate(imgs, 1):
        rel = p.relative_to(IN)
        bgr = cv2.imread(str(p))
        t = time.time()
        out, mask, pct, n_blobs = deflash(bgr)
        dt = time.time() - t

        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(dst), out)
        mdst = MASKS / rel
        mdst.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(mdst), mask)

        if p.stem in PREVIEW_IDS:
            def sm(x):
                return cv2.resize(x, (x.shape[1] // 4, x.shape[0] // 4))
            panel = np.hstack([sm(bgr), sm(out)])
            cv2.imwrite(str(PREVIEWS / f"{p.stem}_ANTES_DEPOIS.png"), panel)

        rows.append({
            "image_id": p.stem,
            "data": rel.parts[0] if len(rel.parts) > 1 else "",
            "pct_inpintado": round(pct, 3),   # área reconstruída — EXCLUIR das densidades
            "n_nucleos_glare": n_blobs,
            "tempo_s": round(dt, 1),
            "tratada": str(dst.relative_to(C.ROOT)),
            "mascara": str(mdst.relative_to(C.ROOT)),
        })
        print(f"  [{k:2d}/{len(imgs)}] {rel}  inpint={pct:5.2f}%  nucleos={n_blobs}  ({dt:.1f}s)")

    with open(LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    com_glare = [r for r in rows if r["pct_inpintado"] > 0]
    print(f"\n[05A] {len(rows)} imagens tratadas (LaMa) -> {OUT.relative_to(C.ROOT)}/")
    print(f"   com glare detectado: {len(com_glare)}/{len(rows)}  "
          f"(área inpintada média nelas: {np.mean([r['pct_inpintado'] for r in com_glare]) if com_glare else 0:.2f}%)")
    print(f"   máscaras (auditoria): {MASKS.relative_to(C.ROOT)}/")
    print(f"   log: {LOG.relative_to(C.ROOT)}")


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(lim)
