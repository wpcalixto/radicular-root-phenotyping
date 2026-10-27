# A2_optico_eletrico.py

**Title:** Optical-electrical longitudinal association  
**File:** `scripts/A2_optico_eletrico.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Tests contemporaneous and lagged associations between changes in apparent conductivity and optical descriptors with mixed models and repeated-measures correlation, and writes per-rhizotron slopes.

## 2. Methodological stage

A2 Association

## 3. Inputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A2_optico_eletrico.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A2_slopes_by_rizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- pandas
- scipy
- statsmodels
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A2_optico_eletrico.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 10

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `82ad95222ad8817aff2a44a29963db12272832a2fb8f144481d25d5c5f0abdd5` (MD5 `5d2200ffd6e69fab34a06c11ef1dc0fc`)
- SHA-256 of the distribution file (with header and docstrings): `2feb0d936e35b46413402303e1cb71347cecfbac39505f73783dbacb647f15a7`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
