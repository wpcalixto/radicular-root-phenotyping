# fig_segment_compare.py

**Title:** Figure: segmentation comparison  
**File:** `scripts/fig_segment_compare.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Writes conditioned image, M1, M2 and M3 panels for one example (06_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- `06_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `06_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `06_figura_resultado_c.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `06_figura_resultado_d.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- PIL
- matplotlib
- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_segment_compare.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 6

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `d1dbb944975f5571e9e2a70c18befccdb8ed7a87d263071a1496ef09bdd63d8f` (MD5 `f511d3b8fcbf7ba88bf94540d42fca22`)
- SHA-256 of the distribution file (with header and docstrings): `a6eb7f40a03f331e0725251110766233841f415e6be18e41c78e5a468bfc1ddd`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
