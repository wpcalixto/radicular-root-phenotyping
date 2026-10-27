# fig_glare_exemplos.py

**Title:** Figure: low and moderate glare examples  
**File:** `scripts/fig_glare_exemplos.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws two same-date examples of low and moderate central reflection with the quality-control central region.

## 2. Methodological stage

Figures

## 3. Inputs

- `R05_31_05_2025.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `R12_31_05_2025.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `Artigo_revista/04_figura_resultado.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- PIL
- matplotlib
- numpy
- local modules: estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_glare_exemplos.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 5

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `1f0a9b0a04562f9311a2dc1ce31f7a4e38cc7718db6f8a2e4cd806bd32bc5b48` (MD5 `bf1c662fcda99f9dc31ef18557fba3fa`)
- SHA-256 of the distribution file (with header and docstrings): `9d4f97c211460021619f5e8b26840d83e1fcd083fc8595ea40b52310954a222f`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
