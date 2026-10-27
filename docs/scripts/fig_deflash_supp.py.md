# fig_deflash_supp.py

**Title:** Figure: reconstruction characterisation (SI)  
**File:** `scripts/fig_deflash_supp.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws the distribution of reconstructed fraction and specular cores and their relation to collection, rhizotron and glare indices (05_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `metricas/image_qc.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/pretratamento_05A.csv` (Dataset: `tabular_data/non_regenerable_results/pretratamento_05A.csv`)

## 4. Outputs

- `05_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `05_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `05_figura_resultado_c.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `05_figura_resultado_d.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `05_figura_resultado_e.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `05_figura_resultado_f.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- matplotlib
- numpy
- scipy
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_deflash_supp.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figure S4

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `cce0f2b5569fe9d4e09b1b94d1423c06ba757f42f3a5c6d83a364e8fc2996bae` (MD5 `ab0304da51899099bba4ed580fe9bbfd`)
- SHA-256 of the distribution file (with header and docstrings): `21c376b47637ab366be089586a5aca620010f396c30accb4ff9607c444c3dac8`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/pretratamento_05A.csv`
