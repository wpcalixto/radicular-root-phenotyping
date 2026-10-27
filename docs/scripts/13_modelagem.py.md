# 13_modelagem.py

**Title:** Predictive modelling of final outcomes  
**File:** `scripts/13_modelagem.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Predicts final root and shoot mass and their ratio from features accumulated up to each horizon with leave-one-rhizotron-out validation for Ridge, Lasso, PLS, Random Forest, SVR and mean baselines.

## 2. Methodological stage

13 Modelling

## 3. Inputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/model_horizon.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/model_performance.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/model_predictions.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- sklearn
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/13_modelagem.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S22

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `2c53ed9e6cde31e79e223fb1b21e303d1f5d980dc5be3037eb39b5c73e1c7fe5` (MD5 `c6b4b1b334077f048f2f06b773de101d`)
- SHA-256 of the distribution file (with header and docstrings): `f10ed96b44f1b7fa8fdbebc9c048fb7197b6ee185d732004164f1e4a1c919891`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
