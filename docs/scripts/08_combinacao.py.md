# 08_combinacao.py

**Title:** Union of M1 and M2  
**File:** `scripts/08_combinacao.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-07  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Forms the union of M1 and M2 masks (M1 already without components below the minimum area) as the unrefined combined mask.

## 2. Methodological stage

08 Fusion

## 3. Inputs

- `saidas/06C_inferencia/masks` (Dataset: `masks/m2_unet`)
- `saidas/07_frangi/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/combinado_parameters.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_combinado/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_combinado/masks/<data>/<id>.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/08_combinacao.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `b7b16616a840a28ff129dfaa79d927530d31c6c8b25cfa9cc20dc69e2499d8b8` (MD5 `6c4ec6a7797901591e1a8cca7e26c04a`)
- SHA-256 of the distribution file (with header and docstrings): `e955626ff989c999812b04b785d5ff0b8daff68469f22b20b1f66a4a2088d1f0`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `masks/m2_unet`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
