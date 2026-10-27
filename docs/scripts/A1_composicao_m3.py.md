# A1_composicao_m3.py

**Title:** Composition of M3  
**File:** `scripts/A1_composicao_m3.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Decomposes each final M3 mask into M1-exclusive, M2-exclusive and common fractions and relates composition to quality-score differences and M3 issue flags.

## 2. Methodological stage

A1 Composition

## 3. Inputs

- `metricas/08D_selecao_por_imagem.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/notas_recebidas` (Dataset: `annotations/blind_assessment/assessor_sheets`)
- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)
- `saidas/06C_inferencia/masks` (Dataset: `masks/m2_unet`)
- `saidas/07_frangi/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_combinado_limpo/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A1_composicao_m3.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- numpy
- openpyxl
- scipy
- skimage
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A1_composicao_m3.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `ae5e43373b4b9c4ea564f172fc7394574c0ba02f7960723c5274ae52adda4fd8` (MD5 `e97c792b228b99b8bca4073b94e795ea`)
- SHA-256 of the distribution file (with header and docstrings): `f39a47421d3005215b6a626f8541185f5b728b90608114b6b508770946228a7b`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/assessor_sheets`
- `annotations/blind_assessment/review_key.csv`
- `masks/m2_unet`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
