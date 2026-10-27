# 05C_auditoria_mascara_raiz.py

**Title:** Root-mask overlap with reconstructed regions  
**File:** `scripts/05C_auditoria_mascara_raiz.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-12  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Crosses each inpainting mask with the final M3 root mask and reports the fraction of detected root pixels inside the reconstructed region and root density inside versus outside it.

## 2. Methodological stage

05C Conditioning audit

## 3. Inputs

- `saidas/05A_tratadas/_mascaras` (Dataset: `masks/reconstruction`)
- `saidas/05A_tratadas/_mascaras/<data>/R##.png` (Dataset: `masks/reconstruction/<data>/R##.png`)
- `saidas/08_combinado_limpo/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_combinado_limpo/masks/<data>/R##.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/deflash_root_overlap.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- numpy
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/05C_auditoria_mascara_raiz.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- Table S3

## 9. Limitations and reproduction conditions

- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `eba1cd59bc0832f3cc7afb432c86423633dee06b25da2bfac3d07c9827093d7b` (MD5 `2811a1484efa5be5097988b7579a3417`)
- SHA-256 of the distribution file (with header and docstrings): `1da6aacf4ee783dba0f3b1474235bfd8f777202f6d007236d1ba7aecff84b614`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `masks/reconstruction/<data>/R##.png`
- `masks/reconstruction`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
