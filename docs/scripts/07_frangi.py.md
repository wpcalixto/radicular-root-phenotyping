# 07_frangi.py

**Title:** Classical segmentation M1 (Frangi)  
**File:** `scripts/07_frangi.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Applies photometric flat-field correction, residual-glare thresholding and multiscale Frangi vesselness with morphological post-processing to the conditioned images, producing M1 masks, glare masks and overlays.

## 2. Methodological stage

07 Segmentation M1

## 3. Inputs

- `saidas/05A_tratadas` (Dataset: `images_processed/conditioned`)

## 4. Outputs

- `metricas/frangi_parameters.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/07_frangi` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/07_frangi/glare/<data>/R##.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/07_frangi/masks/<data>/R##.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `saidas/07_frangi/overlays/<data>/R##.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- numpy
- skimage
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/07_frangi.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Verification in v1.0.0: re-executed in an isolated workspace built from the Dataset; outputs byte-identical to the archived versions.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `8bfc2bb3c371d2a4c12f713560e135a55426cc41bf1fa3532ebada2cfaf8371a` (MD5 `3efa4c4aca6bbe97fdda2fc3af427c40`)
- SHA-256 of the distribution file (with header and docstrings): `8e67653633c76df0e0d4996eba024b387199f5ed9084729effaf0618b9b3a6f2`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `images_processed/conditioned`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
