# config.py

**Title:** Central configuration  
**File:** `scripts/config.py`  
**Type:** Module  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Defines the relative directory tree, experimental constants (sowing date, rhizotrons, collections, Wenner spacing) and processing parameters imported by all scripts.

## 2. Methodological stage

Configuration

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- printed results only

## 5. Dependencies

- Python standard library only

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/config.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: imported by every re-executed script.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `d019a467df854318592edf9ff8053bd8f11a0c7a7d4bad93976123f1b0d31bc6` (MD5 `ebf1bca5d4a0758c3e971d592592cb5e`)
- SHA-256 of the distribution file (with header and docstrings): `be3ad9b9f9fee3e8c9ccf375cb5192503d98f89093f96d7185a3d1f022137114`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- none
