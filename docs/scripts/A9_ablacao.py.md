# A9_ablacao.py

**Title:** Reflection-treatment ablation  
**File:** `scripts/A9_ablacao.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-14  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Runs M1, M2 and M3 on original and reconstructed images and compares masks only in genuinely unchanged areas, reporting Jaccard, Dice, descriptor changes and spatial enrichment E_d.

## 2. Methodological stage

A9 Ablation

## 3. Inputs

- `modelos/external_final_model_PRMI_all.pt` (Dataset: `(Software) models/external_final_model_PRMI_all.pt`)
- `saidas/05A_tratadas` (Dataset: `images_processed/conditioned`)
- `saidas/05_registradas` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A9_ablacao.csv` (Dataset: `tabular_data/non_regenerable_results/A9_ablacao.csv`)

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
python scripts/A9_ablacao.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 3

## 9. Limitations and reproduction conditions

- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `cdd58e189a3c8f3ca488fc0a759688ab8b0da56dbe58daf90d3eb6ce848755ad` (MD5 `93d907c7dbc98d170cdbf141c717cc15`)
- SHA-256 of the distribution file (with header and docstrings): `0db2f975b8c335504613e1bfedeafa174a87f726e45743e5d4a7c3cb3daed9c7`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `(Software) models/external_final_model_PRMI_all.pt`
- `images_processed/conditioned`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/A9_ablacao.csv`
