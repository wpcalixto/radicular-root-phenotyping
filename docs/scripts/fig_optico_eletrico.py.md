# fig_optico_eletrico.py

**Title:** Figure: optical-electrical trajectory agreement  
**File:** `scripts/fig_optico_eletrico.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws per-rhizotron conductivity slopes against occupancy and length slopes (16_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `16_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `16_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `16_figura_resultado_legenda.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A2_slopes_by_rizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- printed results only

## 5. Dependencies

- matplotlib
- numpy
- scipy
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_optico_eletrico.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 12

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `c27e196bb8c90f738543850569f1a0b8b1ffcb9c4dab17cf32a0d3fdbaf85919` (MD5 `c56a4976b48f8592dcee7ad5f5d36943`)
- SHA-256 of the distribution file (with header and docstrings): `837951562b51513c7f942e1c141475d3ffcd04d6d4ab1a256cdfb5b1c0f126cd`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
