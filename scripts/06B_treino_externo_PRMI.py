#!/usr/bin/env python3
"""
Title:
    U-Net training on PRMI (script export)
File type:
    Script
Purpose:
    Script export of the Colab notebook that trains the U-Net (M2) on PRMI in a development phase
    with validation and a final phase on all PRMI data. The archived file declares 40 epochs; the
    weights used in the study come from a 25-epoch execution (see docs/06B_training_provenance.md).
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
    - printed results only
Dependencies:
    - albumentations
    - cv2
    - google
    - numpy
    - segmentation_models_pytorch
    - torch
Execution:
    python scripts/06B_treino_externo_PRMI.py (from a workspace prepared with
    tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Random seeds in code: 42. Not re-executed in the v1.0.0 verification. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    The archived configuration declares 40 epochs (epochs_dev = epochs_final = 40); the weights used
    in the study were produced by a 25-epoch execution on 2026-07-06 whose script version was not
    preserved. See docs/06B_training_provenance.md. Requires the external PRMI archive (Zenodo
    10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages. Contains
    instructions referring to Google Drive/Colab/rclone storage used during the original execution;
    these are historical and optional.
"""
# Original module notes (Portuguese) are preserved below.
"""Fase 06B — treino do modelo externo PRMI (export do notebook Colab).
Par executavel: 06B_treino_externo_PRMI.ipynb. A Fase 08A agora e script proprio.
Linhas de magic do Colab (!pip, !unzip) ficam comentadas aqui (so rodam no .ipynb)."""


# ======================================================================
# # Fase 06B — Treino do modelo externo de segmentação radicular (PRMI)
# 
# **Protocolo de 2 modelos** (decisão do projeto):
# - **06B-1 (desenvolvimento):** treina no `train`, monitora no `val`, avalia **uma vez** no `test` → escolhe arquitetura, função de perda, limiar e hiperparâmetros.
# - **06B-2 (final):** com a configuração **congelada**, treina em `train ∪ val ∪ test` (todas as imagens com máscara) → modelo `f_θ^PRMI-all`, usado **apenas** para inferência nas imagens locais (Fase 06C).
# 
# **Dataset:** PRMI (licença **CC0**), **63.943** imagens com máscara pixel. Zip no Drive:
# `Sistema_Radicular/Dataset_PRMI/PRMI_official.zip`.
# 
# **Saídas (salvas no Drive `Dataset_PRMI/modelos_06B/`):**
# `external_development_model.pt`, `external_development_metrics.csv`,
# `external_final_model_PRMI_all.pt`, `training_log.csv`, `model_configuration.json`.
# 
# **Redação para o artigo:** métricas no PRMI `test` são **diagnóstico de desenvolvimento**,
# não validação do modelo final; a avaliação real é feita nas **imagens locais por
# especialistas** (Fase 08). Como o modelo final usa train+val+test, o `test` não é teste independente dele.


# ======================================================================
# ## CPU ou GPU? → **GPU obrigatória**
# Treinar U-Net em dezenas de milhares de imagens em **CPU é inviável** (dias/semanas).
# 
# | GPU | VRAM | Uso recomendado |
# |---|---|---|
# | **T4** | 16 GB | funciona (batch menor); ok p/ desenvolvimento, mais lento |
# | **L4** | 24 GB | **melhor custo/benefício** p/ desenvolvimento (06B-1) |
# | **A100** | 40/80 GB | **treino final** (06B-2) nas 63k — rápido, batch grande |
# | **H100** | 80 GB | desnecessário p/ U-Net (ganho marginal, caro) |
# 
# Ative em **Ambiente de execução → Alterar o tipo de ambiente de execução → GPU**.
# O notebook detecta a GPU e ajusta o *batch size* automaticamente.

# ---- celula de codigo 2 ----
# 1) GPU disponível?
import torch, subprocess
print("CUDA disponível:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print(subprocess.getoutput("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"))
else:
    print("SEM GPU — troque o ambiente para GPU (T4/L4/A100). Treino em CPU não é viável.")

# ---- celula de codigo 3 ----
# 2) Dependências
# [colab-magic] !pip -q install segmentation-models-pytorch==0.3.4 albumentations==1.4.0 2>/dev/null
import segmentation_models_pytorch as smp, albumentations as A
from albumentations.pytorch import ToTensorV2
print("smp", smp.__version__, "| albumentations", A.__version__)

# ---- celula de codigo 4 ----
# 3) Montar Google Drive
from google.colab import drive
drive.mount('/content/drive')
DRIVE_PRMI = '/content/drive/MyDrive/Sistema_Radicular/Dataset_PRMI'
import os; assert os.path.exists(DRIVE_PRMI), f"Pasta nao encontrada: {DRIVE_PRMI}"
print("OK:", os.listdir(DRIVE_PRMI))


# ======================================================================
# ## Configuração
# Ajuste `IMG_SIZE`, `EPOCHS`, encoder e `SUBSET_FRAC` (use <1.0 para teste rápido).
# O `BATCH` é definido automaticamente pela VRAM da GPU.

# ---- celula de codigo 6 ----
# 4) Config
import torch
CFG = dict(
    zip_path   = f'{DRIVE_PRMI}/PRMI_official.zip',
    work_dir   = '/content/PRMI',                    # extração local (rápida)
    out_dir    = f'{DRIVE_PRMI}/modelos_06B',        # saídas -> Drive
    ckpt_dir   = f'{DRIVE_PRMI}/modelos_06B/checkpoints',
    encoder    = 'resnet34',                          # alt.: efficientnet-b0, resnet50
    encoder_weights = 'imagenet',
    img_size   = 512,
    epochs_dev = 40,
    epochs_final = 40,
    patience   = 8,                                   # early stopping (dev)
    lr         = 1e-4,
    bce_w      = 0.5,  dice_w = 0.5,                  # perda = 0.5 BCE + 0.5 Dice
    thr        = 0.5,                                 # limiar de binarização tau_p
    subset_frac = 1.0,                                # <1.0 p/ iterar rápido
    seed       = 42,
)
os.makedirs(CFG['out_dir'], exist_ok=True); os.makedirs(CFG['ckpt_dir'], exist_ok=True)

# batch automático pela VRAM
mem = torch.cuda.get_device_properties(0).total_memory/1e9 if torch.cuda.is_available() else 0
CFG['batch'] = (48 if mem>=70 else 32 if mem>=38 else 16 if mem>=22 else 10 if mem>=14 else 4)
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
torch.manual_seed(CFG['seed'])
print(f"VRAM ~{mem:.0f} GB -> batch {CFG['batch']} | device {DEVICE} | img {CFG['img_size']}")
CFG

# ---- celula de codigo 7 ----
# 5) Extrair o PRMI (zip do Drive -> disco local do Colab)
import os, time
if not os.path.exists(f"{CFG['work_dir']}/PRMI_official"):
    os.makedirs(CFG['work_dir'], exist_ok=True); t=time.time()
    print("Extraindo ~9.75GB (pode levar alguns minutos)...")
# [colab-magic]     !unzip -q "{CFG['zip_path']}" -d "{CFG['work_dir']}"
    print(f"extraido em {time.time()-t:.0f}s")
ROOT = f"{CFG['work_dir']}/PRMI_official"
print("splits:", os.listdir(ROOT))

# ---- celula de codigo 8 ----
# 6) Pares imagem<->mascara (apenas imagens COM mascara). GT_<nome>.png
import glob
def listar_pares(root, split):
    """
    Purpose:
        List image-mask pairs of a PRMI split.
    Parameters:
        root: extracted PRMI root
        split: train, val or test
    Returns:
        list of (image, mask) paths
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    pares, img_root = [], os.path.join(root, split, 'images')
    msk_root = os.path.join(root, split, 'masks_pixel_gt')
    for sp in sorted(os.listdir(img_root)):
        spd = os.path.join(img_root, sp)
        if not os.path.isdir(spd): continue
        for fn in os.listdir(spd):
            if not fn.lower().endswith(('.jpg','.jpeg','.png')): continue
            stem = os.path.splitext(fn)[0]
            mp = os.path.join(msk_root, sp, f'GT_{stem}.png')
            if os.path.exists(mp):
                pares.append((os.path.join(spd, fn), mp))
    return pares

pares = {s: listar_pares(ROOT, s) for s in ['train','val','test']}
for s in pares: print(f"{s}: {len(pares[s])} pares com mascara")
if CFG['subset_frac'] < 1.0:
    import random; random.seed(CFG['seed'])
    for s in pares:
        k=max(1,int(len(pares[s])*CFG['subset_frac'])); pares[s]=random.sample(pares[s], k)
    print("SUBSET:", {s:len(pares[s]) for s in pares})
pares_all = pares['train'] + pares['val'] + pares['test']   # para o modelo final (06B-2)
print("all (final):", len(pares_all))


# ======================================================================
# ## Dataset e aumentação
# Redimensiona imagem+máscara para `IMG_SIZE`, normaliza (estatísticas ImageNet, pois o
# encoder é pré-treinado). No treino: flips e rotações leves.

# ---- celula de codigo 10 ----
# 7) Dataset
import cv2, numpy as np
from torch.utils.data import Dataset, DataLoader
IMEAN=(0.485,0.456,0.406); ISTD=(0.229,0.224,0.225); S=CFG['img_size']

def aug_train():
    """
    Purpose:
        Build the training augmentation pipeline.
    Parameters:
        none
    Returns:
        albumentations.Compose
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return A.Compose([A.Resize(S,S), A.HorizontalFlip(p=.5), A.VerticalFlip(p=.5),
                      A.RandomRotate90(p=.5), A.RandomBrightnessContrast(p=.3),
                      A.Normalize(IMEAN,ISTD), ToTensorV2()])
def aug_eval():
    """
    Purpose:
        Build the evaluation transform pipeline.
    Parameters:
        none
    Returns:
        albumentations.Compose
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return A.Compose([A.Resize(S,S), A.Normalize(IMEAN,ISTD), ToTensorV2()])

class PRMISet(Dataset):
    """
    Purpose:
        Dataset of PRMI image-mask pairs with a transform.
    Parameters:
        pares: list of pairs
        tf: transform
    Returns:
        torch Dataset
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    def __init__(self, pares, tf): self.p=pares; self.tf=tf
    def __len__(self): return len(self.p)
    def __getitem__(self, i):
        ip, mp = self.p[i]
        img = cv2.cvtColor(cv2.imread(ip), cv2.COLOR_BGR2RGB)
        m = cv2.imread(mp, cv2.IMREAD_GRAYSCALE)
        m = (m>127).astype('float32')
        a = self.tf(image=img, mask=m)
        return a['image'], a['mask'].unsqueeze(0)

def loader(pares, tf, shuffle):
    """
    Purpose:
        Create a DataLoader for a list of pairs.
    Parameters:
        pares: pairs
        tf: transform
        shuffle: shuffle flag
    Returns:
        torch DataLoader
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return DataLoader(PRMISet(pares, tf), batch_size=CFG['batch'], shuffle=shuffle,
                      num_workers=2, pin_memory=True, drop_last=shuffle)


# ======================================================================
# ## Modelo, perda e métricas
# U-Net (encoder pré-treinado). Perda = `bce_w`·BCE + `dice_w`·Dice. Métricas: Dice e IoU.

# ---- celula de codigo 12 ----
# 8) Modelo + perda + métricas
import torch.nn as nn
def build_model():
    """
    Purpose:
        Instantiate the U-Net with the configured encoder.
    Parameters:
        none
    Returns:
        segmentation_models_pytorch.Unet
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return smp.Unet(encoder_name=CFG['encoder'], encoder_weights=CFG['encoder_weights'],
                    in_channels=3, classes=1).to(DEVICE)

bce = nn.BCEWithLogitsLoss(); dice_loss = smp.losses.DiceLoss(mode='binary')
def criterion(logits, mask):
    """
    Purpose:
        Weighted sum of BCE and Dice losses.
    Parameters:
        logits: model output
        mask: ground truth
    Returns:
        torch scalar
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return CFG['bce_w']*bce(logits, mask) + CFG['dice_w']*dice_loss(logits, mask)

@torch.no_grad()
def metricas(logits, mask, thr=None):
    """
    Purpose:
        Compute Dice and IoU at a threshold.
    Parameters:
        logits: model output
        mask: ground truth
        thr: threshold (default from CFG)
    Returns:
        tuple of floats
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    thr = CFG['thr'] if thr is None else thr
    p = (torch.sigmoid(logits) >= thr).float()
    inter = (p*mask).sum((1,2,3)); ps=p.sum((1,2,3)); ms=mask.sum((1,2,3))
    dice = ((2*inter+1e-6)/(ps+ms+1e-6)).mean().item()
    iou  = ((inter+1e-6)/(ps+ms-inter+1e-6)).mean().item()
    return dice, iou


# ---- celula de codigo 13 ----
# 9) Funções de treino/validação (com AMP)
from torch.cuda.amp import autocast, GradScaler
def run_epoch(model, dl, opt=None, scaler=None):
    """
    Purpose:
        Run one training or evaluation epoch.
    Parameters:
        model: U-Net
        dl: DataLoader
        opt: optimiser or None for evaluation
        scaler: AMP scaler
    Returns:
        dict of epoch metrics
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    train = opt is not None; model.train() if train else model.eval()
    tot=dict(loss=0,dice=0,iou=0); n=0
    for img, mask in dl:
        img, mask = img.to(DEVICE), mask.to(DEVICE)
        with torch.set_grad_enabled(train), autocast(enabled=torch.cuda.is_available()):
            logits = model(img); loss = criterion(logits, mask)
        if train:
            opt.zero_grad(); scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
        d,i = metricas(logits.float(), mask); bs=img.size(0); n+=bs
        tot['loss']+=loss.item()*bs; tot['dice']+=d*bs; tot['iou']+=i*bs
    return {k:v/n for k,v in tot.items()}


# ======================================================================
# ## 06B-1 — Modelo de desenvolvimento
# Treina no `train`, valida no `val`, salva o melhor por Dice de validação. *Checkpoint* no
# Drive a cada época (resistente a desconexões do Colab) e *early stopping*.

# ---- celula de codigo 15 ----
# 10) Treino de desenvolvimento
import csv, json, time
dl_tr, dl_va = loader(pares['train'], aug_train(), True), loader(pares['val'], aug_eval(), False)
model = build_model()
opt = torch.optim.AdamW(model.parameters(), lr=CFG['lr'], weight_decay=1e-4)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=CFG['epochs_dev'])
scaler = GradScaler(enabled=torch.cuda.is_available())

log_path = f"{CFG['out_dir']}/training_log.csv"
logf = open(log_path,'w',newline=''); logw=csv.writer(logf)
logw.writerow(['fase','epoca','loss_tr','dice_tr','loss_val','dice_val','iou_val','lr']); logf.flush()

best, bad = -1, 0
for ep in range(1, CFG['epochs_dev']+1):
    t=time.time()
    tr = run_epoch(model, dl_tr, opt, scaler)
    va = run_epoch(model, dl_va)
    sched.step()
    logw.writerow(['dev',ep,tr['loss'],tr['dice'],va['loss'],va['dice'],va['iou'],opt.param_groups[0]['lr']]); logf.flush()
    print(f"[dev {ep:02d}] tr_dice={tr['dice']:.4f} val_dice={va['dice']:.4f} val_iou={va['iou']:.4f} ({time.time()-t:.0f}s)")
    torch.save(model.state_dict(), f"{CFG['ckpt_dir']}/dev_last.pt")   # resume
    if va['dice']>best:
        best=va['dice']; bad=0
        torch.save(model.state_dict(), f"{CFG['out_dir']}/external_development_model.pt")
        print(f"   * novo melhor val_dice={best:.4f} (salvo)")
    else:
        bad+=1
        if bad>=CFG['patience']: print("early stopping."); break
logf.close(); print("melhor val_dice:", best)


# ======================================================================
# ## Fase 08A movida para fase própria
# O diagnóstico no PRMI test (métricas completas) agora está em `08A_diagnostico_externo.py` / `.ipynb` — roda após o treino de desenvolvimento, usando `external_development_model.pt`.


# ======================================================================
# ## 06B-2 — Modelo final para inferência local
# Config **congelada**. Treina em `train ∪ val ∪ test` (todas com máscara). Salva
# `external_final_model_PRMI_all.pt`. Usado apenas na Fase 06C (inferência local).

# ---- celula de codigo 18 ----
# 12) Treino final (PRMI-all)
dl_all = loader(pares_all, aug_train(), True)
mfinal = build_model()
opt2 = torch.optim.AdamW(mfinal.parameters(), lr=CFG['lr'], weight_decay=1e-4)
sched2 = torch.optim.lr_scheduler.CosineAnnealingLR(opt2, T_max=CFG['epochs_final'])
scaler2 = GradScaler(enabled=torch.cuda.is_available())
logf = open(log_path,'a',newline=''); logw=csv.writer(logf)
for ep in range(1, CFG['epochs_final']+1):
    t=time.time(); tr = run_epoch(mfinal, dl_all, opt2, scaler2); sched2.step()
    logw.writerow(['final',ep,tr['loss'],tr['dice'],'','','',opt2.param_groups[0]['lr']]); logf.flush()
    print(f"[final {ep:02d}] dice={tr['dice']:.4f} ({time.time()-t:.0f}s)")
    torch.save(mfinal.state_dict(), f"{CFG['ckpt_dir']}/final_last.pt")
logf.close()
torch.save(mfinal.state_dict(), f"{CFG['out_dir']}/external_final_model_PRMI_all.pt")
print("modelo final salvo.")

# ---- celula de codigo 19 ----
# 13) Salvar configuração (reprodutibilidade)
cfg_out = dict(CFG, device=DEVICE, gpu=(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'),
               n_train=len(pares['train']), n_val=len(pares['val']), n_test=len(pares['test']),
               n_all=len(pares_all), best_val_dice=best, arquitetura='U-Net',
               framework=f"torch {torch.__version__}, smp {smp.__version__}")
with open(f"{CFG['out_dir']}/model_configuration.json",'w') as f: json.dump(cfg_out, f, indent=2, default=str)
print("Saídas no Drive:", os.listdir(CFG['out_dir']))


# ======================================================================
# ## Concluído — próximo: **Fase 06C (inferência local)**
# Use `external_final_model_PRMI_all.pt` para segmentar as nossas 82 imagens registradas
# (Fase 05) → máscara candidata `M^Ext`. A avaliação real (Fase 08) é por especialistas,
# comparando `M^Ext` (este modelo) com `M^Frangi` (Fase 07).
# 
# **Notas:** o notebook faz *checkpoint* por época no Drive (`checkpoints/`), permitindo
# retomar após desconexões; use `subset_frac<1.0` para iterar rápido antes do treino completo.
