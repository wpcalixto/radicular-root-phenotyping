# A16_ic_optico_eletrico.py

**Title:** Intervals for optical-electrical association  
**File:** `scripts/A16_ic_optico_eletrico.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes rhizotron-bootstrap intervals for the trajectory correlations and slopes linking apparent conductivity and optical descriptors.

## 2. Methodological stage

A16 Intervals

## 3. Inputs

- `metricas/electrical_features_by_rhizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_features_by_image.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A16_ic_optico_eletrico.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- scipy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A16_ic_optico_eletrico.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 10

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `5d20b9d48291390b3896ceb50d520db29273886cbfa15350c402853b7c8471bd` (MD5 `dd7e723ea2aa903ddd2de7d278d06d3b`)
- SHA-256 of the distribution file (with header and docstrings): `ba4c02647b11820975eaf5215f03dce58df90097624edfab452c7cc31802b46f`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
