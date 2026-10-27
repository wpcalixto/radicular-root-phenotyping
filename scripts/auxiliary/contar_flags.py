#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    Issue-flag counts by denominator
File type:
    Script
Purpose:
    Counts the issue flags per method from the 12 assessor sheets and reports frequencies over the
    410 judgements of the five flagging assessors and over all 984 judgements (Table 5, Order 22).
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
    python scripts/auxiliary/contar_flags.py (from a workspace prepared with
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
import sys, csv, collections
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location('s', '08D_selecao.py'); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    rows = s.carregar()
key = {(r["image_id"], r["codigo"]): r["metodo_real"] for r in csv.DictReader(open(s.KEY, encoding='utf-8'))}
cnt = collections.defaultdict(lambda: collections.Counter()); tot = collections.Counter(); tot5 = collections.Counter()
peraval = collections.defaultdict(collections.Counter)
for r in rows:
    m = s.LABELS.get(key.get((r["image_id"], r.get("codigo")), "?"), "?")
    a = int(r['avaliador'][1:])
    tot[m] += 1
    if a <= 5: tot5[m] += 1
    for c in s.PROB_COLS:
        if s.marcado(r.get(c)):
            cnt[m][c] += 1; peraval[r['avaliador']][c] += 1
print('totais', dict(tot), 'A1-A5', dict(tot5))
for m in ['M1','M2','M3']:
    print(m, ' '.join(f"{c[5:]}={cnt[m][c]} ({100*cnt[m][c]/tot5[m]:.1f}% /410; {100*cnt[m][c]/tot[m]:.1f}% /984)" for c in s.PROB_COLS))
print('avaliadores com flags:', sorted(peraval, key=lambda x:int(x[1:])), {k: sum(v.values()) for k,v in peraval.items()})
