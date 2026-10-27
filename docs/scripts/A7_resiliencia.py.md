# A7_resiliencia.py

**Title:** Stability of M3 advantage across image conditions  
**File:** `scripts/A7_resiliencia.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-14  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Contrasts M3 against M1 and M2 within image-defined strata at rhizotron level and fits mixed-effects acceptance models with method-by-condition interactions and clustered intervals.

## 2. Methodological stage

A7 Robustness

## 3. Inputs

- `metricas/image_qc.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/notas_recebidas` (Dataset: `annotations/blind_assessment/assessor_sheets`)
- `metricas/pretratamento_05A.csv` (Dataset: `tabular_data/non_regenerable_results/pretratamento_05A.csv`)
- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)
- `metricas/root_features_by_image.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A7_logistico.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A7_resiliencia.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A7_tratamento.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- openpyxl
- pandas
- scipy
- statsmodels
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A7_resiliencia.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 6
- Table S12

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed; A7_resiliencia.csv and A7_tratamento.csv byte-identical; A7_logistico.csv differs by at most 1.05e-4 (relative) in GLMM estimates, with no difference at the published precision.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `3c651532829317e7d8ee582ea89bd176281201c0e22dd7383e8401918e89d9db` (MD5 `75cb33ff0e01aa1f7aaeae36b5981b22`)
- SHA-256 of the distribution file (with header and docstrings): `891b28d3f751a5db1411483ab3a9a41f7d94abef667ea88159482428ff7755b5`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/assessor_sheets`
- `annotations/blind_assessment/review_key.csv`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/pretratamento_05A.csv`
