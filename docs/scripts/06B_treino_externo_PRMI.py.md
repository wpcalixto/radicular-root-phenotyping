# 06B_treino_externo_PRMI.py

**Title:** U-Net training on PRMI (script export)  
**File:** `scripts/06B_treino_externo_PRMI.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Script export of the Colab notebook that trains the U-Net (M2) on PRMI in a development phase with validation and a final phase on all PRMI data. The archived file declares 40 epochs; the weights used in the study come from a 25-epoch execution (see docs/06B_training_provenance.md).

## 2. Methodological stage

06B Training

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- printed results only

## 5. Dependencies

- albumentations
- cv2
- google
- numpy
- segmentation_models_pytorch
- torch

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/06B_treino_externo_PRMI.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S7

## 9. Limitations and reproduction conditions

- The archived configuration declares 40 epochs (epochs_dev = epochs_final = 40); the weights used in the study were produced by a 25-epoch execution on 2026-07-06 whose script version was not preserved. See docs/06B_training_provenance.md.
- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Contains instructions referring to Google Drive/Colab/rclone storage used during the original execution; these are historical and optional.
- Random seeds in code: 42.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `d47885d153ecb7cb0cd67cff32f8663a2cf77665ba5e5c3c64cb5059be6e5996` (MD5 `582313ffe1f86ea80befb340a7f048d7`)
- SHA-256 of the distribution file (with header and docstrings): `db059e1ae7047eca8e236c5ca2637257ba3deea39b70169d13ae03926bc39793`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- none
