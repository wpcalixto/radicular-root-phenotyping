# prepare_workspace.py

**File:** `tools/prepare_workspace.py` · **Version:** v1.0.0 · **Status:** distribution helper (prepared with an AI coding assistant under the author's direction).

## Purpose
Builds, by physical copy, the directory tree expected by `scripts/config.py` from the Dataset and the Software:
`entradas/` (in situ HEIC, harvested roots, assessor sheets), `tabdatas/` (electrical and biomass spreadsheets),
`saidas/05A_tratadas/` (conditioned images and reconstruction masks), `saidas/06C_inferencia/masks/` (M2),
`metricas/` (assessor sheets, answer key and non-regenerable results), `manifestos/external_split.csv`, `config/`,
`modelos/` and `scripts/`, plus the empty output directories `Artigo_revista/`, `figures/`, `figdata/`.

## Inputs / outputs
Inputs: `--dataset`, `--software`, optional `--parts` (default: all). Output: a new `--workspace` directory (never overwritten).

## Execution
`python tools/prepare_workspace.py --dataset ../Dataset_Radicular_v1.0.0 --software . --workspace ../ws`

## Dependencies
Python standard library.

## Limitations
About 2 GB before the pipeline regenerates its outputs (the regenerated images and masks add about 5 GB).
