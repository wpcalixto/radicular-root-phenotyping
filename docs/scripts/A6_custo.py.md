# A6_custo.py

**Title:** Processing time and computational repeatability  
**File:** `scripts/A6_custo.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-14  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Times each processing stage per image using the production functions and checks repeatability of outputs by hashing.

## 2. Methodological stage

A6 Cost

## 3. Inputs

- `modelos/external_final_model_PRMI_all.pt` (Dataset: `(Software) models/external_final_model_PRMI_all.pt`)
- `saidas/05A_tratadas/_mascaras` (Dataset: `masks/reconstruction`)
- `saidas/05_registradas/**` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A6_custo.csv` (Dataset: `tabular_data/non_regenerable_results/A6_custo.csv`)
- `metricas/A6_repetibilidade.csv` (Dataset: `tabular_data/non_regenerable_results/A6_repetibilidade.csv`)

## 5. Dependencies

- cv2
- numpy
- platform
- scipy
- segmentation_models_pytorch
- torch
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A6_custo.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 14

## 9. Limitations and reproduction conditions

- Timings depend on hardware and are not expected to be reproduced exactly.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `94c780d71e1df5387fbaca3524075dc181b4627a6d56e918c798536c9b816545` (MD5 `e6a31c598eac36f9252cc055b674f19c`)
- SHA-256 of the distribution file (with header and docstrings): `6a8c91fb987d13ca250258b3c4b9eefae934110772f1f9528267e221ea30f2c2`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `(Software) models/external_final_model_PRMI_all.pt`
- `masks/reconstruction`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/A6_custo.csv`
- `tabular_data/non_regenerable_results/A6_repetibilidade.csv`
