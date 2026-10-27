# 08F_estatistica.py

**Title:** Statistical comparison of methods  
**File:** `scripts/08F_estatistica.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Tests differences in quality score (Friedman, Kendall W, paired Wilcoxon with Holm correction) and acceptance between methods over the repeated-measures design of the blinded assessment.

## 2. Methodological stage

08F Statistics

## 3. Inputs

- `figures/08_estatistica`
- `metricas/notas_recebidas/*.xlsx` (Dataset: `annotations/blind_assessment/assessor_sheets/*.xlsx`)
- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)

## 4. Outputs

- `figures/08_estatistica/boxplot_Q.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/08F_estatistica.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- matplotlib
- numpy
- scipy
- statsmodels
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 0.

## 7. Execution

```bash
python scripts/08F_estatistica.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 4

## 9. Limitations and reproduction conditions

- Random seeds in code: 0.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `b484acf6c649cf5117e608b26c21bb4737f7544030fd5eedd59ffaf5c6e8e27a` (MD5 `939edb8fbbc9f982616f6daf4cead0f6`)
- SHA-256 of the distribution file (with header and docstrings): `c6c009c8b56911580afa1cc60c3b1d631ae8177458a6c0daa4e852bcef231382`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/assessor_sheets/*.xlsx`
- `annotations/blind_assessment/review_key.csv`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
