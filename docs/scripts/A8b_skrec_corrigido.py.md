# A8b_skrec_corrigido.py

**Title:** Corrected skeleton sensitivity  
**File:** `scripts/A8b_skrec_corrigido.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Recomputes skeleton sensitivity without prediction-dependent exclusion of images, with stratified bootstrap.

## 2. Methodological stage

A8 Benchmark

## 3. Inputs

- `metricas/A8_prmi_por_imagem.csv` (Dataset: `tabular_data/non_regenerable_results/A8_prmi_por_imagem.csv`)

## 4. Outputs

- `metricas/A8b_skrec_corrigido.csv` (Dataset: `tabular_data/non_regenerable_results/A8b_skrec_corrigido.csv`)

## 5. Dependencies

- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. Random seeds in the code: 42.

## 7. Execution

```bash
python scripts/A8b_skrec_corrigido.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Random seeds in code: 42.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `a508f7e060a6cbb9fdfa22521bcc0c1fe406c292e72fe6c4e70e5a036292848b` (MD5 `f5a74d6413e47a274b7e41ef87bddb73`)
- SHA-256 of the distribution file (with header and docstrings): `48b2532ffc6733f7829f725608aced7a139624e7247c33f5e9db7288aad7ed57`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `tabular_data/non_regenerable_results/A8_prmi_por_imagem.csv`
- `tabular_data/non_regenerable_results/A8b_skrec_corrigido.csv`
