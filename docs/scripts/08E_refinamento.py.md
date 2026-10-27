# 08E_refinamento.py

**Title:** M3 refinement (Frangi denoising before union)  
**File:** `scripts/08E_refinamento.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Removes small, rounded M1 components while keeping elongated and large ones, unites the result with M2 and applies a final closing to produce the final M3 masks.

## 2. Methodological stage

08E Fusion M3

## 3. Inputs

- `saidas/06C_inferencia/masks` (Dataset: `masks/m2_unet`)
- `saidas/07_frangi/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/combinado_limpo_parameters.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_combinado_limpo/masks` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/08_combinado_limpo/masks/<data>/<id>.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- numpy
- skimage
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/08E_refinamento.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `8e9aabaa96559c01b7b2f3722688a171b4f09aff998fd8e26eed922353c3e801` (MD5 `3147149b4507a95da84e603d5160d0f3`)
- SHA-256 of the distribution file (with header and docstrings): `22de39c8b0355da2f2ed50b7d81101e753b316b4a5e9fa2227383353a953516c`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `masks/m2_unet`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
