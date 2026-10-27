# fig_biomassa.py

**Title:** Figure: final biomass by treatment  
**File:** `scripts/fig_biomassa.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws shoot and root air-dry mass per treatment with individual rhizotrons (14_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `14_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `14_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/multimodal_targets.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

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
python scripts/fig_biomassa.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figure S14

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `b7f7c11a796f683f9b658a50d6e6f8f9bd73741c64459afcd4e5f3c4ac8cd265` (MD5 `3b0436125daf3686f166dc0cd408d457`)
- SHA-256 of the distribution file (with header and docstrings): `8912564083418873accd3905db92744b68d584d4a6e04acc18d16c1492b0d7fc`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
