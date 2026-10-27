# 08B_pacote_cego.py

**Title:** Blinded assessment package (M3 final)  
**File:** `scripts/08B_pacote_cego.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Generates anonymised overlays of M1, M2 and final M3 on each conditioned image with a fixed-seed random code assignment, the answer key and the score sheet used by the assessors.

## 2. Methodological stage

08B Blinded assessment

## 3. Inputs

- `saidas/05A_tratadas` (Dataset: `images_processed/conditioned`)
- `saidas/06C_inferencia/masks` (Dataset: `masks/m2_unet`)
- `saidas/07_frangi/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_combinado_limpo/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/review_image_set.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)
- `metricas/review_score_sheet.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_avaliacao/review_package` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_avaliacao/review_package/<image_id>__<codigo>.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- skimage
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/08B_pacote_cego.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Contains instructions referring to Google Drive/Colab/rclone storage used during the original execution; these are historical and optional.
- Random seeds in code: 42.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `2e7c2fdcb933f240811db1777d97e4c28771fa4fba93456f5db477478854faa9` (MD5 `48b36577ed2b32ef4ea19cc41cdaf8a4`)
- SHA-256 of the distribution file (with header and docstrings): `8d4ba5f9fa40b3d77ef5617b4e71f073e103d391cd4e94e30f96ea5f2000f023`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/review_key.csv`
- `images_processed/conditioned`
- `masks/m2_unet`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
