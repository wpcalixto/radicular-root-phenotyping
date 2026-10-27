# 03_conversao_heic.py

**Title:** HEIC to PNG conversion  
**File:** `scripts/03_conversao_heic.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Converts the in situ HEIC images to lossless PNG at full resolution, applying the EXIF orientation and logging the original orientation for audit.

## 2. Methodological stage

03 Conversion

## 3. Inputs

- `entradas/<data_coleta>/R##_<data>.heic` (Dataset: `images_raw/in_situ_rgb/<data_coleta>/R##_<data>.heic`)

## 4. Outputs

- `manifestos/03_conversao.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/03_convertidas` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/03_convertidas/<data>/R##_<data>.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- PIL
- pillow_heif
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/03_conversao_heic.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `9dd10442d97ffa28c596eb4a09a7fbd4be233b91041f730ff35b9e95bbbd4a00` (MD5 `6d2f98dd35e3aefd0a007aa1d4f5d93f`)
- SHA-256 of the distribution file (with header and docstrings): `611814b39e106ec66ecb375ac0d217950ea34376b30186edd407c544ff9e7f2d`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `images_raw/in_situ_rgb/<data_coleta>/R##_<data>.heic`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
