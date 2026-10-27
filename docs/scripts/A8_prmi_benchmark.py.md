# A8_prmi_benchmark.py

**Title:** M1/M2/M3 benchmark on PRMI test  
**File:** `scripts/A8_prmi_benchmark.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-14  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Applies M1, the development U-Net (M2) and M3 to the PRMI test split and measures pixel, centreline and skeleton metrics against ground truth.

## 2. Methodological stage

A8 Benchmark

## 3. Inputs

- `modelos/external_development_model.pt` (Dataset: `(Software) models/external_development_model.pt`)

## 4. Outputs

- `A8_prmi_por_imagem.csv` (Dataset: `tabular_data/non_regenerable_results/A8_prmi_por_imagem.csv`)
- `A8_prmi_shard_I.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

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
python scripts/A8_prmi_benchmark.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 7
- Table S6

## 9. Limitations and reproduction conditions

- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `80baa4f7dc51014c4b61fe349165025ac02d18cd55eef44317b2abc1ff00edad` (MD5 `ed20de496a66e64e18bb98c3716d6559`)
- SHA-256 of the distribution file (with header and docstrings): `b95d779400b67c08243ec42db4f482fa4d2e0d22fb3f12472b38671b9af2af45`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `(Software) models/external_development_model.pt`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/A8_prmi_por_imagem.csv`
