# 11_integracao.py

**Title:** Multimodal integration  
**File:** `scripts/11_integracao.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Joins image descriptors, electrical variables, management, chronology and final outcomes (air-dry shoot and root mass from Massa_full.xlsx and their ratio) by rhizotron and collection.

## 2. Methodological stage

11 Integration

## 3. Inputs

- `metricas/electrical_features_by_rhizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_features_by_image.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/root_harvested.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `tabdatas/Massa_full.xlsx` (Dataset: `tabular_data/biomass/Massa_full.xlsx`)

## 4. Outputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_targets.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_wide.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- openpyxl
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/11_integracao.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S18

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `e7af5b5408586774cdeab6a89466d444993ad50ccf3a8797a73aa24a99582415` (MD5 `f2b1161c31356702d67e04d904e89ae8`)
- SHA-256 of the distribution file (with header and docstrings): `d96d1c099397dc5d05984510fed30434f37fe38d43470c08a037a9dd39c9e488`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/biomass/Massa_full.xlsx`
