# A17_associacoes_complementares.py

**Title:** Complementary associations  
**File:** `scripts/A17_associacoes_complementares.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Tests in situ occupancy versus final root mass and conditioning cost versus intervention complexity with Spearman correlations and bootstrap intervals.

## 2. Methodological stage

A17 Associations

## 3. Inputs

- `metricas/A6_custo.csv` (Dataset: `tabular_data/non_regenerable_results/A6_custo.csv`)
- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_targets.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A17_associacoes.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- scipy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A17_associacoes_complementares.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `2718f495042ad3bdc92d159f1341186cddc59a32810b3bac6211284ba43b92ae` (MD5 `eea6876fa97a75a2ce26cf1456808184`)
- SHA-256 of the distribution file (with header and docstrings): `a972435fecb3567d9594230ef3ae51f37747db4454a407731b8bf4da4d6a4bc9`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/A6_custo.csv`
