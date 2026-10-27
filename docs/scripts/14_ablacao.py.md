# 14_ablacao.py

**Title:** Ablation studies  
**File:** `scripts/14_ablacao.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Quantifies the contribution of modalities, morphological groups and collections by controlled removal and comparison of leave-one-rhizotron-out MAE against the full Ridge model.

## 2. Methodological stage

14 Ablation

## 3. Inputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/ablation_collection.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/ablation_fusion.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/ablation_group.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/ablation_modality.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- sklearn
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/14_ablacao.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 12
- Table S21
- Table S23

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `22db0ebc0d9feec94571d766f5b494ddf726882ba011b5b2c07d59c7e402abaf` (MD5 `078cb6c0ac0b035ca3a30ab986066cb4`)
- SHA-256 of the distribution file (with header and docstrings): `c49e55be8239c57eff642b70fd4fc88819e106522e5f501c6a3980ea4eb6c9ac`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
