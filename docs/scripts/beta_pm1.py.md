# beta_pm1.py

**Title:** Regression of M3 score on Frangi share and DAP  
**File:** `scripts/auxiliary/beta_pm1.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-10-25  
**Status:** Auxiliary script of the manuscript preparation (Phase 20 / Order 22).

## 1. Scientific purpose

Fits Q_M3 ~ P_M1 + DAP by least squares with rhizotron bootstrap intervals (beta_PM1 = -1.09 [-2.04; -0.10]) from A1_composicao_m3.csv and 08D_selecao_por_imagem.csv.

## 2. Methodological stage

Phase 20-F auxiliary

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- printed results only

## 5. Dependencies

- numpy
- pandas

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/auxiliary/beta_pm1.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Random seeds in code: 42.
- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `0791c3b20bb0c72a905a3b111599d8cc833ccc80288c6b92728e5d83b3524840` (MD5 `f7d1b1668c54618f891641aa0d77c904`)
- SHA-256 of the distribution file (with header and docstrings): `b906a2359b4e04d7a2f61c17d80dc2c5e2988cf8947c8948aa0e458b1c772ed4`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: records of the manuscript preparation (ETAPA4_CONGELADA_2026-10-26 / Order 22 working area)

## 11. Dataset references

- none
