#!/usr/bin/env python3
"""
Title:
    Image quality control and central glare
File type:
    Script
Purpose:
    Computes, on normalised luminance, brightness, contrast, sharpness (Laplacian variance), global
    over- and under-exposure and central glare indices (G_c, R_c, glare class) for every converted
    image; no correction is applied.
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
    - saidas/03_convertidas
Outputs:
    - manifestos/03_conversao.csv
    - metricas/image_qc.csv
Dependencies:
    - PIL
    - numpy
    - skimage
    - local: config
Execution:
    python scripts/04_qc_imagens.py (from a workspace prepared with tools/prepare_workspace.py)
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
Fase 04 — Controle de qualidade das imagens + quantificação do glare central.

Para cada imagem convertida (Fase 03) calcula, no canal de luminosidade L*
normalizado (L_n):
  - brilho médio μ_L, contraste σ_L, nitidez B = Var(∇²L_n)
  - super/subexposição global F_over, F_under
  - glare central: G_c (saturação em Ω_c=35–65%), R_c (brilho centro/periferia),
    glare_flag (0=ausente/baixo, 1=moderado, 2=intenso)
NÃO corrige nada (isso é da Fase 07). Só mede e sinaliza.

Regra de QC do usuário: imagem de raiz = retrato; paisagem ⇒ não-raiz/revisar.

Saída: metricas/image_qc.csv  (uma linha por imagem)
"""
import os
import sys
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

import numpy as np
from PIL import Image
from skimage.color import rgb2lab
from skimage.filters import laplace

IMG_DIR = C.SAIDAS / "03_convertidas"
OUT_CSV = C.METRICAS / "image_qc.csv"
LOG03 = C.MANIFESTOS / "03_conversao.csv"


def orientacao_por_id():
    """Lê orientation_flag da tabela da Fase 03 (para a regra raiz=retrato)."""
    m = {}
    if LOG03.exists():
        with open(LOG03, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                m[r["image_id"]] = r.get("orientation_flag", "")
    return m


def metricas_imagem(path):
    """
    Purpose:
        Compute brightness, contrast, sharpness, exposure fractions and central glare indices of one image.
    Parameters:
        path: converted PNG image
    Returns:
        dict of quality metrics
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    L = rgb2lab(rgb)[:, :, 0]                       # L* em [0,100]
    Ln = (L - L.min()) / (L.max() - L.min() + 1e-8)  # normalizado [0,1]
    H, W = Ln.shape

    mu = float(Ln.mean())
    sigma = float(Ln.std())
    B = float(np.var(laplace(Ln)))                 # nitidez
    F_over = float(np.mean(Ln >= C.QC_TAU_OVER))
    F_under = float(np.mean(Ln <= C.QC_TAU_UNDER))

    a1, a2, b1, b2 = C.QC_CENTRAL
    x0, x1 = int(a1 * W), int(a2 * W)
    y0, y1 = int(b1 * H), int(b2 * H)
    central = Ln[y0:y1, x0:x1]
    mask_perif = np.ones_like(Ln, dtype=bool)
    mask_perif[y0:y1, x0:x1] = False

    G_c = float(np.mean(central >= C.QC_TAU_SAT))
    R_c = float(central.mean() / (Ln[mask_perif].mean() + 1e-8))
    glare = 0 if G_c < C.QC_GAMMA1 else (1 if G_c < C.QC_GAMMA2 else 2)

    return dict(mu_L=mu, sigma_L=sigma, B=B, F_over=F_over, F_under=F_under,
                G_c=G_c, R_c=R_c, glare_flag=glare, H=H, W=W)


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
    orient = orientacao_por_id()
    imgs = sorted(IMG_DIR.rglob("*.png"))
    if not imgs:
        print("[Fase 04] Nenhuma imagem convertida encontrada (rode a Fase 03).")
        return

    linhas = []
    for p in imgs:
        iid = p.stem
        try:
            m = metricas_imagem(p)
            oflag = orient.get(iid, "")
            eh_raiz = (oflag != "paisagem")   # regra: raiz = retrato

            usable = int(
                (m["B"] >= C.QC_B_MIN) and
                (m["F_over"] <= C.QC_FOVER_MAX) and
                (m["F_under"] <= C.QC_FUNDER_MAX) and
                eh_raiz
            )
            motivos = []
            if not eh_raiz: motivos.append("orientacao_paisagem(nao_raiz)")
            if m["B"] < C.QC_B_MIN: motivos.append("desfocada")
            if m["F_over"] > C.QC_FOVER_MAX: motivos.append("superexposta")
            if m["F_under"] > C.QC_FUNDER_MAX: motivos.append("subexposta")

            linhas.append({
                "image_id": iid,
                "path": str(p.relative_to(C.ROOT)),
                "orientation_flag": oflag,
                "mu_L": round(m["mu_L"], 4),
                "sigma_L": round(m["sigma_L"], 4),
                "B": round(m["B"], 8),
                "F_over": round(m["F_over"], 5),
                "F_under": round(m["F_under"], 5),
                "G_c": round(m["G_c"], 5),
                "R_c": round(m["R_c"], 4),
                "glare_flag": m["glare_flag"],
                "overexposure_center": int(m["G_c"] >= C.QC_GAMMA1),
                "low_confidence_region": int(m["glare_flag"] == 2),
                "usable_image": usable,
                "exclusion_reason": ";".join(motivos),
            })
        except Exception as e:
            linhas.append({"image_id": iid, "path": str(p.relative_to(C.ROOT)),
                           "orientation_flag": "", "mu_L": "", "sigma_L": "", "B": "",
                           "F_over": "", "F_under": "", "G_c": "", "R_c": "",
                           "glare_flag": "", "overexposure_center": "",
                           "low_confidence_region": "", "usable_image": 0,
                           "exclusion_reason": f"erro:{e}"})

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader(); w.writerows(linhas)

    # Resumo
    from collections import Counter
    gl = Counter(r["glare_flag"] for r in linhas)
    us = sum(1 for r in linhas if r["usable_image"] == 1)
    Bs = [r["B"] for r in linhas if isinstance(r["B"], float)]
    print(f"[Fase 04] QC de {len(linhas)} imagens  ->  {OUT_CSV.relative_to(C.ROOT)}")
    print(f"   Utilizáveis: {us}/{len(linhas)}")
    print(f"   glare_flag: 0(baixo)={gl.get(0,0)}  1(moderado)={gl.get(1,0)}  2(intenso)={gl.get(2,0)}")
    if Bs:
        print(f"   Nitidez B: min={min(Bs):.2e}  mediana={sorted(Bs)[len(Bs)//2]:.2e}  max={max(Bs):.2e}")
    baixa = sum(1 for r in linhas if r["low_confidence_region"] == 1)
    print(f"   Imagens com região de baixa confiança (glare intenso): {baixa}")


if __name__ == "__main__":
    main()
