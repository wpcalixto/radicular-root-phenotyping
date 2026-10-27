# 10_eletricas.py

**Title:** Electrical variables  
**File:** `scripts/10_eletricas.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Maps the Wenner spreadsheets to rhizotrons, recomputes apparent resistivity with the electrode spacing a = 0.16 m and derives apparent conductivity and standardised values per collection.

## 2. Methodological stage

10 Electrical

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- `metricas/electrical_by_treatment_dap.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/electrical_features_by_rhizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- openpyxl
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/10_eletricas.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S18

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `36280b31a25e8f52da64b253c9a042c45ae0179f7da29bbc1e84d0ee2b98eb82` (MD5 `081a208476285386138499a8bda235b5`)
- SHA-256 of the distribution file (with header and docstrings): `74852a5a04de18cf5e5b6d7468d98a8f02cef234634078d6b30ed913ee8e8ab0`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
