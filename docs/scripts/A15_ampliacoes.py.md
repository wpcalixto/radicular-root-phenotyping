# A15_ampliacoes.py

**Title:** Paired enlargements of diagnostic cases  
**File:** `scripts/A15_ampliacoes.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Selects, for each diagnostic case, the 500-pixel window that maximises M1/M2 disagreement and writes paired panels with identical spatial limits and the window table.

## 2. Methodological stage

A15 Figures

## 3. Inputs

- `metricas/A5_casos.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `Artigo_revista/21_figura_resultado_<1-6><a-d>.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/A15_janelas.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- matplotlib
- numpy
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A15_ampliacoes.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figura 9
- Figure S10
- Table S13

## 9. Limitations and reproduction conditions

- The approved PDFs were produced with savefig.pad_inches = 0.10; use scripts/auxiliary/run_A15_pad010.py.
- Verification in v1.0.0: re-executed through scripts/auxiliary/run_A15_pad010.py; PDFs pixel-identical (72 dpi) to the RSOS files.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `85f7c8b5b840b0bf6150fe86d3fcf283b0bc39f57b60df87f6ba874da0afb5e5` (MD5 `05a8b20d05c4b5fe1ed8b0523ae319dd`)
- SHA-256 of the distribution file (with header and docstrings): `fe20042162f9024a41e686b825c06f66d3808670ef39a3875c996d9beca2516e`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
