# A12b_kappa_dicotomizado.py

**Title:** Fleiss kappa for dichotomised scores  
**File:** `scripts/A12b_kappa_dicotomizado.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-08-01  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes the 95% interval of Fleiss kappa for scores dichotomised at 3 using the rhizotron-clustered resampling of A12.

## 2. Methodological stage

A12 Agreement

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- printed results only

## 5. Dependencies

- numpy

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A12b_kappa_dicotomizado.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S9

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `e55b2a1d4be81378c11ca67210e5dce50e282cac77db434b2e65cd8cc8577532` (MD5 `3a4494b9ce11b54a52ff80589a5d015c`)
- SHA-256 of the distribution file (with header and docstrings): `251eeecb67a84bfb0d4061471ebfd9bbd2761c42bc5f07b0f40b30ba9b5511b9`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- none
