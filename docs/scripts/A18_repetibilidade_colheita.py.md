# A18_repetibilidade_colheita.py

**Title:** Relative consistency and harvested-root correspondence  
**File:** `scripts/A18_repetibilidade_colheita.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-09-21  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes between-collection rank consistency (Spearman, ICC(3,1)) of M3 descriptors and the correspondence of in situ descriptors and root mass with harvested projected length, with bootstrap and leave-one-out sensitivity.

## 2. Methodological stage

A18 Consistency

## 3. Inputs

- `metricas/A4_profundidade.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_targets.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_features_by_image.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_features_by_image_M1.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_features_by_image_M2.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_harvested.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A18_insitu_colheita.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A18_repetibilidade.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- scipy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A18_repetibilidade_colheita.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S17

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `5271d0a027f17e1c034bc35c9398efe584840f42de14588afe8ca8e9a23d865b` (MD5 `2d189a0ec7e150240a51fe7036b72d21`)
- SHA-256 of the distribution file (with header and docstrings): `03ba850f50d80595decbddc6c31c31e3b641c80b336b1f123bd60ed2a8615594`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
