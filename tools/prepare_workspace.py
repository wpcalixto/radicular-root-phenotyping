#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    Workspace preparation for the Radicular pipeline
File type:
    Script (distribution helper added in v1.0.0; not part of the historical pipeline)
Purpose:
    Build, by physical copy, the directory tree expected by scripts/config.py
    (ROOT/entradas, ROOT/tabdatas, ROOT/config, ROOT/saidas, ROOT/metricas,
    ROOT/modelos, ROOT/scripts) from the Radicular Dataset and Software packages.
    The Dataset and Software directories are only read; nothing is written to them.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0
Date:
    2026-10-26
Developer:
    Prof. Wesley Pacheco Calixto
Authors:
    Wesley Pacheco Calixto; Universidade de Coimbra (UC), Portugal;
    Universidade Federal de Goiás (UFG), Brazil; Instituto Federal de Educação,
    Ciência e Tecnologia de Goiás (IFG), Brazil
Corresponding author:
    Wesley Pacheco Calixto
License:
    MIT (see LICENSE)
Citation:
    If you use this code, please cite the Radicular Software record
    (Zenodo DOI 10.5281/zenodo.23679263) and the associated article.
Related publication:
    Auditable longitudinal root phenotyping in rhizotrons using Frangi--U-Net
    fusion and apparent conductivity (manuscript in preparation for submission to Royal Society Open Science)
Inputs:
    - --dataset: path to Dataset_Radicular_v1.0.0
    - --software: path to Software_Radicular_v1.0.0
    - --parts: comma-separated subset of {raw,processed,masks,assessment,tabular,metrics,metadata,models}
      (default: all parts)
Outputs:
    - --workspace: new directory with the tree expected by scripts/config.py
Dependencies:
    - Python >= 3.9 standard library only
Execution:
    python tools/prepare_workspace.py --dataset ../Dataset_Radicular_v1.0.0 --software . --workspace ../ws --parts metrics,tabular,assessment
Portability notes:
    All paths are given on the command line; no machine-specific path is used.
Reproducibility notes:
    Files are copied byte for byte (shutil.copy2) and made user-writable; the workspace can be deleted
    and rebuilt at any time. An existing workspace directory is never overwritten.
Warnings:
    The full workspace requires about 2 GB of free space before the pipeline regenerates its outputs.
"""
import argparse
import os
import shutil
import stat
import sys

# Dataset directory -> workspace directory, grouped by part.
MAP = {
    "raw": [("images_raw/in_situ_rgb", "entradas"), ("images_raw/harvested_roots", "entradas/Raizes"),
            ("annotations/blind_assessment/assessor_sheets", "entradas/Especialistas")],
    "processed": [("images_processed/conditioned", "saidas/05A_tratadas")],
    "masks": [("masks/reconstruction", "saidas/05A_tratadas/_mascaras"), ("masks/m2_unet", "saidas/06C_inferencia/masks")],
    "assessment": [("annotations/blind_assessment/assessor_sheets", "metricas/notas_recebidas")],
    "tabular": [("tabular_data/electrical", "tabdatas"), ("tabular_data/biomass", "tabdatas")],
    "metrics": [("tabular_data/non_regenerable_results", "metricas")],
    "metadata": [("metadata/external_split.csv", "manifestos/external_split.csv")],
}
REVIEW = ["review_key.csv"]


def copy_tree(src, dst):
    """
    Purpose:
        Copy every file below src into dst, preserving relative paths.
    Parameters:
        src (str): Existing source directory (read only).
        dst (str): Destination directory inside the workspace.
    Returns:
        int: Number of files copied.
    Raises:
        FileNotFoundError: If src does not exist.
    Notes:
        Existing destination files are not overwritten.
    """
    if os.path.isfile(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        os.chmod(dst, os.stat(dst).st_mode | stat.S_IWUSR)
        return 1
    if not os.path.isdir(src):
        raise FileNotFoundError(src)
    n = 0
    for d, _, files in os.walk(src):
        for f in files:
            s = os.path.join(d, f)
            t = os.path.join(dst, os.path.relpath(s, src))
            if os.path.exists(t):
                continue
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(s, t)
            os.chmod(t, os.stat(t).st_mode | stat.S_IWUSR)
            n += 1
    return n


def main():
    """
    Purpose:
        Parse arguments and build the workspace.
    Parameters:
        None (command-line arguments).
    Returns:
        None
    Raises:
        SystemExit: If the workspace already exists or an argument is invalid.
    Notes:
        Scripts, configuration and model weights are always copied.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("Purpose:")[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--software", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--parts", default="raw,processed,masks,assessment,tabular,metrics,metadata,models")
    a = ap.parse_args()
    if os.path.exists(a.workspace):
        sys.exit("workspace already exists: " + a.workspace)
    parts = [p.strip() for p in a.parts.split(",") if p.strip()]
    for p in parts:
        if p not in MAP and p != "models":
            sys.exit("unknown part: " + p)
    n = copy_tree(os.path.join(a.software, "scripts"), os.path.join(a.workspace, "scripts"))
    n += copy_tree(os.path.join(a.software, "config"), os.path.join(a.workspace, "config"))
    if "models" in parts:
        n += copy_tree(os.path.join(a.software, "models"), os.path.join(a.workspace, "modelos"))
    for p in parts:
        for s, t in MAP.get(p, []):
            n += copy_tree(os.path.join(a.dataset, s), os.path.join(a.workspace, t))
    for d in ("Artigo_revista", "figures", "figdata", "manifestos", "metricas"):
        os.makedirs(os.path.join(a.workspace, d), exist_ok=True)   # output directories expected by the scripts
    if "metrics" in parts or "assessment" in parts:
        for f in REVIEW:
            s = os.path.join(a.dataset, "annotations/blind_assessment", f)
            if os.path.exists(s):
                t = os.path.join(a.workspace, "metricas", f)
                shutil.copy2(s, t)
                os.chmod(t, os.stat(t).st_mode | stat.S_IWUSR)
                n += 1
    print(f"workspace ready: {a.workspace} ({n} files)")


if __name__ == "__main__":
    main()
