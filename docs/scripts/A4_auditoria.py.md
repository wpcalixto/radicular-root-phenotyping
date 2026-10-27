# A4_auditoria.py

**Title:** Audit of vertical-distribution descriptors  
**File:** `scripts/A4_auditoria.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Checks redundancy among D50, D90, F_prof and B_d and the sensitivity of B_d to small mask components.

## 2. Methodological stage

A4 Audit

## 3. Inputs

- `metricas/A4_profundidade.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/05A_tratadas/_mascaras` (Dataset: `masks/reconstruction`)
- `saidas/08_combinado_limpo/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- printed results only

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
python scripts/A4_auditoria.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `d2b2f78d32610024096d65e354b1d81d79f94261431f669c383508795d630093` (MD5 `80faff12808617cb7d23388b54c00d7c`)
- SHA-256 of the distribution file (with header and docstrings): `7bb57a9167c63c98fdbd4f45bcf4760b9ce52f36c0cf76e13f7e7426d2c7e644`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `masks/reconstruction`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
