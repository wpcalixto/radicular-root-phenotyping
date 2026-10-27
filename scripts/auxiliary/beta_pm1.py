#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    Regression of M3 score on Frangi share and DAP
File type:
    Script
Purpose:
    Fits Q_M3 ~ P_M1 + DAP by least squares with rhizotron bootstrap intervals (beta_PM1 = -1.09
    [-2.04; -0.10]) from A1_composicao_m3.csv and 08D_selecao_por_imagem.csv.
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
    - numpy
    - pandas
Execution:
    python scripts/auxiliary/beta_pm1.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Verification in v1.0.0: re-executed in an isolated workspace built
    from the Dataset; outputs byte-identical to the archived versions. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
import pandas as pd,numpy as np,sys
v=sys.argv[1]
a=pd.read_csv(f'{v}/metricas/A1_composicao_m3.csv'); s=pd.read_csv(f'{v}/metricas/08D_selecao_por_imagem.csv')
d=a.copy()
d['DAP']=(pd.to_datetime(d.image_id.str[4:],format='%d_%m_%Y')-pd.Timestamp('2025-04-23')).dt.days; d['riz']=d.image_id.str[:3]
X=np.c_[np.ones(len(d)),d.P_M1,d.DAP]; y=d.Q_M3.values
b=np.linalg.lstsq(X,y,rcond=None)[0]
rng=np.random.default_rng(42); R=d.riz.unique(); B=[]
for _ in range(5000):
    pick=rng.choice(R,len(R),replace=True); dd=pd.concat([d[d.riz==r] for r in pick])
    B.append(np.linalg.lstsq(np.c_[np.ones(len(dd)),dd.P_M1,dd.DAP],dd.Q_M3.values,rcond=None)[0])
B=np.array(B); print(v,'n',len(d),'DAP NaN',d.DAP.isna().sum(),'beta_PM1=%.3f [%.3f;%.3f] beta_DAP=%.4f [%.4f;%.4f]'%(b[1],*np.percentile(B[:,1],[2.5,97.5]),b[2],*np.percentile(B[:,2],[2.5,97.5])))
