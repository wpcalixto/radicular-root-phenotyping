# A2_auditoria.py

**Title:** Rigour audits of optical-electrical analyses  
**File:** `scripts/A2_auditoria.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-13  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Runs increment analyses with rhizotron bootstrap, trajectory tests with blocked permutation and Holm correction, and intra-rhizotron level models.

## 2. Methodological stage

A2 Audit

## 3. Inputs

- `metricas/multimodal_long.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- printed results only

## 5. Dependencies

- numpy
- pandas
- scipy
- statsmodels
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A2_auditoria.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed without error (printed results only).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `7f14f6c7394f72100b0794d98934b1337b07793724fe3cc8f0e35914acce2561` (MD5 `6d08725c63328e9e9e9dd09c8bdc99bf`)
- SHA-256 of the distribution file (with header and docstrings): `1c63d0c97b141ee65b69a29e4683c7dc2e5c9b74efb577c39ddaf317e914978e`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
