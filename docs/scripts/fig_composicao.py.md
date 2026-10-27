# fig_composicao.py

**Title:** Figure: M3 composition  
**File:** `scripts/fig_composicao.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws M3 composition per image and the gain of M3 versus the Frangi-exclusive fraction (15_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `metricas/A1_composicao_m3.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A1_composicao_m3.csv.` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `15_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `15_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- matplotlib
- numpy
- scipy
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_composicao.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 8

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `928a9745ebafbe6c9839e964cf8f53878cbfb5e91938964fc0d898dc8f0da9ee` (MD5 `5ed9b8e1310dac5a61c6e7634fbc1df8`)
- SHA-256 of the distribution file (with header and docstrings): `1214a8012bf8914dff459ca076f37f0324020d2591f2656cfb8855c3687698c5`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
