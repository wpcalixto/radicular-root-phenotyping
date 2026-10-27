#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    Flag counts for the six diagnostic cases
File type:
    Script
Purpose:
    Counts acceptance (n/12) and M3 issue flags (n/5) for the six diagnostic images (Table S14,
    Order 22).
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
    - Python standard library
Execution:
    python scripts/auxiliary/casos_flags.py (from a workspace prepared with
    tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Not re-executed in the v1.0.0 verification. Environment of the verification: Python 3.9.6
    (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
import sys, csv, collections, importlib.util, contextlib, io
spec = importlib.util.spec_from_file_location('s', '08D_selecao.py'); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
with contextlib.redirect_stdout(io.StringIO()):
    rows = s.carregar()
key = {(r["image_id"], r["codigo"]): r["metodo_real"] for r in csv.DictReader(open(s.KEY, encoding='utf-8'))}
casos = ['R03_07_06_2025','R01_23_05_2025','R04_23_05_2025','R04_05_07_2025','R08_05_07_2025','R04_07_06_2025']
c = collections.defaultdict(collections.Counter)
for r in rows:
    m = s.LABELS.get(key.get((r["image_id"], r.get("codigo")), "?"), "?")
    if m != 'M3' or r['image_id'] not in casos: continue
    a = int(r['avaliador'][1:]); d = c[r['image_id']]
    d['n'] += 1; d['acc'] += s.aceito(r.get('aceita'))
    if a <= 5: d['n5'] += 1
    for k in s.PROB_COLS:
        if s.marcado(r.get(k)): d[k] += 1; d[k+'_A6+'] += (a > 5)
for i in casos:
    d = c[i]; print(i, f"acc {d['acc']}/{d['n']} n5={d['n5']} solo {d['prob_excesso_solo']} falta {d['prob_falta_raiz']} frag {d['prob_fragmentado']} glare {d['prob_glare']} flagsA6+ {sum(v for k,v in d.items() if k.endswith('A6+'))}")
