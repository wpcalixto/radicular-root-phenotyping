# A14_sensibilidade_segmentador.py

**Title:** Sensitivity to the segmenter  
**File:** `scripts/A14_sensibilidade_segmentador.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Extracts the same descriptors from M1, M2 and M3 and repeats the temporal and treatment analyses to separate root properties from mask properties.

## 2. Methodological stage

A14 Sensitivity

## 3. Inputs

- `metricas/electrical_features_by_rhizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_targets.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A14_sensibilidade_segmentador.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- scipy
- sklearn
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A14_sensibilidade_segmentador.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 13
- Tabela 8

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `a92846bede9d61ed7da41e9ceda721ae9da675c545150701d38f6971628c7592` (MD5 `1bca4dc875615d97c794f895e30a4779`)
- SHA-256 of the distribution file (with header and docstrings): `4f8a13f6fdcaaf7e2c2706aa96a5ff8640d0f444b9fb6e00e7c3033ed7836a71`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
