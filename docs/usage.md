# Usage

`scripts/config.py` resolves every path from the repository root (`ROOT` = parent of `scripts/`). Build the expected tree with
`python tools/prepare_workspace.py --dataset <Dataset> --software <this directory> --workspace <new directory>` and run,
from the workspace root:

| Order | Commands |
|---|---|
| 1 | `01_manifesto`, `02_cronologia_dap`, `03_conversao_heic`, `04_qc_imagens`, `05_registro_calibracao` |
| 2 (optional) | `05A_pretratamento` (LaMa; downloads weights; the Dataset already provides its outputs) |
| 3 (optional) | `DRIVE_PRMI=<dir with imagens_05A/ and modelos_06B/> python scripts/06C_inferencia.py` (the Dataset provides the M2 masks) |
| 4 | `07_frangi` (about 12 min), `08_combinacao`, `08E_refinamento`, `05C_auditoria_mascara_raiz` |
| 5 | `09_descritores` (then with argument `M1` and `M2`), `09B_raiz_colhida`, `10_eletricas`, `11_integracao`, `12_temporal` |
| 6 | `13_modelagem`, `14_ablacao`, `15_explicabilidade`, `modelagem_incerteza` |
| 7 | `08B_pacote_cego` (regenerates the anonymised package and key), `08D_selecao`, `08F_estatistica`, `08G_reanalise`, `A12_concordancia_ic`, `A12b_kappa_dicotomizado`, `A13_auditoria_aceitacao`, `A1_composicao_m3`, `A7_resiliencia` |
| 8 | `A4_profundidade`, `A4_auditoria`, `A14_sensibilidade_segmentador`, `A2_optico_eletrico`, `A2_auditoria`, `A3_baselines`, `A3_horizonte`, `A16_ic_optico_eletrico`, `A16b_ic_beta_misto`, `A17_associacoes_complementares`, `A18_repetibilidade_colheita`, `A9b_Ed_ic`, `A8_agg`, `A8b_skrec_corrigido` |
| 9 | `python scripts/auxiliary/beta_pm1.py .`; from `scripts/`: `python auxiliary/contar_flags.py`, `python auxiliary/casos_flags.py` |
| 10 | `FIG_GRAVAR=1 python scripts/fig_<name>.py` for all fig_* scripts and `A5_casos.py`; from `scripts/`: `FIG_GRAVAR=1 python auxiliary/run_A15_pad010.py` |
| 11 | `python tests/test_smoke.py --compare <workspace>` |

Scripts that require external resources: `06A_dataset_externo`, `06B_treino_externo_PRMI` (.py/.ipynb, Colab GPU),
`08A_diagnostico_externo`, `A8_prmi_benchmark` (PRMI archive); `A6_custo` (timing); `A9_ablacao`, `A11_sensibilidade_geometrica` (M2 re-inference).
