# 12_temporal.py

**Title:** Temporal analysis  
**File:** `scripts/12_temporal.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes, per rhizotron and variable, rates between collections, relative changes, area under the curve and regression slopes against DAP, and tests treatment differences.

## 2. Methodological stage

12 Temporal

## 3. Inputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/temporal_by_rhizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/temporal_by_treatment.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/temporal_rates.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/temporal_treatment_stats.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- scipy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/12_temporal.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 9
- Table S19

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `ed26edd3a2b379ebe9050ed0084b58531e07ace472c22213f7379e4db382c8ab` (MD5 `5b079c637c02ff6087dccbe8e66d6e28`)
- SHA-256 of the distribution file (with header and docstrings): `d4b3ba07f778c244bda852d9cd3908d73b155212742c1ae5287cbc24eb54b114`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
