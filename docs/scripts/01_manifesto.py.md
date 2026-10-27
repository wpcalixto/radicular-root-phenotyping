# 01_manifesto.py

**Title:** Master dataset manifest  
**File:** `scripts/01_manifesto.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-06  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Builds the master manifest with one row per rhizotron (R01-R12) and collection, linking each observation to treatment, replicate, date, DAP, image path and electrical files, with image, electrical and joint availability flags.

## 2. Methodological stage

01 Manifest

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- `manifestos/dataset_manifest.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/01_manifesto.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `8772d603f3457384862ea7b72b6ebea621de342af3a37f4e6a6a32b24457ec0f` (MD5 `77ce2e37fca54bbc806f72edcc71abf2`)
- SHA-256 of the distribution file (with header and docstrings): `a2f05affba2aa3aa55083eb46e36bb53ab894982e2c2f8fbb15c3aaf867051f0`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
