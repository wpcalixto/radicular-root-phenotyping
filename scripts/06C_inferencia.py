#!/usr/bin/env python3
"""
Title:
    M2 inference on the conditioned images
File type:
    Script
Purpose:
    Applies the final PRMI-trained U-Net (external_final_model_PRMI_all.pt) to the 82 conditioned
    images and writes the candidate M2 masks and overlays.
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
    - {DRIVE_PRMI}/modelos_06B/external_final_model_PRMI_all.pt
Outputs:
    - {DRIVE_PRMI}/06C_inferencia/external_local_inference_log.csv
    - {DRIVE_PRMI}/06C_inferencia/masks/<data>/<id>.png
Dependencies:
    - cv2
    - numpy
    - segmentation_models_pytorch
    - torch
Execution:
    python scripts/06C_inferencia.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: re-executed on CPU (torch 2.8, segmentation-models-pytorch 0.5.0) with
    the archived weights and JPEG inputs; 82/82 masks not byte-identical (median Dice 0.9996,
    minimum 0.9965, median 61 differing pixels), attributed to environment differences from the
    original Colab run. Environment of the verification: Python 3.9.6 (macOS) with the versions
    listed in requirements.txt.
Warnings:
    Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not
    redistributed in these packages. Contains instructions referring to Google Drive/Colab/rclone
    storage used during the original execution; these are historical and optional.
"""
# Original module notes (Portuguese) are preserved below.
"""
Fase 06C — Inferência local com o modelo externo (PRMI-all).

Aplica o modelo final `external_final_model_PRMI_all.pt` (treinado 100% no PRMI, Fase 06B)
às nossas 82 imagens TRATADAS na Fase 05A (sem flash) → máscara candidata M^Ext.

Princípios (metodologia + decisões do projeto):
  - Usa as MESMAS imagens que o método clássico (Frangi, Fase 07) — entrada idêntica p/
    a comparação de métodos (Fase 08).
  - Redimensiona PRESERVANDO O ASPECTO (lado maior = LONG, múltiplo de 32) e devolve a
    máscara ao tamanho original — NÃO usa resize quadrado (que esmagaria raízes finas).
  - Limiar de binarização τ_p = 0,5 (congelado no desenvolvimento, Fase 06B).

Executado no Google Colab (GPU + Drive). Este `.py` é a versão versionada/reprodutível;
o par `.ipynb` (06C_inferencia.ipynb) roda o mesmo código no Colab (monta o Drive antes).

Entrada:  {DRIVE_PRMI}/imagens_05A/<data>/<id>.jpg   (82 tratadas, subidas na 05A)
Modelo:   {DRIVE_PRMI}/modelos_06B/external_final_model_PRMI_all.pt
Saídas:   {DRIVE_PRMI}/06C_inferencia/masks/<data>/<id>.png      (M^Ext binária)
          {DRIVE_PRMI}/06C_inferencia/overlays/<data>/<id>.jpg   (raiz em verde)
          {DRIVE_PRMI}/06C_inferencia/external_local_inference_log.csv
"""
import os
import glob
import csv

import numpy as np
import cv2
import torch
import segmentation_models_pytorch as smp

# ----------------------------------------------------------------------
# Configuração (ajuste DRIVE_PRMI se rodar fora do Colab)
# ----------------------------------------------------------------------
DRIVE_PRMI = os.environ.get(
    "DRIVE_PRMI",
    "/content/drive/MyDrive/Sistema_Radicular/Dataset_PRMI")
ENCODER = "resnet34"
LONG = 1024          # lado maior na inferência (preserva aspecto; múltiplo de 32)
THR = 0.5            # τ_p — limiar de binarização (congelado na Fase 06B)
IMEAN = np.array([0.485, 0.456, 0.406], np.float32)   # normalização ImageNet
ISTD = np.array([0.229, 0.224, 0.225], np.float32)

LOCAIS = f"{DRIVE_PRMI}/imagens_05A"
MODELO = f"{DRIVE_PRMI}/modelos_06B/external_final_model_PRMI_all.pt"
OUT06C = f"{DRIVE_PRMI}/06C_inferencia"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_model():
    """Mesma arquitetura do treino (Fase 06B): U-Net, encoder resnet34."""
    return smp.Unet(encoder_name=ENCODER, encoder_weights=None,
                    in_channels=3, classes=1).to(DEVICE)


def preparar(rgb):
    """Resize preservando aspecto: lado maior -> LONG, ambos múltiplos de 32."""
    H0, W0 = rgb.shape[:2]
    s = LONG / max(H0, W0)
    Hn = max(32, int(round(H0 * s / 32)) * 32)
    Wn = max(32, int(round(W0 * s / 32)) * 32)
    img = cv2.resize(rgb, (Wn, Hn)).astype(np.float32) / 255.0
    x = torch.from_numpy(((img - IMEAN) / ISTD).transpose(2, 0, 1)).unsqueeze(0).to(DEVICE)
    return x, (H0, W0)


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
    for sub in ("masks", "overlays"):
        os.makedirs(f"{OUT06C}/{sub}", exist_ok=True)

    model = build_model()
    model.load_state_dict(torch.load(MODELO, map_location=DEVICE))
    model.eval()

    imgs = sorted(glob.glob(f"{LOCAIS}/**/*.jpg", recursive=True))
    assert imgs, f"nenhuma imagem em {LOCAIS} — as 82 tratadas (05A) já subiram ao Drive?"
    print(f"{len(imgs)} imagens locais | inferência com lado maior = {LONG} | device={DEVICE}")

    rows = []
    for p in imgs:
        rgb = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)
        x, (H0, W0) = preparar(rgb)
        with torch.no_grad():
            prob = torch.sigmoid(model(x))[0, 0].float().cpu().numpy()
        prob = cv2.resize(prob, (W0, H0))                 # volta ao tamanho original
        mask = (prob >= THR).astype(np.uint8)

        rel = os.path.relpath(p, LOCAIS)
        mrel = os.path.splitext(rel)[0] + ".png"          # máscara SEMPRE em PNG (binária)
        os.makedirs(os.path.dirname(f"{OUT06C}/masks/{mrel}"), exist_ok=True)
        os.makedirs(os.path.dirname(f"{OUT06C}/overlays/{rel}"), exist_ok=True)
        cv2.imwrite(f"{OUT06C}/masks/{mrel}", mask * 255)
        ov = rgb.copy(); ov[mask.astype(bool), 1] = 255
        cv2.imwrite(f"{OUT06C}/overlays/{rel}", cv2.cvtColor(ov, cv2.COLOR_RGB2BGR))

        rp = int(mask.sum())
        rows.append({"image_id": os.path.splitext(os.path.basename(p))[0],
                     "data": rel.split(os.sep)[0],
                     "prob_media": round(float(prob.mean()), 5),
                     "root_px": rp, "root_pct": round(100 * rp / (H0 * W0), 3)})
        print(f"  {rel}  root={rows[-1]['root_pct']:.2f}%")

    with open(f"{OUT06C}/external_local_inference_log.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("06C concluído ->", OUT06C)


if __name__ == "__main__":
    main()
