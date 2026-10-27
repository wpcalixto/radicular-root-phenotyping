# modelagem_incerteza.py

**Title:** Uncertainty of modelling and ablation  
**File:** `scripts/modelagem_incerteza.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes rhizotron-level bootstrap intervals for configuration MAEs and MAE differences and jackknife influence by rhizotron.

## 2. Methodological stage

13 Modelling

## 3. Inputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/model_uncertainty.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- sklearn
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/modelagem_incerteza.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S20

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `24c8bea0aa28e049738042be8ba734e05a345018dd9c2a0577d33f1760f95e9e` (MD5 `2f248ac499e9b4ab5440f3fca1ebc70b`)
- SHA-256 of the distribution file (with header and docstrings): `7777c5befd677831d72f2ecc563611751bb1d48720cbce8e84a145a92dd82a7d`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
