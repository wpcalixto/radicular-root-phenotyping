#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    A15 with approved padding
File type:
    Script
Purpose:
    Runs A15_ampliacoes.py restoring savefig.pad_inches = 0.10, the configuration of the approved
    21_figura_resultado PDFs (Order 20-H).
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-10-25
Date:
    2026-10-25
Developer:
    Prof. Wesley Pacheco Calixto
Authors:
    Wesley Pacheco Calixto; Universidade de Coimbra (UC), Portugal; Universidade Federal de Goiás
    (UFG), Brazil; Instituto Federal de Educação, Ciência e Tecnologia de Goiás (IFG), Brazil
    (direction). Code prepared with an AI coding assistant (Claude, Anthropic) under the author's
    direction in Orders 20-F/20-G/20-H/22 of the manuscript preparation
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
    - printed results only
Dependencies:
    - matplotlib
    - runpy
    - local: estilo_figuras
Execution:
    python scripts/auxiliary/run_A15_pad010.py (from a workspace prepared with
    tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi)
    with identical page size to the RSOS files (SHA-256 differs only by PDF metadata). Environment
    of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Executa A15_ampliacoes.py repondo savefig.pad_inches=0.10, configuracao dos PDFs aprovados (31/07/2026)
import sys,runpy,matplotlib
sys.path.insert(0,'.')
import estilo_figuras as E
_ap=E.aplicar
def aplicar(*a,**k):
    """
    Purpose:
        Wrap estilo_figuras.aplicar and restore savefig.pad_inches = 0.10 after it.
    Parameters:
        *a, **k: arguments forwarded to estilo_figuras.aplicar
    Returns:
        value returned by estilo_figuras.aplicar
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    r=_ap(*a,**k); matplotlib.rcParams['savefig.pad_inches']=0.10; return r
E.aplicar=aplicar
runpy.run_path('A15_ampliacoes.py',run_name='__main__')
