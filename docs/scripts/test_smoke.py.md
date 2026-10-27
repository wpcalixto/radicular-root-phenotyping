# test_smoke.py

**File:** `tests/test_smoke.py` · **Version:** v1.0.0 · **Status:** verification (prepared with an AI coding assistant under the author's direction).

## Purpose
Compiles all scripts, validates the notebooks, imports `config.py`, verifies the Dataset checksums and reproduces
A9b_Ed_ic.csv (when `RADICULAR_DATASET` is set); `--compare <workspace>` compares every regenerated output with
`tests/expected_outputs_sha256.csv`.

## Execution
`RADICULAR_DATASET=../Dataset_Radicular_v1.0.0 python tests/test_smoke.py` and `python tests/test_smoke.py --compare ../ws`
