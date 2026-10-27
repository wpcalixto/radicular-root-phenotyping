# fig_pred.py

**Title:** Figure: observed versus predicted mass  
**File:** `scripts/fig_pred.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws observed versus leave-one-rhizotron-out predictions for root and shoot mass (13_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `13_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `13_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `13_figura_resultado_legenda.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/predictions_by_rhizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- printed results only

## 5. Dependencies

- matplotlib
- numpy
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_pred.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figure S16

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `30a89392754b87766295880d42566021b911ec3a0a10e2bd4e76c406f3a5fad1` (MD5 `120144eca8f99fb3f7de55fb2f81b7d0`)
- SHA-256 of the distribution file (with header and docstrings): `4669d9a032155939995396be43c252450a103a8ed28ffea1091caff037f00982`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
