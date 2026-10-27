# fig_disponibilidade.py

**Title:** Figure: multimodal availability matrix  
**File:** `scripts/fig_disponibilidade.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws the 12 x 7 availability matrix of images and electrical measurements (03_figura_resultado.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- `Artigo_revista/03_figura_resultado.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- matplotlib
- numpy
- local modules: estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_disponibilidade.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 4

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `5f6da0730f200df5c89903de999745ac6dc9408eaef3b61877e4ec7f53ff614a` (MD5 `b1291cb30be60330c6b4c40fb8ac8b26`)
- SHA-256 of the distribution file (with header and docstrings): `e89b1dff8abf24a8108fdceadfa8883e4b68f4f71b3b14e1a51b8d848f90140d`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
