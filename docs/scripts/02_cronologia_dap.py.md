# 02_cronologia_dap.py

**Title:** Chronology and days after planting  
**File:** `scripts/02_cronologia_dap.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-06  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Validates the experimental chronology using the sowing date as time zero; computes DAP, the interval between consecutive collections and its deviation from 7 days, and checks fertilisation timing.

## 2. Methodological stage

02 Chronology

## 3. Inputs

- `config/cronograma_experimento.csv` (Dataset: `(Software) config/cronograma_experimento.csv`)

## 4. Outputs

- `config/cronologia_dap.csv` (Dataset: `(Software) config/cronologia_dap.csv`)

## 5. Dependencies

- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/02_cronologia_dap.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 2

## 9. Limitations and reproduction conditions

- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `2350355e4c0f4b6b0a282f32252a5aa844e1bf139725abae3139c634b7baccc2` (MD5 `abb1563373858950dd6d9146c01eac01`)
- SHA-256 of the distribution file (with header and docstrings): `177e75872c3bcb026350410c1804e6b75687e312a343e162ba18de439c9a5cd8`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `(Software) config/cronograma_experimento.csv`
- `(Software) config/cronologia_dap.csv`
