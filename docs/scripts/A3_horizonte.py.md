# A3_horizonte.py

**Title:** Horizon performance relative to treatment reference  
**File:** `scripts/A3_horizonte.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes, for horizons 1-6, the ratio between model MAE and the treatment-reference MAE for optical, electrical, combined and full configurations.

## 2. Methodological stage

A3 Baselines

## 3. Inputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A3_horizonte.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- sklearn
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A3_horizonte.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `18a02d5fd31c1ff6557d51f227ab210a9a52609359f6566e5563f36ed2020956` (MD5 `3b941e36cf63ee38d80bb9a0baa98f29`)
- SHA-256 of the distribution file (with header and docstrings): `f64de356acc34dd4eaf1969c9171f8cc4a78f0af4f73e5c92db92b264c46bfd8`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
