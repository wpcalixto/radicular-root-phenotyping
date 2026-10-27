#!/usr/bin/env python3
"""
Title:
    Geometric registration and centred cropping
File type:
    Script
Purpose:
    Crops every converted image around its centre with radii bounded by the smallest image in the
    set, producing registered images of identical size, and logs the registration parameters.
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
    - saidas/03_convertidas
Outputs:
    - metricas/image_registration_log.csv
    - saidas/05_registradas
    - saidas/05_registradas/<data>/R##.png
Dependencies:
    - PIL
    - local: config
Execution:
    python scripts/05_registro_calibracao.py (from a workspace prepared with
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
Fase 05 — Registro geométrico, recorte centrado e calibração espacial.

Recorte por RAIO a partir do centro (método robusto):
  1. Referência = MENOR imagem do conjunto (min_W × min_H).
  2. Raio horizontal r_x e vertical r_y definidos a partir do centro, limitados
     pela menor imagem menos uma margem mínima:
        r_x = min_W//2 - margem_x ;  r_y = min_H//2 - margem_y
  3. Cada imagem é recortada como [c_x±r_x] × [c_y±r_y] em torno do SEU centro.
  Como r_x e r_y são iguais para todas e cabem na menor, TODAS ficam do MESMO
  tamanho (2r_x × 2r_y) e centradas no mesmo ponto — nenhuma extrapola a imagem.

Orientação semântica: retrato (profundidade = y, topo = superfície do solo), θ_sem=0.
SEM calibração métrica: o enquadramento não tem borda do rizotron nem fiducial, logo
não há escala px->cm confiável (exigiria s_x=s_y, e 60/W_px != 80/H_px). Todos os
descritores (Fase 09) são reportados em pixels / proporção / profundidade normalizada.

Saídas: saidas/05_registradas/<data>/R##.png ; metricas/image_registration_log.csv
"""
import os
import sys
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from PIL import Image

IMG_IN = C.SAIDAS / "03_convertidas"
IMG_OUT = C.SAIDAS / "05_registradas"
OUT_CSV = C.METRICAS / "image_registration_log.csv"


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
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    imgs = sorted(IMG_IN.rglob("*.png"))
    if not imgs:
        print("[Fase 05] Nenhuma imagem convertida (rode a Fase 03)."); return

    # --- Passo 1: dimensões de todas (referência = menor) ---
    dims = {p: Image.open(p).size for p in imgs}       # (W, H)
    min_W = min(w for w, h in dims.values())
    min_H = min(h for w, h in dims.values())

    # --- Passo 2: raios a partir do centro (margem mínima na referência) ---
    margem_x = round(C.CROP_MARGIN_FRAC * min_W)
    margem_y = round(C.CROP_MARGIN_FRAC * min_H)
    r_x = min_W // 2 - margem_x
    r_y = min_H // 2 - margem_y
    W_px, H_px = 2 * r_x, 2 * r_y

    # --- SEM calibração métrica: unidades = pixels (ver docstring/config) ---

    # --- Passo 3: recorta cada imagem em torno do SEU centro ---
    regs = []
    for p in imgs:
        rel = p.relative_to(IMG_IN)
        reg = {"image_id": p.stem, "raw_path": str(p.relative_to(C.ROOT)),
               "registration_status": "erro"}
        try:
            W, H = dims[p]
            cx, cy = W // 2, H // 2
            box = (cx - r_x, cy - r_y, cx + r_x, cy + r_y)
            dst = IMG_OUT / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            Image.open(p).crop(box).save(dst, format="PNG", compress_level=6)
            reg.update({
                "converted_path": str(dst.relative_to(C.ROOT)),
                "semantic_orientation": "retrato", "depth_axis": "y",
                "top_is_soil_surface": int(C.TOP_IS_SURFACE), "theta_sem": 0,
                "center_x": cx, "center_y": cy, "r_x": r_x, "r_y": r_y,
                "x0": box[0], "y0": box[1], "x1": box[2], "y1": box[3],
                "W_px": W_px, "H_px": H_px,
                "ref_min_W": min_W, "ref_min_H": min_H,
                "unidade": "pixel", "calibracao_metrica": "ausente_sem_fiducial",
                "registration_status": "ok",
            })
        except Exception as e:
            reg["registration_status"] = f"erro: {e}"
        regs.append(reg)

    campos = ["image_id", "raw_path", "converted_path", "semantic_orientation",
              "depth_axis", "top_is_soil_surface", "theta_sem",
              "center_x", "center_y", "r_x", "r_y", "x0", "y0", "x1", "y1",
              "W_px", "H_px", "ref_min_W", "ref_min_H",
              "unidade", "calibracao_metrica",
              "registration_status"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader(); w.writerows(regs)

    ok = sum(1 for r in regs if r["registration_status"] == "ok")
    print(f"[Fase 05] Registro + recorte (raio do centro): {ok}/{len(regs)} OK")
    print(f"   Referência (menor imagem): {min_W} x {min_H} px")
    print(f"   Raios: r_x={r_x}, r_y={r_y} (margem {C.CROP_MARGIN_FRAC:.0%}) -> saída {W_px} x {H_px} px (uniforme)")
    print(f"   Unidade: PIXEL (sem calibração métrica — sem fiducial no enquadramento)")
    print(f"   Imagens: {IMG_OUT.relative_to(C.ROOT)}/  |  Log: {OUT_CSV.relative_to(C.ROOT)}")
    for r in regs:
        if r["registration_status"] != "ok":
            print(f"   [FALHA] {r['raw_path']}: {r['registration_status']}")


if __name__ == "__main__":
    main()
