# fig_deflash.py

**Title:** Figure: reflection conditioning example  
**File:** `scripts/fig_deflash.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Writes original, inpainting mask, reconstructed image and removed region panels for one example image (04_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- `04_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `04_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `04_figura_resultado_c.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `04_figura_resultado_d.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- PIL
- matplotlib
- numpy

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/fig_deflash.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 5

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `75fbbcfb29c3075de6c335cefee61dd76a70672defe6d6b33ce5b123f720be6b` (MD5 `0271c9d359bf24039624df051718ebc3`)
- SHA-256 of the distribution file (with header and docstrings): `bc2c932f03fe144f0b0d4b12a62a19b6edf8b27de2961e59128162c60e849f39`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
