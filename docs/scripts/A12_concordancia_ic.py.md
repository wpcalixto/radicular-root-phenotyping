# A12_concordancia_ic.py

**Title:** Agreement coefficients with intervals  
**File:** `scripts/A12_concordancia_ic.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-30  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Computes Fleiss kappa, Krippendorff ordinal alpha, ICC(2,1) and ICC(3,1) with rhizotron-level bootstrap confidence intervals.

## 2. Methodological stage

A12 Agreement

## 3. Inputs

- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)

## 4. Outputs

- `metricas/A12_concordancia_ic.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A12_concordancia_ic.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S9

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `16979e54b72bf4bf5320f89552a1f264eec815730e45aec7e21c11f7f67756c3` (MD5 `d0b3f9988ff34e901bdea795401fb66f`)
- SHA-256 of the distribution file (with header and docstrings): `1ac55442b797eabb049fe7bd944d6920544cbdc38a5e934b3c9283016ec49fa7`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/review_key.csv`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
