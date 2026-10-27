# run_A15_pad010.py

**Title:** A15 with approved padding  
**File:** `scripts/auxiliary/run_A15_pad010.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-10-25  
**Status:** Auxiliary script of the manuscript preparation (Phase 20 / Order 22).

## 1. Scientific purpose

Runs A15_ampliacoes.py restoring savefig.pad_inches = 0.10, the configuration of the approved 21_figura_resultado PDFs (Order 20-H).

## 2. Methodological stage

Phase 20-H auxiliary

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- printed results only

## 5. Dependencies

- matplotlib
- runpy
- local modules: estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/auxiliary/run_A15_pad010.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S13

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `0c7693f0b1d6f294e010a2e7628f59246ee8b53a280e3faecd653ae5e056655c` (MD5 `429704045d242e84d9d20aa2beb5d04c`)
- SHA-256 of the distribution file (with header and docstrings): `9a94407a5728c6bc029c767839b7d059217f99a9bd839151950fc6a144023dd1`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: records of the manuscript preparation (ETAPA4_CONGELADA_2026-10-26 / Order 22 working area)

## 11. Dataset references

- none
