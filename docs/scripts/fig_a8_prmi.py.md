# fig_a8_prmi.py

**Title:** Figure: PRMI paired differences  
**File:** `scripts/fig_a8_prmi.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws the forest plot of M3-M2 and M3-M1 differences on the PRMI test (20_figura_resultado.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `metricas/A8_prmi_resumo.csv` (Dataset: `tabular_data/non_regenerable_results/A8_prmi_resumo.csv`)

## 4. Outputs

- `20_figura_resultado.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- matplotlib
- numpy
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_a8_prmi.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `faa955c446735c84ffbad596d76568cac58d1ca2ffefa55b2fd4ed1b1eadc050` (MD5 `60397730684fd3b887c24e588c8bbbbb`)
- SHA-256 of the distribution file (with header and docstrings): `e3cfb4bba8be73104cedfc612fb39ce2870c74132154850078bd8eb4efcf094e`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/A8_prmi_resumo.csv`
