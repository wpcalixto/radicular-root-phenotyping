# 05_registro_calibracao.py

**Title:** Geometric registration and centred cropping  
**File:** `scripts/05_registro_calibracao.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-12  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Crops every converted image around its centre with radii bounded by the smallest image in the set, producing registered images of identical size, and logs the registration parameters.

## 2. Methodological stage

05 Registration

## 3. Inputs

- `saidas/03_convertidas` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/image_registration_log.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/05_registradas` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/05_registradas/<data>/R##.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- PIL
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/05_registro_calibracao.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `32624053d7ea980c5bcfdceaa280e9531cb778e9c7dc31b2f9f4b534a9233004` (MD5 `338aed152a8b376df5dd3c533f49b421`)
- SHA-256 of the distribution file (with header and docstrings): `97158399f51b37c5f495f4bf79e93d97cfd9594c4dba339ed8da0dd076837dc5`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
