# fig_importancia.py

**Title:** Figure: importance by modality  
**File:** `scripts/fig_importancia.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws the sum of absolute permutation importance by modality for root and shoot mass (11_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `11_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `11_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/explainability_by_group.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- printed results only

## 5. Dependencies

- matplotlib
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_importancia.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figure S17

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `d4029838c82c2211fc964230d7845e56a6f2948b513fd409867e2c030909864f` (MD5 `54a5fe68190363ded4d0960848b519e3`)
- SHA-256 of the distribution file (with header and docstrings): `bada06c4ece7df9f530bd75ca3dab55f07e25e596bca962f31a75f0183e6ce6f`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
