# A3_baselines.py

**Title:** Treatment-dependent baselines  
**File:** `scripts/A3_baselines.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Compares seven predictive configurations against treatment-conditioned references by leave-one-rhizotron-out validation with paired rhizotron-level differences and bootstrap intervals.

## 2. Methodological stage

A3 Baselines

## 3. Inputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/A3_baselines.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- scipy
- sklearn
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A3_baselines.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 11

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `eea0e7ab29637319ce0c50df723d0821953b50ce9742bda50bbfe6773476aa15` (MD5 `347c9841631a15addf29d9525adf48ed`)
- SHA-256 of the distribution file (with header and docstrings): `fedc28c27f5fed51b65b8cc913c11d0d55ce19598089ba5ba392236cc2bb98d2`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
