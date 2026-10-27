# 15_explicabilidade.py

**Title:** Permutation importance and model summary  
**File:** `scripts/15_explicabilidade.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes signed permutation importance by variable and joint permutation by source in the full Ridge model, coherence summaries and copies model_performance.csv to model_comparison.csv.

## 2. Methodological stage

15 Explainability

## 3. Inputs

- `metricas/ablation_group.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/explainability_by_group.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/explainability_coherence.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/explainability_results.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/model_comparison.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/model_performance.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/model_predictions.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/predictions_by_rhizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- scipy
- sklearn
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/15_explicabilidade.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S22
- Table S24

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `79b172e13a9e376826ead6b4bab466f3b17473eb47ed18e23c8fc05d60c92bcc` (MD5 `555786eb6bb48ef376ac723f763a095a`)
- SHA-256 of the distribution file (with header and docstrings): `5c110c1c49fba594a851ba3cbc151d0fdb1fcb4db6fbbe68cae5502fbcc5ca3f`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
