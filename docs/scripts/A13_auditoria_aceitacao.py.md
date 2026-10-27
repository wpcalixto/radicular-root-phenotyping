# A13_auditoria_aceitacao.py

**Title:** Acceptance audit and assessor panel  
**File:** `scripts/A13_auditoria_aceitacao.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-30  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Detects content-identical assessor files and compares acceptance under the marked() and accepted() reading rules for the assessor panels.

## 2. Methodological stage

A13 Audit

## 3. Inputs

- `metricas/notas_recebidas` (Dataset: `annotations/blind_assessment/assessor_sheets`)
- `metricas/review_key.csv` (Dataset: `annotations/blind_assessment/review_key.csv`)

## 4. Outputs

- `metricas/A13_auditoria_aceitacao.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/A13_auditoria_aceitacao.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S10

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `900cc54662ea2d28830a88796e1c7d0434fd458f1f61e41c168b4a339fbdd57c` (MD5 `63e5f8b7d3f660c5b3c0ee0b9dce4417`)
- SHA-256 of the distribution file (with header and docstrings): `b130294d3ac5e7dfc16b31d613f9dca3c7fbf5c2ebec65d76b8e8e069cf945e8`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `annotations/blind_assessment/assessor_sheets`
- `annotations/blind_assessment/review_key.csv`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
