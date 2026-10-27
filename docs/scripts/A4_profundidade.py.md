# A4_profundidade.py

**Title:** Vertical-distribution descriptors  
**File:** `scripts/A4_profundidade.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes D50, D90, deep-region fraction and branching density from the final M3 masks excluding reconstructed pixels.

## 2. Methodological stage

A4 Descriptors

## 3. Inputs

- `metricas/root_features_by_image.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/05A_tratadas/_mascaras` (Dataset: `masks/reconstruction`)
- `saidas/08_combinado_limpo/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A4_profundidade.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A4_profundidade.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S16

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `0be82a9ca6021636c875754dcb64c2f65de410b5bffc4e1390c84031a873be0c` (MD5 `57d50ab45b221eaa8a5cbdb5285f85fb`)
- SHA-256 of the distribution file (with header and docstrings): `50727a76b9cb79b760ae25e7c8c309993bb14294db2495da36f1c748ad9ae247`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `masks/reconstruction`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
