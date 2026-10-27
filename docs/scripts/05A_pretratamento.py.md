# 05A_pretratamento.py

**Title:** Specular-reflection conditioning by LaMa inpainting  
**File:** `scripts/05A_pretratamento.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-07  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Detects specular reflection cores and reconstructs them by LaMa inpainting, producing the conditioned images used by all segmentation methods and the binary reconstruction masks; logs the reconstructed fraction per image.

## 2. Methodological stage

05A Conditioning

## 3. Inputs

- `saidas/05_registradas` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 4. Outputs

- `metricas/pretratamento_05A.csv` (Dataset: `tabular_data/non_regenerable_results/pretratamento_05A.csv`)
- `saidas/05A_tratadas` (Dataset: `images_processed/conditioned`)
- `saidas/05A_tratadas/<data>/R##_<data>.png` (Dataset: `images_processed/conditioned/<data>/R##_<data>.png`)
- `saidas/05A_tratadas/_mascaras/<data>/R##_<data>.png` (Dataset: `masks/reconstruction/<data>/R##_<data>.png`)
- `saidas/05A_tratadas/_previas/<image_id>_ANTES_DEPOIS.png` (Dataset: `images_processed/conditioned/_previas/<image_id>_ANTES_DEPOIS.png`)

## 5. Dependencies

- PIL
- cv2
- numpy
- simple_lama_inpainting
- torch
- local modules: config

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/05A_pretratamento.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- LaMa weights are downloaded at run time by simple_lama_inpainting; their version and licence are not archived here.
- Not re-executed in the v1.0.0 verification.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `ee12fff6df54c5c3cc5895e00c90abe43d2ea2581a597d431f7c39f6bfd985fe` (MD5 `d0f0108a77323f59148fe2c29dc7e9aa`)
- SHA-256 of the distribution file (with header and docstrings): `3115ff5aa887ed68fd1622fa99bc9e48f0c40ba2f6e60b8e065d2191773bacf6`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `images_processed/conditioned/<data>/R##_<data>.png`
- `images_processed/conditioned/_previas/<image_id>_ANTES_DEPOIS.png`
- `images_processed/conditioned`
- `masks/reconstruction/<data>/R##_<data>.png`
- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
- `tabular_data/non_regenerable_results/pretratamento_05A.csv`
