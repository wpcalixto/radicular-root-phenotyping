# estilo_figuras.py

**Title:** Figure style module  
**File:** `scripts/estilo_figuras.py`  
**Type:** Module  
**Version:** v1.0.0 (distribution); historical source dated 2026-08-01  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Implements the figure protocol (vector PDF, embedded fonts, English labels, colours and markers) shared by the fig_*.py scripts and switches between preview and recording mode (FIG_GRAVAR).

## 2. Methodological stage

Figures

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- printed results only

## 5. Dependencies

- matplotlib

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/estilo_figuras.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: imported by every re-executed figure script.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `f7317938ee82885495c19943b8ff7e150bbbcd96a7913c78a716efd2289e7a3e` (MD5 `f7b7ac7b7b4ece335f7a329f85ae1fe3`)
- SHA-256 of the distribution file (with header and docstrings): `cbd07d46faecb8209c7d8a14e18fc4d59515e8f15d8d3cf42e22bac8286daf25`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- none
