# 09_descritores.py

**Title:** Morphological descriptors per image  
**File:** `scripts/09_descritores.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Extracts pixel-based root descriptors (area, occupancy, skeleton length, branch nodes, depth distribution) from the final M3 masks, excluding reconstructed pixels from numerator and denominator; also for M1 and M2.

## 2. Methodological stage

09 Descriptors

## 3. Inputs

- `saidas/05A_tratadas/_mascaras` (Dataset: `masks/reconstruction`)
- `saidas/06C_inferencia/masks` (Dataset: `masks/m2_unet`)
- `saidas/07_frangi/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_combinado_limpo/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/root_density_by_layer.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_features_by_image.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_features_by_treatment_dap.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- numpy
- scipy
- skimage
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/09_descritores.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S16

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `9ab87c495ef617a53adf903e4bf9c272264aecf4bb0717577769af2835a8b7d4` (MD5 `cdeed5c7fd45594d7c8c5737831a42b7`)
- SHA-256 of the distribution file (with header and docstrings): `952e198fb1d29c19397865a9719e645670930e0c4e3866c532c19cff5a6068dd`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `masks/m2_unet`
- `masks/reconstruction`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
