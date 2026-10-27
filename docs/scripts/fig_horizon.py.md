# fig_horizon.py

**Title:** Figure: MAE by horizon  
**File:** `scripts/fig_horizon.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws leave-one-rhizotron-out MAE by horizon and outcome against the mean baseline (12_figura_resultado_a.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `metricas/model_performance.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `12_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- matplotlib
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_horizon.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figure S16

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `a406317fd6bac2c4a39b22fe1b92968d086f0e681c957f00f80d287a00e32bec` (MD5 `6b1f51a5931fe042e7154a2c6f10ae92`)
- SHA-256 of the distribution file (with header and docstrings): `7ba0839cf90be059761bf2be4208954eab25b36b9a31bf6a15209f1275b8b75a`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
