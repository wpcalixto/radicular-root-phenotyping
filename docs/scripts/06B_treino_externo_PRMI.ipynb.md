# 06B_treino_externo_PRMI.ipynb

**Title:** U-Net training on PRMI (Colab notebook)  
**File:** `scripts/06B_treino_externo_PRMI.ipynb`  
**Type:** Jupyter notebook  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Colab notebook paired with 06B_treino_externo_PRMI.py; installs segmentation-models-pytorch 0.3.4 and albumentations 1.4.0 and trains the U-Net on PRMI. The archived version declares 40 epochs; the executed run used 25.

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
Open in Jupyter or Google Colab and run the cells in order.
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- The archived configuration declares 40 epochs (epochs_dev = epochs_final = 40); the weights used in the study were produced by a 25-epoch execution on 2026-07-06 whose script version was not preserved. See docs/06B_training_provenance.md.
- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Contains instructions referring to Google Drive/Colab/rclone storage used during the original execution; these are historical and optional.
- Random seeds in code: 42.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `9f4bee5b9c21cf497e95314cee7bf896f12b3c07e38a3fe8c0448228d53e16bb` (MD5 `fae1aa956990639b787d3cb9dc4a64ae`)
- SHA-256 of the distribution file (with header and docstrings): `6f1e35a495421a05498439cf1c26712865802078d80c4d1f16cbb4a4451cf7ac`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- none
