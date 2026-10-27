# Parameters

All numerical parameters are defined in the scripts themselves (constants near the top of each file) or in
`scripts/config.py`; they were not changed in v1.0.0. Main values:

| Parameter | Value | Location |
|---|---|---|
| Sowing date (DAP = 0) | 2025-04-23 | config.py |
| Rhizotrons / collections | R01-R12 / 7 collections (23/05-05/07/2025) | config.py |
| Wenner spacing a | 0.16 m (spreadsheets used 0.2667 m) | config.py |
| QC thresholds | over 0.95, under 0.05, saturation 0.90, central region 35-65%, glare classes 0.05/0.20 | config.py |
| U-Net inference | resnet34 encoder, longest side 1024, threshold 0.5, ImageNet normalisation | 06C_inferencia.py |
| U-Net training (declared) | epochs_dev = epochs_final = 40, patience 8, cosine schedule (executed: 25 epochs) | 06B_treino_externo_PRMI.py |
| Exclusion band around reconstruction | 40 pixels | A9_ablacao.py |
| E_d distance bands | 60, 120, 240 pixels | A9_ablacao.py |
| Bootstrap | B = 5000, seed 42 (most analyses) | A12, A16, A18, A9b, ... |
| Blinded package | fixed random seed for anonymous codes | 08B_pacote_cego.py |

Per-file parameters and seeds are listed in `docs/scripts/<file>.md`, section 6.
