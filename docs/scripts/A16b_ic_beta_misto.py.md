# A16b_ic_beta_misto.py

**Title:** Interval for the mixed-model beta  
**File:** `scripts/A16b_ic_beta_misto.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes the rhizotron-clustered bootstrap interval of the standardised beta of the A2.3 mixed model.

## 2. Methodological stage

A16 Intervals

## 3. Inputs

- `metricas/A16_ic_beta_misto.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- printed results only

## 5. Dependencies

- numpy
- pandas
- statsmodels
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A16b_ic_beta_misto.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 10

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `836f5e0e7e31a3cf72529a080ea2724d1fa2c87cbb064be16a3e79762e70fb03` (MD5 `7dcce6dbd42b9b3389f7234df86dca63`)
- SHA-256 of the distribution file (with header and docstrings): `45021c3ac91cded81e63174913685b6f2ce836098f06ac1db339e02820fc3abe`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
