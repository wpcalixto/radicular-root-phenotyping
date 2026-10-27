# Provenance of the U-Net training (06B)

## Documented facts

| Evidence | Content | Source |
|---|---|---|
| Archived scripts | `06B_treino_externo_PRMI.py` and `.ipynb`: `epochs_dev = 40`, `epochs_final = 40`, `patience = 8`, `CosineAnnealingLR(T_max = epochs)` | scripts.zip members dated 2026-07-08 12:31 (.py) and 12:09 (.ipynb) |
| Other copies | `resultados/Sistema_Radicular/Dataset_PRMI/06B_treino_externo_PRMI.ipynb` and the 2026-09-21 submission zip: identical declaration (40 epochs) | project index of 145,599 files and zip members (Order 25) |
| Checkpoint | `final_state.pt` (2026-07-06 19:57; not distributed, archived in the project with SHA-256 recorded in the Order 25 manifest): epoch = 25; optimiser initial_lr = 1e-4, lr = 0.0 | record 20F_08 |
| Final weights | `models/external_final_model_PRMI_all.pt` (2026-07-06 19:57): the same 230 tensors as final_state.pt | record 20F_08 |
| Training log | `external_training_log.csv` (Dataset): 25 dev epochs and 25 final epochs; lr at epoch 1 = 9.96057e-05; lr at epoch 25 = 0.0 | Dataset, tabular_data/derived_metrics |
| Calculation | cosine schedule: 1e-4 (1 + cos(pi/T))/2 = 9.9606e-05 for T = 25 (9.9846e-05 for T = 40); lr = 0 at epoch 25 only for T_max = 25 | record 20F_08 |
| Notebook pins | `!pip install segmentation-models-pytorch==0.3.4 albumentations==1.4.0` | .ipynb |

## Search for the executed version (Order 25)

- Project tree: 7,050 files and 138,549 zip members hashed and scanned for epoch settings: no file declares 25 epochs.
- Encrypted cloud backups (`backup_nuvem`, `backup_drive`, `backup_mac`): contain no project files.
- Google Drive remote configured on the server: shared backup drive only; the `Sistema_Radicular` folder used in July is not reachable through it.
- Dropbox: name search over the whole account (rate-limited); final status in the Order 26 report.

## Determination

The weights used in the study were produced by an execution with 25 epochs in both phases on 2026-07-06.
The archived script (40 epochs) does **not** reproduce that training directly. The executed version is not
preserved in the examined sources. The script was **not** modified in v1.0.0.

## Reproduction scope

- **Inference** with the preserved weights (06C): reproducible within a small tolerance (median Dice 0.9996 in v1.0.0 verification).
- **Training**: requires the archived script with `epochs_dev = epochs_final = 25` as a documented posterior
  reconstruction, the PRMI data and split (`external_split.csv`), and a GPU environment; Python, torch and CUDA
  versions of the original Colab run were not recorded. Such a reconstruction would not be the historical code.
