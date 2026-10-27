# fig_a7_resiliencia.py

**Title:** Figure: M3 advantage across conditions  
**File:** `scripts/fig_a7_resiliencia.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws forest plots of M3-minus-M1/M2 score and acceptance differences by condition with clustered intervals (files 19_figura_resultado_*.pdf).

## 2. Methodological stage

Figures

## 3. Inputs

- `19_figura_resultado_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `19_figura_resultado_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `19_figura_resultado_legenda.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A7_resiliencia.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

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
python scripts/fig_a7_resiliencia.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 7

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `d1fad5a026efeba951bca9930e94f729bfba271bf03b37164e65a3985e20ccb7` (MD5 `a1a59109caf152696e9950ec67619550`)
- SHA-256 of the distribution file (with header and docstrings): `dce0c8d0ddc39b3df97c51f795f35c0ee0d21056b4821019e0f26addb6daf8f3`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
