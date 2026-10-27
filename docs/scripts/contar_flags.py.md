# contar_flags.py

**Title:** Issue-flag counts by denominator  
**File:** `scripts/auxiliary/contar_flags.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-10-25  
**Status:** Auxiliary script of the manuscript preparation (Phase 20 / Order 22).

## 1. Scientific purpose

Counts the issue flags per method from the 12 assessor sheets and reports frequencies over the 410 judgements of the five flagging assessors and over all 984 judgements (Table 5, Order 22).

## 2. Methodological stage

Order 22 auxiliary

## 3. Inputs

- none detected by static analysis

## 4. Outputs

- printed results only

## 5. Dependencies

- Python standard library only

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/auxiliary/contar_flags.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Tabela 5

## 9. Limitations and reproduction conditions

- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `8b2d3aec94be3d3d631c882e8b9b76f4aba2fd5b77d14ff6fd2086222ef8e16e` (MD5 `fdbba7a49da513ad27d8201b7127f7f2`)
- SHA-256 of the distribution file (with header and docstrings): `149d812ff678f6de79a7598369024bbd57ff68035a45909fe1ae2f3ddea39868`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: records of the manuscript preparation (ETAPA4_CONGELADA_2026-10-26 / Order 22 working area)

## 11. Dataset references

- none
