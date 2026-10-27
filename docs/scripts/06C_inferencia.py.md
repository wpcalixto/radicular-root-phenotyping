# 06C_inferencia.py

**Title:** M2 inference on the conditioned images  
**File:** `scripts/06C_inferencia.py`  
**Type:** Script  
**Version:** v1.0.0 (distribution); historical source dated 2026-07-08  
**Status:** Part of the processing chain that produced the RSOS v3 results.

## 1. Scientific purpose

Applies the final PRMI-trained U-Net (external_final_model_PRMI_all.pt) to the 82 conditioned images and writes the candidate M2 masks and overlays.

## 2. Methodological stage

06C Inference

## 3. Inputs

- `{DRIVE_PRMI}/modelos_06B/external_final_model_PRMI_all.pt`

## 4. Outputs

- `{DRIVE_PRMI}/06C_inferencia/external_local_inference_log.csv` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)
- `{DRIVE_PRMI}/06C_inferencia/masks/<data>/<id>.png` (Dataset: `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`)

## 5. Dependencies

- cv2
- numpy
- segmentation_models_pytorch
- torch

## 6. Parameters and configuration

Constants and paths come from `scripts/config.py`. No random seed is set in this file.

## 7. Execution

```bash
python scripts/06C_inferencia.py (from a workspace prepared with tools/prepare_workspace.py)
```

## 8. Related article results

- No figure or table of the RSOS v3 article is generated directly by this file (see docs/reproducibility.md for indirect roles).

## 9. Limitations and reproduction conditions

- Requires the external PRMI archive (Zenodo 10.5281/zenodo.5974905, CC0 1.0), which is not redistributed in these packages.
- Contains instructions referring to Google Drive/Colab/rclone storage used during the original execution; these are historical and optional.
- Verification in v1.0.0: re-executed on CPU (torch 2.8, segmentation-models-pytorch 0.5.0) with the archived weights and JPEG inputs; 82/82 masks not byte-identical (median Dice 0.9996, minimum 0.9965, median 61 differing pixels), attributed to environment differences from the original Colab run.
- Environment of the verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.

## 10. Provenance

- SHA-256 of the historical file (before documentation): `8ba1f178f88b29aa9099ac6a74c8e045961e1527fdf809b255dc3b21c253ed79` (MD5 `1406223bd31fd573c138b3dee340afcd`)
- SHA-256 of the distribution file (with header and docstrings): `60a1bd56397d91c579e3d914a6e844c3a58c9410b1f4894110deeb7237adb552`
- Structural equivalence (AST without docstrings / code cells): verified
- Origin: `resultados/Nova_versao/scripts.zip` (member identical to the audited package)

## 11. Dataset references

- `regenerated output (expected SHA-256 in tests/expected_outputs_sha256.csv when applicable)`
