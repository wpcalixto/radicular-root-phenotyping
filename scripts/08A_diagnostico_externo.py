#!/usr/bin/env python3
"""
Title:
    Diagnostic metrics of the external model on PRMI test
File type:
    Script
Purpose:
    Evaluates the development U-Net once on the PRMI test subset and reports micro and macro Dice,
    IoU, precision, recall, specificity, FPR and FNR.
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
    - none detected by static analysis
Outputs:
    - {DRIVE_PRMI}/modelos_06B/external_diagnostic_metrics.csv
Dependencies:
    - albumentations
    - cv2
    - numpy
    - segmentation_models_pytorch
    - torch
Execution:
    python scripts/08A_diagnostico_externo.py (from a workspace prepared with
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
Fase 08A — Diagnóstico quantitativo do modelo externo no domínio EXTERNO (PRMI test).

Avalia o **modelo de desenvolvimento** (06B-1, `external_development_model.pt`) UMA única
vez no subconjunto `test` do PRMI, com métricas completas derivadas de TP/FP/TN/FN:
Dice, IoU, Precision, Recall (sensibilidade), Specificity, FPR e FNR — em versão
**micro** (global, somando TP/FP sobre todo o conjunto) e **macro** (média por imagem).

IMPORTANTE (metodologia): são métricas **só de desenvolvimento**. NÃO validam o modelo
final (que usa train∪val∪test). A avaliação real é nas imagens locais, por especialistas
(Fases 08B–08D).

Roda no Google Colab (GPU + Drive). Par: `08A_diagnostico_externo.ipynb`.
Saída: {DRIVE_PRMI}/modelos_06B/external_diagnostic_metrics.csv
"""
import os
import glob
import csv

import numpy as np
import cv2
import torch
from torch.utils.data import Dataset, DataLoader
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2

DRIVE_PRMI = os.environ.get("DRIVE_PRMI",
                            "/content/drive/MyDrive/Sistema_Radicular/Dataset_PRMI")
WORK = os.environ.get("PRMI_WORK", "/content/PRMI")
CFG = dict(encoder="resnet34", img_size=512, thr=0.5, batch=16)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
IMEAN = (0.485, 0.456, 0.406); ISTD = (0.229, 0.224, 0.225)
MODELO_DEV = f"{DRIVE_PRMI}/modelos_06B/external_development_model.pt"
OUT_CSV = f"{DRIVE_PRMI}/modelos_06B/external_diagnostic_metrics.csv"


def preparar_prmi():
    """Extrai o zip do PRMI (uma vez) e devolve a raiz."""
    root = f"{WORK}/PRMI_official"
    if not os.path.exists(root):
        os.makedirs(WORK, exist_ok=True)
        os.system(f'unzip -q "{DRIVE_PRMI}/PRMI_official.zip" -d "{WORK}"')
    return root


def listar_pares(root, split):
    """Pares imagem↔máscara (só imagens COM máscara GT_<nome>.png)."""
    pares = []
    img_root = os.path.join(root, split, "images")
    msk_root = os.path.join(root, split, "masks_pixel_gt")
    for sp in sorted(os.listdir(img_root)):
        spd = os.path.join(img_root, sp)
        if not os.path.isdir(spd):
            continue
        for fn in os.listdir(spd):
            if not fn.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            stem = os.path.splitext(fn)[0]
            mp = os.path.join(msk_root, sp, f"GT_{stem}.png")
            if os.path.exists(mp):
                pares.append((os.path.join(spd, fn), mp))
    return pares


def aug_eval():
    """
    Purpose:
        Build the evaluation transform.
    Parameters:
        none
    Returns:
        albumentations.Compose
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return A.Compose([A.Resize(CFG["img_size"], CFG["img_size"]),
                      A.Normalize(IMEAN, ISTD), ToTensorV2()])


class PRMISet(Dataset):
    """
    Purpose:
        Dataset of PRMI test pairs.
    Parameters:
        pares: pairs
        tf: transform
    Returns:
        torch Dataset
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    def __init__(self, pares, tf):
        self.p = pares; self.tf = tf
    def __len__(self):
        return len(self.p)
    def __getitem__(self, i):
        ip, mp = self.p[i]
        img = cv2.cvtColor(cv2.imread(ip), cv2.COLOR_BGR2RGB)
        m = (cv2.imread(mp, cv2.IMREAD_GRAYSCALE) > 127).astype("float32")
        a = self.tf(image=img, mask=m)
        return a["image"], a["mask"].unsqueeze(0)


def build_model():
    """
    Purpose:
        Instantiate the U-Net without pretrained weights.
    Parameters:
        none
    Returns:
        segmentation_models_pytorch.Unet
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return smp.Unet(encoder_name=CFG["encoder"], encoder_weights=None,
                    in_channels=3, classes=1).to(DEVICE)


@torch.no_grad()
def metricas_completas(model, dl, thr):
    """
    Purpose:
        Accumulate TP/FP/TN/FN and compute micro and macro metrics on the test set.
    Parameters:
        model: U-Net
        dl: DataLoader
        thr: threshold
    Returns:
        dict of metrics
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    model.eval()
    TP = FP = TN = FN = 0.0; dices = []; ious = []
    for img, mask in dl:
        img, mask = img.to(DEVICE), mask.to(DEVICE)
        p = (torch.sigmoid(model(img)) >= thr).float()
        tp = (p * mask).sum((1, 2, 3)); fp = (p * (1 - mask)).sum((1, 2, 3))
        fn = ((1 - p) * mask).sum((1, 2, 3)); tn = ((1 - p) * (1 - mask)).sum((1, 2, 3))
        TP += tp.sum().item(); FP += fp.sum().item(); FN += fn.sum().item(); TN += tn.sum().item()
        dices += ((2 * tp + 1e-6) / (2 * tp + fp + fn + 1e-6)).tolist()
        ious += ((tp + 1e-6) / (tp + fp + fn + 1e-6)).tolist()
    e = 1e-9
    return dict(n=len(dices), TP=TP, FP=FP, TN=TN, FN=FN,
                dice_micro=(2 * TP) / (2 * TP + FP + FN + e), iou_micro=TP / (TP + FP + FN + e),
                precision=TP / (TP + FP + e), recall=TP / (TP + FN + e),
                specificity=TN / (TN + FP + e), fpr=FP / (FP + TN + e), fnr=FN / (FN + TP + e),
                dice_macro=sum(dices) / max(1, len(dices)), iou_macro=sum(ious) / max(1, len(ious)))


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
    root = preparar_prmi()
    pares_test = listar_pares(root, "test")
    print(f"PRMI test: {len(pares_test)} pares | device={DEVICE}")
    dl = DataLoader(PRMISet(pares_test, aug_eval()), batch_size=CFG["batch"], num_workers=2)

    model = build_model()
    model.load_state_dict(torch.load(MODELO_DEV, map_location=DEVICE))
    M = metricas_completas(model, dl, CFG["thr"])

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["conjunto", "n", "TP", "FP", "TN", "FN", "dice_micro", "iou_micro",
                    "precision", "recall_sensibilidade", "specificity", "fpr", "fnr",
                    "dice_macro", "iou_macro"])
        w.writerow(["PRMI_test", M["n"], int(M["TP"]), int(M["FP"]), int(M["TN"]), int(M["FN"]),
                    round(M["dice_micro"], 4), round(M["iou_micro"], 4), round(M["precision"], 4),
                    round(M["recall"], 4), round(M["specificity"], 4), round(M["fpr"], 4),
                    round(M["fnr"], 4), round(M["dice_macro"], 4), round(M["iou_macro"], 4)])
    print("Fase 08A — diagnóstico externo (PRMI test):",
          {k: (round(v, 4) if isinstance(v, float) else v) for k, v in M.items()})
    print("Métricas SÓ de desenvolvimento; NÃO validam o modelo final. Saída:", OUT_CSV)


if __name__ == "__main__":
    main()
