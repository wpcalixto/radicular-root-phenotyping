#!/usr/bin/env python3
"""
Title:
    Blinded assessment package (M3 final)
File type:
    Script
Purpose:
    Generates anonymised overlays of M1, M2 and final M3 on each conditioned image with a fixed-seed
    random code assignment, the answer key and the score sheet used by the assessors.
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
    - saidas/05A_tratadas
    - saidas/06C_inferencia/masks
    - saidas/07_frangi/masks
    - saidas/08_combinado_limpo/masks
Outputs:
    - metricas/review_image_set.csv
    - metricas/review_key.csv
    - metricas/review_score_sheet.csv
    - saidas/08_avaliacao/review_package
    - saidas/08_avaliacao/review_package/<image_id>__<codigo>.png
Dependencies:
    - numpy
    - skimage
    - local: config
Execution:
    python scripts/08B_pacote_cego.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Not re-executed in the v1.0.0 verification. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    Contains instructions referring to Google Drive/Colab/rclone storage used during the original
    execution; these are historical and optional.
"""
# Original module notes (Portuguese) are preserved below.
"""
Fase 08 (08B + 08C) — Pacote de avaliação cego + planilha de notas dos especialistas.

Compara as máscaras candidatas de cada imagem (3 métodos):
  - M^Frangi  (Fase 07, local)      -> saidas/07_frangi/masks/<data>/R##.png
  - M^Ext     (Fase 06C, modelo PRMI) -> saidas/06C_inferencia/masks/<data>/R##.png
  - M^Comb    (Frangi ∪ Ext)        -> saidas/08_combinado/masks/<data>/R##.png
sobre a imagem tratada (Fase 05A).

08B: gera overlays com CÓDIGOS ANÔNIMOS por imagem (metodo_A/B/C embaralhados),
     para o especialista não saber qual método é qual (avaliação cega).
08C: gera a planilha de notas em branco (uma linha por imagem×método) + o gabarito.

NÃO faz 08A (diagnóstico externo — sai do 06B) nem 08D (seleção — após os especialistas
preencherem as notas).

Saídas:
  saidas/08_avaliacao/review_package/<image_id>__<codigo>.png   (overlay verde)
  metricas/review_score_sheet.csv    (planilha para os especialistas preencherem)
  metricas/review_key.csv            (gabarito codigo->metodo; NÃO mostrar aos avaliadores)
  metricas/review_image_set.csv      (índice das imagens do pacote)
"""
import os
import sys
import csv
import random
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from skimage import io, img_as_float, img_as_ubyte

IMG_DIR = C.SAIDAS / "05A_tratadas"                   # imagem base (tratada, sem flash)
FRANGI_DIR = C.SAIDAS / "07_frangi" / "masks"         # M^Frangi
EXT_MASKS_DIR = C.SAIDAS / "06C_inferencia" / "masks" # M^Ext (baixar do Drive p/ cá)
COMB_DIR = C.SAIDAS / "08_combinado_limpo" / "masks"  # M3 final = R(Frangi) ∪ Ext (refinamento antes da combinação)
OUT = C.SAIDAS / "08_avaliacao" / "review_package"
SEED = 42
LETRAS = ["A", "B", "C", "D"]                          # códigos anônimos por método

# Planilha "marque x": o avaliador só põe um 'x' na caixa apropriada.
#   - qualidade: marca UMA das 5 notas (nota_0..nota_4)
#   - aceita: marca se aceitaria a máscara para medir
#   - problema principal: marca se houver (pode marcar mais de um)
CRITERIOS = ["nota_0_rejeita", "nota_1_ruim", "nota_2_regular", "nota_3_boa", "nota_4_muito_boa",
             "aceita", "prob_falta_raiz", "prob_excesso_solo", "prob_glare", "prob_fragmentado",
             "observacoes"]


def overlay(rgb, mask, cor=(0, 255, 0)):
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
    ov = (rgb * 255).astype(np.uint8).copy()
    ov[mask.astype(bool)] = cor
    return ov


def carregar_mask(path):
    """
    Purpose:
        Read a mask image as boolean.
    Parameters:
        path: mask image
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    m = io.imread(path, as_gray=True)
    return (m > 0.5)


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
    random.seed(SEED)
    C.METRICAS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    if not EXT_MASKS_DIR.exists():
        print(f"[Fase 08] M^Ext ainda não disponível em {EXT_MASKS_DIR.relative_to(C.ROOT)}")
        print("  -> rode o 06C no Colab e baixe as máscaras do Drive:")
        print('     rclone copy "pacheco:Sistema_Radicular/Dataset_PRMI/06C_inferencia/masks" '
              f'"{EXT_MASKS_DIR}"')
        return

    imgs = sorted(p for p in IMG_DIR.rglob("*.png")
                  if not any(part.startswith("_") for part in p.relative_to(IMG_DIR).parts))
    key_rows, sheet_rows, set_rows = [], [], []
    METODOS = {"Frangi": FRANGI_DIR, "Ext": EXT_MASKS_DIR, "Comb": COMB_DIR}

    n_ok = 0
    for p in imgs:
        rel = p.relative_to(IMG_DIR)
        iid = p.stem
        masks = {}
        for m, d in METODOS.items():
            mp = d / rel
            if mp.exists():
                masks[m] = mp
        if len(masks) < len(METODOS):
            print(f"  [pula] {iid}: faltam máscaras ({list(masks)})"); continue

        rgb = img_as_float(io.imread(p))[:, :, :3]
        # embaralha os códigos por imagem (cego)
        metodos = list(masks.keys()); random.shuffle(metodos)
        codigos = dict(zip(metodos, LETRAS[:len(metodos)]))
        for metodo, cod in codigos.items():
            ov = overlay(rgb, carregar_mask(masks[metodo]))
            nome = f"{iid}__metodo_{cod}.png"
            io.imsave(OUT / nome, img_as_ubyte(ov), check_contrast=False)
            key_rows.append({"image_id": iid, "data": rel.parts[0], "codigo": f"metodo_{cod}",
                             "metodo_real": metodo, "overlay": nome})
            row = {"image_id": iid, "data": rel.parts[0], "codigo": f"metodo_{cod}",
                   "prancha": f"{iid}.jpg", "avaliador": ""}
            row.update({c: "" for c in CRITERIOS})
            sheet_rows.append(row)
        set_rows.append({"image_id": iid, "data": rel.parts[0],
                         "imagem_base": str(p.relative_to(C.ROOT))})
        n_ok += 1

    # planilha de notas (em branco), gabarito e índice
    with open(C.METRICAS / "review_score_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image_id", "data", "codigo", "prancha", "avaliador"] + CRITERIOS)
        w.writeheader(); w.writerows(sheet_rows)
    with open(C.METRICAS / "review_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image_id", "data", "codigo", "metodo_real", "overlay"])
        w.writeheader(); w.writerows(key_rows)
    with open(C.METRICAS / "review_image_set.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image_id", "data", "imagem_base"])
        w.writeheader(); w.writerows(set_rows)

    print(f"[Fase 08] Pacote cego: {n_ok} imagens × {len(METODOS)} métodos = {len(key_rows)} overlays")
    print(f"   Overlays: {OUT.relative_to(C.ROOT)}/")
    print(f"   Planilha (especialistas preenchem): metricas/review_score_sheet.csv")
    print(f"   Gabarito (NÃO mostrar): metricas/review_key.csv")
    print("   Escala Q: 0=rejeitada 1=muito ruim 2=regular 3=boa 4=muito boa")


if __name__ == "__main__":
    main()
