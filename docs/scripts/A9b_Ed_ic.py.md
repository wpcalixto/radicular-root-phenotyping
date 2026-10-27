# A9b_Ed_ic.py

**Title:** Intervals for spatial enrichment E_d  
**File:** `scripts/A9b_Ed_ic.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-08-01  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes rhizotron-clustered bootstrap intervals of the median spatial enrichment E_d per method and distance band.

## 2. Methodological stage

A9 Ablation

## 3. Inputs

- `metricas/A9_ablacao.csv` (Dataset: `tabular_data/non_regenerable_results/A9_ablacao.csv`)

## 4. Outputs

- `metricas/A9b_Ed_ic.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 5000.

## 7. Execution

```bash
python scripts/A9b_Ed_ic.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S5

## 9. Limitations and reproduction conditions

- Random seeds in code: 5000.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `ded688f7cb98a312e559b629eda55b73dd89e474fa098ca80184a7fb36003cf3` (MD5 `a4e880722aecb8f3b1772d1b0027926c`)
- SHA-256 of the distribution file (with header and docstrings): `1fec30b2c7325728ce2e21aa26e092489102b26f5814f3e292027585f9f1a45b`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/A9_ablacao.csv`
