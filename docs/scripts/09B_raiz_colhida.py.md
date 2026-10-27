# 09B_raiz_colhida.py

**Title:** Projected length of harvested roots  
**File:** `scripts/09B_raiz_colhida.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Segments the washed-root photographs, measures skeleton length and vertical extent in pixels and estimates the cm-per-pixel scale from the ruler by Fourier analysis, accepting units only under geometric criteria.

## 2. Methodological stage

09B Post-harvest

## 3. Inputs

- `entradas/Raizes` (Dataset: `images_raw/harvested_roots`)
- `figures/09B_raiz_colhida`

## 4. Outputs

- `metricas/root_harvested.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- PIL
- cv2
- numpy
- pillow_heif
- skimage
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/09B_raiz_colhida.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `96e2868b54e2e7cfce6f91b5832c762c308bb7b8a8dbc09de1567c11b8e0f873` (MD5 `80fc32878a642fc015a34b876e4764b7`)
- SHA-256 of the distribution file (with header and docstrings): `3993a2c6f57bf9114fc65740b4cf6fd7c3870f327bee410d43466c67e0d6d7b3`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `images_raw/harvested_roots`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
