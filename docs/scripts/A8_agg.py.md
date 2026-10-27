# A8_agg.py

**Title:** Aggregation of the PRMI benchmark  
**File:** `scripts/A8_agg.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-14  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Aggregates per-image PRMI benchmark metrics on complete cases with parental-unit clustered and species-stratified bootstrap.

## 2. Methodological stage

A8 Benchmark

## 3. Inputs

- `metricas/A8_prmi_por_imagem.csv` (Dataset: `tabular_data/non_regenerable_results/A8_prmi_por_imagem.csv`)

## 4. Outputs

- `metricas/A8_por_especie.csv` (Dataset: `tabular_data/non_regenerable_results/A8_por_especie.csv`)
- `metricas/A8_prmi_resumo.csv` (Dataset: `tabular_data/non_regenerable_results/A8_prmi_resumo.csv`)

## 5. Dependencies

- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A8_agg.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 7
- Table S6

## 9. Limitations and reproduction conditions

- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Random seeds in code: 42.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `3485fbbfda46e7c687bac20817faeb1d7988970c34c9d476f294050800fb5f4f` (MD5 `5babfb43d544bc40be067b43543905ea`)
- SHA-256 of the distribution file (with header and docstrings): `e241c9cf7b262942a1f0ffb3aa25ffa1771bf74de12cdd966d52e32a9b8e1f5d`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `tabular_data/non_regenerable_results/A8_por_especie.csv`
- `tabular_data/non_regenerable_results/A8_prmi_por_imagem.csv`
- `tabular_data/non_regenerable_results/A8_prmi_resumo.csv`
