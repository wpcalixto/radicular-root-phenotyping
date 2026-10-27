#!/usr/bin/env python3
"""
Title:
    HEIC to PNG conversion
File type:
    Script
Purpose:
    Converts the in situ HEIC images to lossless PNG at full resolution, applying the EXIF
    orientation and logging the original orientation for audit.
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
    - entradas/<data_coleta>/R##_<data>.heic
Outputs:
    - manifestos/03_conversao.csv
    - saidas/03_convertidas
    - saidas/03_convertidas/<data>/R##_<data>.png
Dependencies:
    - PIL
    - pillow_heif
    - local: config
Execution:
    python scripts/03_conversao_heic.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 03 — Conversão .heic -> .png respeitando a orientação EXIF.

- Converte sem recompressão com perda (PNG lossless), preservando resolução.
- Lê e APLICA a orientação EXIF (ImageOps.exif_transpose); registra a original.
- NÃO define ainda a orientação semântica da raiz (isso é da Fase 05).
- Documenta tudo em CSV para auditoria.

Entrada:  entradas/<data_coleta>/R##_<data>.heic  (série in-situ dos rizotrons)
Saídas:   saidas/03_convertidas/<data>/R##_<data>.png
          manifestos/03_conversao.csv  (tabela de conversão)
"""
import os
import sys
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

from PIL import Image, ImageOps
import pillow_heif
pillow_heif.register_heif_opener()

SAIDA_IMG = C.SAIDAS / "03_convertidas"
LOG_CSV = C.MANIFESTOS / "03_conversao.csv"

EXIF_ORIENTATION = 0x0112
# ângulo nominal implícito pela orientação EXIF (para registro; a rotação real
# é aplicada por exif_transpose, que também trata espelhamentos)
THETA_EXIF = {1: 0, 2: 0, 3: 180, 4: 180, 5: 90, 6: 90, 7: 270, 8: 270}


def coletar_heic():
    """.heic da série in-situ dos rizotrons (pastas de data de coleta)."""
    itens = []
    for pasta in C.COLETAS:
        d = C.ENTRADAS / pasta
        if d.is_dir():
            for p in sorted(d.glob("*.heic")):
                itens.append(p)
    return itens


def processar(src):
    """
    Purpose:
        Convert one HEIC image to PNG applying the EXIF orientation and return its log record.
    Parameters:
        src: path of the HEIC image
    Returns:
        dict log record
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rel = src.relative_to(C.ENTRADAS)
    reg = {
        "image_id": src.stem,
        "raw_path": str(src.relative_to(C.ROOT)),
        "converted_path": "",
        "original_width_px": "", "original_height_px": "",
        "exif_orientation": "", "theta_EXIF": "", "espelhado_exif": "",
        "converted_width_px": "", "converted_height_px": "",
        "orientation_flag": "", "conversion_status": "erro",
    }
    try:
        img = Image.open(src)
        orient = img.getexif().get(EXIF_ORIENTATION, "")
        ow, oh = img.size
        img2 = ImageOps.exif_transpose(img)          # aplica orientação EXIF
        cw, ch = img2.size
        flag = "paisagem" if cw > ch else ("retrato" if ch > cw else "quadrada")

        dst = SAIDA_IMG / rel.with_suffix(".png")
        dst.parent.mkdir(parents=True, exist_ok=True)
        img2.convert("RGB").save(dst, format="PNG", compress_level=6)

        reg.update({
            "converted_path": str(dst.relative_to(C.ROOT)),
            "original_width_px": ow, "original_height_px": oh,
            "exif_orientation": orient,
            "theta_EXIF": THETA_EXIF.get(orient, 0) if orient else 0,
            # orientações EXIF 2,4,5,7 incluem espelhamento (o transpose já aplica corretamente;
            # aqui só documentamos, pois theta_EXIF sozinho não representa o flip)
            "espelhado_exif": 1 if orient in (2, 4, 5, 7) else 0,
            "converted_width_px": cw, "converted_height_px": ch,
            "orientation_flag": flag, "conversion_status": "ok",
        })
    except Exception as e:
        reg["conversion_status"] = f"erro: {e}"
    return reg


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
    C.MANIFESTOS.mkdir(parents=True, exist_ok=True)
    SAIDA_IMG.mkdir(parents=True, exist_ok=True)

    heics = coletar_heic()
    if not heics:
        print("[Fase 03] Nenhum .heic encontrado nas pastas de coleta."); return

    regs = [processar(p) for p in heics]

    with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(regs[0].keys()))
        w.writeheader(); w.writerows(regs)

    ok = sum(1 for r in regs if r["conversion_status"] == "ok")
    from collections import Counter
    flags = Counter(r["orientation_flag"] for r in regs if r["conversion_status"] == "ok")
    print(f"[Fase 03] Conversão .heic -> .png : {ok}/{len(regs)} OK")
    print(f"   Imagens em: {SAIDA_IMG.relative_to(C.ROOT)}/")
    print(f"   Log CSV   : {LOG_CSV.relative_to(C.ROOT)}")
    print(f"   Orientação (após EXIF): " +
          ", ".join(f"{k}={v}" for k, v in flags.items()))
    falhas = [r for r in regs if r["conversion_status"] != "ok"]
    for r in falhas:
        print(f"   [FALHA] {r['raw_path']}: {r['conversion_status']}")


if __name__ == "__main__":
    main()
