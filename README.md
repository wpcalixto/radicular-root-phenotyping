# Radicular: auditable longitudinal root phenotyping pipeline for rhizotron images and apparent electrical conductivity

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23679263.svg)](https://doi.org/10.5281/zenodo.23679263)

> **The dataset is on Zenodo.** This GitHub repository contains **only the source code and documentation**.
> The **dataset** (rhizotron images, masks, blinded assessments, Wenner measurements and biomass) and the **trained U-Net models** are archived on Zenodo, in a single record together with this code:
>
> **Zenodo record: [https://doi.org/10.5281/zenodo.23679263](https://doi.org/10.5281/zenodo.23679263)** (DOI 10.5281/zenodo.23679263)
>
> To reproduce the results, download `Radicular_Dataset_v1.0.0.zip` and `Radicular_Software_v1.0.0.zip` from the Zenodo record (the software archive also contains `models/`).
> Please cite the Zenodo record (see `CITATION.cff`).

## What is here and what is on Zenodo

| | GitHub (this repository) | Zenodo (10.5281/zenodo.23679263) |
|---|---|---|
| Source code, configuration, tools | ✔ | ✔ |
| Documentation, environment, tests | ✔ | ✔ |
| Dataset | — | ✔ |
| Trained models (`models/`) | — | ✔ |

Apart from this README, the files are identical to those of `Radicular_Software_v1.0.0.zip` on Zenodo (the integrity checksums are in the Zenodo archive).

## Package documentation (as archived on Zenodo)

| Field | Value |
|---|---|
| Version | v1.0.0 |
| Resource type | Software |
| DOI | 10.5281/zenodo.23679263 (reserved; registered upon publication) |
| Author and developer | Wesley Pacheco Calixto — Universidade de Coimbra (UC), Portugal; Universidade Federal de Goiás (UFG), Brazil; Instituto Federal de Educação, Ciência e Tecnologia de Goiás (IFG), Brazil |
| Corresponding author | Wesley Pacheco Calixto, wesley.pacheco@isr.uc.pt |
| Licence | MIT (see LICENSE) |
| Related publication | Auditable longitudinal root phenotyping in rhizotrons using Frangi--U-Net fusion and apparent conductivity (manuscript in preparation for submission to Royal Society Open Science) |
| Related dataset | Radicular Dataset v1.0.0, in this same record (DOI 10.5281/zenodo.23679263) |
| Funding | Fundação para a Ciência e a Tecnologia (FCT, Portugal) and University of Coimbra, (DOI 10.54499/UID/00048/2025); CNPq (Brazil) 301644/2022-5, 150331/2026-6, 178681/2024-5, 402016/2025-4 and 140964/2025-8; CAPES (Brazil) 88887.985910/2024-00 and 88887.088466/2024-00 |

### Scope

Only the code needed to reproduce and verify the results of the related article: 74 historical files (73 scripts and the 06B notebook) of
the study, 4 auxiliary scripts of the final manuscript preparation (`scripts/auxiliary/`), the U-Net weights needed for
inference and for the PRMI diagnostics, the experimental chronology (`config/`), a workspace tool and tests. Each file has
a Protocol-15 header and an individual document (`docs/scripts/`); executable lines are unchanged.

### External resources (not redistributed)

- PRMI minirhizotron dataset (Zenodo 10.5281/zenodo.5974905, CC0 1.0): needed only to re-run the U-Net training (06B) and the PRMI benchmark (06A, 08A, A8).
- LaMa inpainting: simple-lama-inpainting 0.1.0 (Apache-2.0) and the `big-lama.pt` weights of its v0.1.0 release (LaMa, Apache-2.0): needed only to re-run the conditioning (05A).
- Python libraries listed in `requirements.txt`, installed by the user under their own licences.

### Provenance of the code

`docs/historical_hashes.csv` lists, for every script, the MD5 and SHA-256 of the historical file and the SHA-256 of the
distributed file (which only adds a header and docstrings; executable code verified identical). For example, the
classical-segmentation routine `07_frangi.py` corresponds to the historical file with MD5 3efa4c4a….

### Structure

```text
scripts/            pipeline scripts (config.py defines the directory tree relative to the repository root)
scripts/auxiliary/  beta_pm1.py, contar_flags.py, casos_flags.py, run_A15_pad010.py
config/             cronograma_experimento.csv, cronologia_dap.csv
models/             external_final_model_PRMI_all.pt (M2 inference), external_development_model.pt (PRMI diagnostics)
tools/              prepare_workspace.py (builds the tree expected by the scripts from the Dataset)
tests/              test_smoke.py, expected_outputs_sha256.csv (672 expected outputs)
docs/               installation, usage, parameters, reproducibility, limitations, 06B training provenance, per-file documents
checksums/          checksums_sha256.txt
```

### Quick start

```bash
pip install -r requirements.txt
python tools/prepare_workspace.py --dataset ../Dataset_Radicular_v1.0.0 --software . --workspace ../ws
# run the pipeline as in docs/usage.md, then:
python tests/test_smoke.py --compare ../ws
```

### Reproducibility (verified 2026-10-26 from the Dataset and this Software only)

66 pipeline steps executed without error; 557 outputs byte-identical to the archived results (images, M1 and M3 masks,
all regenerable result tables, chronology and manifest); A7_logistico.csv equivalent at the published precision; 114
figure files pixel-identical to the article; blinded-assessment key and 246 overlays regenerated identically. See
`docs/reproducibility.md`. Not reproducible from these packages: U-Net training (06B; see docs/06B_training_provenance.md),
LaMa conditioning (05A; conditioned images are distributed as data), PRMI-dependent and hardware-dependent results
(distributed as non-regenerable results in the Dataset).
