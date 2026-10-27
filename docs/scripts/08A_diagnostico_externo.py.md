# 08A_diagnostico_externo.py

**Title:** Diagnostic metrics of the external model on PRMI test  
**File:** `scripts/08A_diagnostico_externo.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Evaluates the development U-Net once on the PRMI test subset and reports micro and macro Dice, IoU, precision, recall, specificity, FPR and FNR.

## 2. Methodological stage

08A External diagnostic

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- `{DRIVE_PRMI}/modelos_06B/external_diagnostic_metrics.csv` (Dataset: `tabular_data/non_regenerable_results/external_diagnostic_metrics.csv`)

## 5. Dependencies

- albumentations
- cv2
- numpy
- segmentation_models_pytorch
- torch

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/08A_diagnostico_externo.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S7

## 9. Limitations and reproduction conditions

- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Contains instructions referring to Google Drive/Colab/rclone storage used during the original execution; these are historical and optional.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `d0a8395d94968a0c76975ad881079a9511252eead65cb3bad1c8c65e661c31f5` (MD5 `6c813fbd208dd920261b2f9c9a50dc8a`)
- SHA-256 of the distribution file (with header and docstrings): `2faf7fd66bdfd7190634a0f2e28473765ba0e576faf0b8646292b704c23bcf51`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `tabular_data/non_regenerable_results/external_diagnostic_metrics.csv`
