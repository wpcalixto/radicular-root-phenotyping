# fig_si.py

**Title:** Supporting Information figures  
**File:** `scripts/fig_si.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-08-01  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Draws the Supporting Information figure panels S1-S9 (training curves, PRMI, profiles by segmenter, root under reflection, scores per image, rates, electrical trajectories, horizon by model, parameters).

## 2. Methodological stage

Figures

## 3. Inputs

- `08D_selecao_por_imagem.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `A8_por_especie.csv` (Dataset: `tabular_data/non_regenerable_results/A8_por_especie.csv`)
- `A8_prmi_por_imagem.csv` (Dataset: `tabular_data/non_regenerable_results/A8_prmi_por_imagem.csv`)
- `S3_legenda.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S6_legenda.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S7_legenda.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S8_legenda.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `combinado_limpo_parameters.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `deflash_root_overlap.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `electrical_features_by_rhizotron.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `external_training_log.csv` (Dataset: `tabular_data/non_regenerable_results/external_training_log.csv`)
- `frangi_parameters.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `model_horizon.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `root_density_by_layer.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `root_density_by_layer_M1.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `root_density_by_layer_M2.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `temporal_rates.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `S2_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S2_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S4_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S4_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S4_c.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S5_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S5_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S7_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S7_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S9_a.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S9_b.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `S9_c.pdf` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- matplotlib
- numpy
- local modules: config, estilo_figuras

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py` and the figure style from `scripts/estilo_figuras.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/fig_si.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figure S11
- Figure S12
- Figure S13
- Figure S15
- Figure S2
- Figure S3
- Figure S5
- Figure S6
- Figure S7

## 9. Limitations and reproduction conditions

- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Random seeds in code: 42.
- Verification in v1.0.0: re-executed with FIG_GRAVAR=1; regenerated PDFs pixel-identical (72 dpi) with identical page size to the RSOS files (SHA-256 differs only by PDF metadata).
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `7eed91c4cd2d3e86b3763efec991fb848b4a2ccc047929c5681c4124ce2f1322` (MD5 `5d3fcd5b185a2be186dce124a9024e4d`)
- SHA-256 of the distribution file (with header and docstrings): `49828e173c01e5bf3777370555b8fad0d74b8a84b888f33d901d544d154d3646`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/A8_por_especie.csv`
- `tabular_data/non_regenerable_results/A8_prmi_por_imagem.csv`
- `tabular_data/non_regenerable_results/external_training_log.csv`
