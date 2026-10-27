# fig_horizonte_trat.py

**Title:** Figure: horizon ratio to treatment reference  
**File:** `scripts/fig_horizonte_trat.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws the MAE ratio to the treatment reference by horizon for root and shoot mass (17_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `17_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `17_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `17_figura_resultado_legenda.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A3_horizonte.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- printed results only

## 5. Dependencies

- matplotlib
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_horizonte_trat.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 13

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `4c7f8ec390fd97f25b75063c27c177edb40986e8c8efc40e8e5a01e4cbbbc258` (MD5 `75355e818bd668a83d0bfb87a23c0926`)
- SHA-256 of the distribution file (with header and docstrings): `c7ec43ad262b38deac9b684cf0a9144f4f263ee089de4f56c472bb73215f1a8c`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
