#!/usr/bin/env python3
"""
Title:
    External PRMI dataset indexing
File type:
    Script
Purpose:
    Records the source, integrity (MD5) and licence of the external PRMI archive and rebuilds the
    image-mask-species-split index and the split file from the archive listing.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-06
Date:
    2026-07-06
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
    - manifestos/external_dataset_index.csv
    - manifestos/external_split.csv
Outputs:
    - external_dataset_license.txt
    - manifestos/prmi_ziplist.txt
Dependencies:
    - local: config
Execution:
    python scripts/06A_dataset_externo.py (from a workspace prepared with
    tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Not re-executed in the v1.0.0 verification. Environment of the verification: Python 3.9.6
    (macOS) with the versions listed in requirements.txt.
Warnings:
    Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not
    redistributed in these packages. Contains instructions referring to Google Drive/Colab/rclone
    storage used during the original execution; these are historical and optional.
"""
# Original module notes (Portuguese) are preserved below.
"""
Fase 06A — Seleção, download e organização do dataset externo (PRMI).

Reprodutível e auditável. O zip (9,75 GB) fica no Google Drive; NÃO trafega ao
local. Este script:
  1. Registra fonte, integridade (md5) e licença -> external_dataset_license.txt
  2. (Re)constrói os índices a partir da listagem do zip (`unzip -Z1`), gerando
     external_dataset_index.csv (imagem<->máscara<->espécie<->split<->has_mask) e
     external_split.csv (contagem por split x espécie).

Como obter a listagem (sem baixar tudo de novo, na nuvem/onde o zip estiver):
    unzip -Z1 PRMI_official.zip > manifestos/prmi_ziplist.txt

Saídas: manifestos/external_dataset_{index,split}.csv, external_dataset_license.txt
"""
import os
import sys
import csv
import re
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

# --- Metadados do dataset externo (Fase 06A) ---
PRMI = {
    "nome": "PRMI — Plant Root Minirhizotron Imagery",
    "fonte_zenodo": "https://zenodo.org/records/5974905",
    "espelho_dryad_doi": "10.5061/dryad.2v6wwpzp4",
    "arquivo": "PRMI_official.zip",
    "bytes": 9748189339,
    "md5": "659fc0fc1bcba81112cf7a0ca0ff52d0",
    "licenca": "CC0 1.0 Universal (Domínio Público)",
    "drive": "Meu Drive/Sistema_Radicular/Dataset_PRMI/",
    "citacao": ('W. Xu, G. Yu, Y. Cui, R. Gloaguen, A. Zare et al., '
                '"PRMI: A Dataset of Minirhizotron Images for Diverse Plant Root '
                'Study", AIAFS Workshops, AAAI, Feb 2022.'),
    "download": ("aria2c -x16 -s16 "
                 "https://zenodo.org/api/records/5974905/files/PRMI_official.zip/content "
                 "-o PRMI_official.zip  ;  rclone copyto PRMI_official.zip "
                 "pacheco:Sistema_Radicular/Dataset_PRMI/PRMI_official.zip"),
}

LIC = C.MANIFESTOS / "external_dataset_license.txt"
IDX = C.MANIFESTOS / "external_dataset_index.csv"
SPLIT = C.MANIFESTOS / "external_split.csv"
ZIPLIST = C.MANIFESTOS / "prmi_ziplist.txt"


def escrever_licenca():
    """
    Purpose:
        Write the PRMI source, integrity and licence record.
    Parameters:
        none
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    C.MANIFESTOS.mkdir(parents=True, exist_ok=True)
    with open(LIC, "w", encoding="utf-8") as f:
        f.write("Registro de licença do dataset externo — Fase 06A\n")
        f.write("=" * 52 + "\n")
        for k in ("nome", "fonte_zenodo", "espelho_dryad_doi", "arquivo",
                  "bytes", "md5", "licenca", "drive"):
            f.write(f"{k:20s}: {PRMI[k]}\n")
        f.write(f"\nLicença: {PRMI['licenca']} — uso/modificação/redistribuição livres, "
                "sem exigência de atribuição (citação recomendada).\n")
        f.write("Verificado em: 2026-07-06 (metadado Zenodo: license id = cc-zero).\n")
        f.write(f"\nComando de download:\n  {PRMI['download']}\n")
        f.write(f"\nCitação recomendada:\n  {PRMI['citacao']}\n")
    print(f"[06A] licença registrada -> {LIC.relative_to(C.ROOT)}")


def construir_indice(listagem_path):
    """
    Purpose:
        Rebuild the image-mask-species-split index from the archive listing.
    Parameters:
        listagem_path: text file with the archive listing
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    lines = [l.strip() for l in open(listagem_path, encoding="utf-8")
             if l.strip() and not l.endswith("/")]
    masks = set(l for l in lines if "/masks_pixel_gt/" in l)
    IMG_EXT = (".jpg", ".jpeg", ".png")
    rows = []
    for l in lines:
        if "/images/" not in l or not l.lower().endswith(IMG_EXT):
            continue
        p = l.split("/")
        i = p.index("images")
        split, species, base = p[i - 1], p[i + 1], os.path.splitext(p[-1])[0]
        mask = "/".join(p[:i]) + f"/masks_pixel_gt/{species}/GT_{base}.png"
        has = 1 if mask in masks else 0
        rows.append({"split": split, "species": species, "image_path": l,
                     "mask_path": mask if has else "", "has_mask": has})
    with open(IDX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["split", "species", "image_path", "mask_path", "has_mask"])
        w.writeheader(); w.writerows(rows)
    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        agg[(r["split"], r["species"])][0] += 1
        agg[(r["split"], r["species"])][1] += r["has_mask"]
    with open(SPLIT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["split", "species", "n_images", "n_with_mask"])
        for (s, sp), (n, m) in sorted(agg.items()):
            w.writerow([s, sp, n, m])
    tot_m = sum(r["has_mask"] for r in rows)
    print(f"[06A] índice reconstruído: {len(rows)} imagens, {tot_m} com máscara "
          f"-> {IDX.relative_to(C.ROOT)}, {SPLIT.relative_to(C.ROOT)}")


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
    escrever_licenca()
    if ZIPLIST.exists():
        construir_indice(ZIPLIST)
    elif IDX.exists():
        print(f"[06A] índices já existem ({IDX.relative_to(C.ROOT)}). "
              "Para reconstruir: gere manifestos/prmi_ziplist.txt (unzip -Z1) e rode de novo.")
    else:
        print("[06A] índices ausentes. Gere manifestos/prmi_ziplist.txt (unzip -Z1 do zip) e rode de novo.")


if __name__ == "__main__":
    main()
