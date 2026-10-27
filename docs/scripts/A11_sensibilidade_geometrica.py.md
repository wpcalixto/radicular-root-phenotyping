# A11_sensibilidade_geometrica.py

**Title:** Geometric sensitivity of descriptors  
**File:** `scripts/A11_sensibilidade_geometrica.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-30  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Re-runs the full segmentation chain on images subjected to six small affine perturbations (translation, scale, rotation) and reports signed and absolute relative descriptor changes and rank correlations.

## 2. Methodological stage

A11 Sensitivity

## 3. Inputs

- `modelos/external_final_model_PRMI_all.pt` (Dataset: `(Software) models/external_final_model_PRMI_all.pt`)
- `saidas/05A_tratadas` (Dataset: `images_processed/conditioned`)

## 4. Outputs

- `metricas/A11_sensibilidade_geometrica.csv` (Dataset: `tabular_data/non_regenerable_results/A11_sensibilidade_geometrica.csv`)
- `metricas/A11_sensibilidade_resumo.csv` (Dataset: `tabular_data/non_regenerable_results/A11_sensibilidade_resumo.csv`)

## 5. Dependencies

- cv2
- numpy
- scipy
- segmentation_models_pytorch
- skimage
- torch
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A11_sensibilidade_geometrica.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S15

## 9. Limitations and reproduction conditions

- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `61d730227a4597c493fd9910381c30cad1b2b5d78a8cc64cb6b1739519a3414b` (MD5 `2bc0df479fdd6ce82542694f0d3a5400`)
- SHA-256 of the distribution file (with header and docstrings): `e2f31aab15fe5d4f34f6a950fe158c0fdf4344c75e60df44b2bde0a7c9864313`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `(Software) models/external_final_model_PRMI_all.pt`
- `images_processed/conditioned`
- `tabular_data/non_regenerable_results/A11_sensibilidade_geometrica.csv`
- `tabular_data/non_regenerable_results/A11_sensibilidade_resumo.csv`
