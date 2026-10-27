# 08D_selecao.py

**Title:** Assessment consolidation, method selection and agreement  
**File:** `scripts/08D_selecao.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Reads all assessor sheets (xlsx or csv), derives the 0-4 quality score and acceptance, joins the answer key and produces method rankings, per-image winners, per-assessor means and inter-assessor agreement.

## 2. Methodological stage

08D Selection

## 3. Inputs

- `metricas/notas_recebidas` (Dataset: `annotations/blind_assessment/assessor_sheets`)
- `metricas/notas_recebidas/*.xlsx` (Dataset: `annotations/blind_assessment/assessor_sheets/*.xlsx`)
- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)

## 4. Outputs

- `metricas/08D_concordancia.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/08D_metodos_agregado.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/08D_por_avaliador.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/08D_selecao_por_imagem.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- openpyxl
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/08D_selecao.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 4
- Tabela 5
- Table S8

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `369421183af1b9b3cf9bc12973c7058dab0b873adec0052aa5c90f78e01bd1c7` (MD5 `489154b487646d4747fdb1062a7d98d3`)
- SHA-256 of the distribution file (with header and docstrings): `3ce50b65558518501d20705aaadd7bf5989f2524a143751f8efe32618fabeb80`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/assessor_sheets/*.xlsx`
- `annotations/blind_assessment/assessor_sheets`
- `annotations/blind_assessment/review_key.csv`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
