#!/usr/bin/env python3
"""
Title:
    Master dataset manifest
File type:
    Script
Purpose:
    Builds the master manifest with one row per rhizotron (R01-R12) and collection, linking each
    observation to treatment, replicate, date, DAP, image path and electrical files, with image,
    electrical and joint availability flags.
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
    - none detected by static analysis
Outputs:
    - manifestos/dataset_manifest.csv
Dependencies:
    - local: config
Execution:
    python scripts/01_manifesto.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 01 — Manifesto mestre do dataset.

Uma linha por rizotron (R01..R12) × coleta (1..K). Vincula cada observação
temporal à unidade biológica e às fontes multimodais (imagem, elétricas, alvo).

Disponibilidade: I (imagem), E (elétrica), completude C = I·E.

Saída: manifestos/dataset_manifest.csv
Colunas: rhizotron_id, treatment_id, replicate_id, collection_id, collection_date,
         DAP, image_path, conductivity_file, resistance_file, resistivity_file,
         target_file, I_img, E_elec, C_completude, source, quality_flag
"""
import os
import sys
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

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
    linhas = []

    for k, pasta in enumerate(C.COLETAS, start=1):
        data = C.parse_data_pasta(pasta)
        dap_k = C.dap(data)
        elet = C.arquivos_eletricos(pasta)
        # elétrica disponível se os 3 arquivos existem em tabdatas/
        elet_ok = all((C.TABDATAS / elet[key]).exists() for key in elet)
        target_ok = (C.TABDATAS / C.TARGET_FILE).exists()

        for riz in C.RIZOTRONS:
            tcod, _ = C.tratamento(riz)
            img_nome = f"{riz}_{pasta}.heic"
            img_path = C.ENTRADAS / pasta / img_nome
            I = 1 if img_path.exists() else 0
            E = 1 if elet_ok else 0
            linhas.append({
                "rhizotron_id": riz,
                "treatment_id": tcod,
                "replicate_id": C.replicata(riz),
                "collection_id": k,
                "collection_date": data.isoformat(),
                "DAP": dap_k,
                "image_path": str(img_path.relative_to(C.ROOT)) if I else "",
                "conductivity_file": elet["conductivity_file"] if elet_ok else "",
                "resistance_file": elet["resistance_file"] if elet_ok else "",
                "resistivity_file": elet["resistivity_file"] if elet_ok else "",
                "target_file": C.TARGET_FILE if target_ok else "",
                "I_img": I,
                "E_elec": E,
                "C_completude": I * E,
                "source": "UFG_Ademir",
                "quality_flag": "pendente",   # preenchido na Fase 04
            })

    out = C.MANIFESTOS / "dataset_manifest.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    # Resumo de completude
    n = len(linhas)
    n_img = sum(r["I_img"] for r in linhas)
    n_elec = sum(r["E_elec"] for r in linhas)
    n_comp = sum(r["C_completude"] for r in linhas)
    print(f"[Fase 01] Manifesto: {n} observações (12 rizotrons × {len(C.COLETAS)} coletas)")
    print(f"          -> {out.relative_to(C.ROOT)}")
    print(f"   Imagens disponíveis (I=1):    {n_img}/{n}")
    print(f"   Elétrica disponível (E=1):    {n_elec}/{n}")
    print(f"   Completude multimodal (C=1):  {n_comp}/{n}")
    faltantes = [(r['rhizotron_id'], r['collection_date']) for r in linhas if r['I_img'] == 0]
    if faltantes:
        print("   Imagens ausentes:", ", ".join(f"{a}@{b}" for a, b in faltantes))

if __name__ == "__main__":
    main()
