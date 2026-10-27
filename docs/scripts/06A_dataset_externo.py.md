# 06A_dataset_externo.py

**Title:** External PRMI dataset indexing  
**File:** `scripts/06A_dataset_externo.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-06  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Records the source, integrity (MD5) and licence of the external PRMI archive and rebuilds the image-mask-species-split index and the split file from the archive listing.

## 2. Methodological stage

06A External data

## 3. Inputs

- `manifestos/external_dataset_index.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `manifestos/external_split.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `external_dataset_license.txt`
- `manifestos/prmi_ziplist.txt` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/06A_dataset_externo.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Contains instructions referring to Google Drive/Colab/rclone storage used during the original execution; these are historical and optional.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `56462c498ed03993a1cce16ce030a0dd7acb394d28dec96a9b0163d6c0c3d4a5` (MD5 `02db2649ee7e820b47dc80e747c8705f`)
- SHA-256 of the distribution file (with header and docstrings): `d2b8400092062394147184190fa6ca879d72aea72a41557f9ebfb163137b5f55`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
