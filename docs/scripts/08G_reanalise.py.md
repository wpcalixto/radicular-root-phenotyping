# 08G_reanalise.py

**Title:** Rhizotron-level reanalysis and ordinal agreement  
**File:** `scripts/08G_reanalise.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Aggregates the blinded scores at rhizotron level (n=12) with paired tests and rhizotron bootstrap intervals and computes Krippendorff ordinal alpha and ICC(2,1)/ICC(3,1).

## 2. Methodological stage

08G Statistics

## 3. Inputs

- `metricas/notas_recebidas` (Dataset: `annotations/blind_assessment/assessor_sheets`)
- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)

## 4. Outputs

- `metricas/08G_reanalise.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- openpyxl
- scipy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/08G_reanalise.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S11

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `9c507b23da38c973a932731ebcdc4b6321e59b5374a10217f054d7d3e690967b` (MD5 `f3656f065d3c86ea0c2c1ffdd30d8004`)
- SHA-256 of the distribution file (with header and docstrings): `ca4bcfd4fd77e36ef9732ea6893dc1ff7ea96d40ec65410ad3a24c3c3014fce2`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/assessor_sheets`
- `annotations/blind_assessment/review_key.csv`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
