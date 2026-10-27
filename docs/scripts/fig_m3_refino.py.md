# fig_m3_refino.py

**Title:** Figure: M3 refinement example  
**File:** `scripts/fig_m3_refino.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Writes conditioned image, raw M3, removed components and refined M3 panels (08_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- `08_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `08_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `08_figura_resultado_c.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `08_figura_resultado_d.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- PIL
- cv2
- matplotlib
- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_m3_refino.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `624588468dca56eab1a80e1406ac9a001fcf6f7a14884085413dbbee3d5cde2d` (MD5 `61cf1ebc261a60823b484d525a66f728`)
- SHA-256 of the distribution file (with header and docstrings): `c8e4b0ae64b29b201f2382d2670a6b4ce2aa9f90cbc7523e7026f5f1dae4c298`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
