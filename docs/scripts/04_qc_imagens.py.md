# 04_qc_imagens.py

**Title:** Image quality control and central glare  
**File:** `scripts/04_qc_imagens.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-06  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes, on normalised luminance, brightness, contrast, sharpness (Laplacian variance), global over- and under-exposure and central glare indices (G_c, R_c, glare class) for every converted image; no correction is applied.

## 2. Methodological stage

04 Quality control

## 3. Inputs

- `saidas/03_convertidas` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `manifestos/03_conversao.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/image_qc.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- PIL
- numpy
- skimage
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/04_qc_imagens.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S4

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `778ac38f0fbf55d258d83c6b545263fc51508e1dad0124d7bccaefe15d3a2e09` (MD5 `c047af63931004b2213382ae92717b0e`)
- SHA-256 of the distribution file (with header and docstrings): `1282b42412bcdaf17bd4f185daae0586c7c4b13a82f90f78144ba1734e0be30d`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
