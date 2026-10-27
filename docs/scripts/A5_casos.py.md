# A5_casos.py

**Title:** Representative and failure cases  
**File:** `scripts/A5_casos.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-31  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Selects six images by objective rules and writes four-panel figures and the per-case metric table (score, acceptance, flags, M3 composition).

## 2. Methodological stage

A5 Cases

## 3. Inputs

- `metricas/A1_composicao_m3.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `metricas/notas_recebidas` (Dataset: `annotations/blind_assessment/assessor_sheets`)
- `metricas/pretratamento_05A.csv` (Dataset: `tabular_data/non_regenerable_results/pretratamento_05A.csv`)
- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)

## 4. Outputs

- `metricas/A5_casos.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- matplotlib
- numpy
- openpyxl
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A5_casos.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Figure S8
- Figure S9
- Table S14

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed (with run_A5_sem_render.py and with rendering); A5_casos.csv byte-identical; regenerated PDFs pixel-identical (72 dpi) to the RSOS files.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `ba07a6b3dc68dda0bce00b13bab654d039b4b4a2422517e309b5ac9ef8dbc5da` (MD5 `34d5fa86ad54e0c52f8946d8533a30d8`)
- SHA-256 of the distribution file (with header and docstrings): `d5a5d01f80472bed6213f1757143f68b1842f3141ed49b169339cb11a56847cc`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/assessor_sheets`
- `annotations/blind_assessment/review_key.csv`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/pretratamento_05A.csv`
