# Index of per-file documentation

| File | Title | Stage | Document |
|---|---|---|---|
| `scripts/01_manifesto.py` | Master dataset manifest | 01 Manifest | [01_manifesto.py.md](01_manifesto.py.md) |
| `scripts/02_cronologia_dap.py` | Chronology and days after planting | 02 Chronology | [02_cronologia_dap.py.md](02_cronologia_dap.py.md) |
| `scripts/03_conversao_heic.py` | HEIC to PNG conversion | 03 Conversion | [03_conversao_heic.py.md](03_conversao_heic.py.md) |
| `scripts/04_qc_imagens.py` | Image quality control and central glare | 04 Quality control | [04_qc_imagens.py.md](04_qc_imagens.py.md) |
| `scripts/05A_pretratamento.py` | Specular-reflection conditioning by LaMa inpainting | 05A Conditioning | [05A_pretratamento.py.md](05A_pretratamento.py.md) |
| `scripts/05C_auditoria_mascara_raiz.py` | Root-mask overlap with reconstructed regions | 05C Conditioning audit | [05C_auditoria_mascara_raiz.py.md](05C_auditoria_mascara_raiz.py.md) |
| `scripts/05_registro_calibracao.py` | Geometric registration and centred cropping | 05 Registration | [05_registro_calibracao.py.md](05_registro_calibracao.py.md) |
| `scripts/06A_dataset_externo.py` | External PRMI dataset indexing | 06A External data | [06A_dataset_externo.py.md](06A_dataset_externo.py.md) |
| `scripts/06B_treino_externo_PRMI.ipynb` | U-Net training on PRMI (Colab notebook) | 06B Training | [06B_treino_externo_PRMI.ipynb.md](06B_treino_externo_PRMI.ipynb.md) |
| `scripts/06B_treino_externo_PRMI.py` | U-Net training on PRMI (script export) | 06B Training | [06B_treino_externo_PRMI.py.md](06B_treino_externo_PRMI.py.md) |
| `scripts/06C_inferencia.py` | M2 inference on the conditioned images | 06C Inference | [06C_inferencia.py.md](06C_inferencia.py.md) |
| `scripts/07_frangi.py` | Classical segmentation M1 (Frangi) | 07 Segmentation M1 | [07_frangi.py.md](07_frangi.py.md) |
| `scripts/08A_diagnostico_externo.py` | Diagnostic metrics of the external model on PRMI test | 08A External diagnostic | [08A_diagnostico_externo.py.md](08A_diagnostico_externo.py.md) |
| `scripts/08B_pacote_cego.py` | Blinded assessment package (M3 final) | 08B Blinded assessment | [08B_pacote_cego.py.md](08B_pacote_cego.py.md) |
| `scripts/08D_selecao.py` | Assessment consolidation, method selection and agreement | 08D Selection | [08D_selecao.py.md](08D_selecao.py.md) |
| `scripts/08E_refinamento.py` | M3 refinement (Frangi denoising before union) | 08E Fusion M3 | [08E_refinamento.py.md](08E_refinamento.py.md) |
| `scripts/08F_estatistica.py` | Statistical comparison of methods | 08F Statistics | [08F_estatistica.py.md](08F_estatistica.py.md) |
| `scripts/08G_reanalise.py` | Rhizotron-level reanalysis and ordinal agreement | 08G Statistics | [08G_reanalise.py.md](08G_reanalise.py.md) |
| `scripts/08_combinacao.py` | Union of M1 and M2 | 08 Fusion | [08_combinacao.py.md](08_combinacao.py.md) |
| `scripts/09B_raiz_colhida.py` | Projected length of harvested roots | 09B Post-harvest | [09B_raiz_colhida.py.md](09B_raiz_colhida.py.md) |
| `scripts/09_descritores.py` | Morphological descriptors per image | 09 Descriptors | [09_descritores.py.md](09_descritores.py.md) |
| `scripts/10_eletricas.py` | Electrical variables | 10 Electrical | [10_eletricas.py.md](10_eletricas.py.md) |
| `scripts/11_integracao.py` | Multimodal integration | 11 Integration | [11_integracao.py.md](11_integracao.py.md) |
| `scripts/12_temporal.py` | Temporal analysis | 12 Temporal | [12_temporal.py.md](12_temporal.py.md) |
| `scripts/13_modelagem.py` | Predictive modelling of final outcomes | 13 Modelling | [13_modelagem.py.md](13_modelagem.py.md) |
| `scripts/14_ablacao.py` | Ablation studies | 14 Ablation | [14_ablacao.py.md](14_ablacao.py.md) |
| `scripts/15_explicabilidade.py` | Permutation importance and model summary | 15 Explainability | [15_explicabilidade.py.md](15_explicabilidade.py.md) |
| `scripts/A11_sensibilidade_geometrica.py` | Geometric sensitivity of descriptors | A11 Sensitivity | [A11_sensibilidade_geometrica.py.md](A11_sensibilidade_geometrica.py.md) |
| `scripts/A12_concordancia_ic.py` | Agreement coefficients with intervals | A12 Agreement | [A12_concordancia_ic.py.md](A12_concordancia_ic.py.md) |
| `scripts/A12b_kappa_dicotomizado.py` | Fleiss kappa for dichotomised scores | A12 Agreement | [A12b_kappa_dicotomizado.py.md](A12b_kappa_dicotomizado.py.md) |
| `scripts/A13_auditoria_aceitacao.py` | Acceptance audit and assessor panel | A13 Audit | [A13_auditoria_aceitacao.py.md](A13_auditoria_aceitacao.py.md) |
| `scripts/A14_sensibilidade_segmentador.py` | Sensitivity to the segmenter | A14 Sensitivity | [A14_sensibilidade_segmentador.py.md](A14_sensibilidade_segmentador.py.md) |
| `scripts/A15_ampliacoes.py` | Paired enlargements of diagnostic cases | A15 Figures | [A15_ampliacoes.py.md](A15_ampliacoes.py.md) |
| `scripts/A16_ic_optico_eletrico.py` | Intervals for optical-electrical association | A16 Intervals | [A16_ic_optico_eletrico.py.md](A16_ic_optico_eletrico.py.md) |
| `scripts/A16b_ic_beta_misto.py` | Interval for the mixed-model beta | A16 Intervals | [A16b_ic_beta_misto.py.md](A16b_ic_beta_misto.py.md) |
| `scripts/A17_associacoes_complementares.py` | Complementary associations | A17 Associations | [A17_associacoes_complementares.py.md](A17_associacoes_complementares.py.md) |
| `scripts/A18_repetibilidade_colheita.py` | Relative consistency and harvested-root correspondence | A18 Consistency | [A18_repetibilidade_colheita.py.md](A18_repetibilidade_colheita.py.md) |
| `scripts/A1_composicao_m3.py` | Composition of M3 | A1 Composition | [A1_composicao_m3.py.md](A1_composicao_m3.py.md) |
| `scripts/A2_auditoria.py` | Rigour audits of optical-electrical analyses | A2 Audit | [A2_auditoria.py.md](A2_auditoria.py.md) |
| `scripts/A2_optico_eletrico.py` | Optical-electrical longitudinal association | A2 Association | [A2_optico_eletrico.py.md](A2_optico_eletrico.py.md) |
| `scripts/A3_baselines.py` | Treatment-dependent baselines | A3 Baselines | [A3_baselines.py.md](A3_baselines.py.md) |
| `scripts/A3_horizonte.py` | Horizon performance relative to treatment reference | A3 Baselines | [A3_horizonte.py.md](A3_horizonte.py.md) |
| `scripts/A4_auditoria.py` | Audit of vertical-distribution descriptors | A4 Audit | [A4_auditoria.py.md](A4_auditoria.py.md) |
| `scripts/A4_profundidade.py` | Vertical-distribution descriptors | A4 Descriptors | [A4_profundidade.py.md](A4_profundidade.py.md) |
| `scripts/A5_casos.py` | Representative and failure cases | A5 Cases | [A5_casos.py.md](A5_casos.py.md) |
| `scripts/A6_custo.py` | Processing time and computational repeatability | A6 Cost | [A6_custo.py.md](A6_custo.py.md) |
| `scripts/A7_resiliencia.py` | Stability of M3 advantage across image conditions | A7 Robustness | [A7_resiliencia.py.md](A7_resiliencia.py.md) |
| `scripts/A8_agg.py` | Aggregation of the PRMI benchmark | A8 Benchmark | [A8_agg.py.md](A8_agg.py.md) |
| `scripts/A8_prmi_benchmark.py` | M1/M2/M3 benchmark on PRMI test | A8 Benchmark | [A8_prmi_benchmark.py.md](A8_prmi_benchmark.py.md) |
| `scripts/A8b_skrec_corrigido.py` | Corrected skeleton sensitivity | A8 Benchmark | [A8b_skrec_corrigido.py.md](A8b_skrec_corrigido.py.md) |
| `scripts/A9_ablacao.py` | Reflection-treatment ablation | A9 Ablation | [A9_ablacao.py.md](A9_ablacao.py.md) |
| `scripts/A9b_Ed_ic.py` | Intervals for spatial enrichment E_d | A9 Ablation | [A9b_Ed_ic.py.md](A9b_Ed_ic.py.md) |
| `scripts/auxiliary/beta_pm1.py` | Regression of M3 score on Frangi share and DAP | Phase 20-F auxiliary | [beta_pm1.py.md](beta_pm1.py.md) |
| `scripts/auxiliary/casos_flags.py` | Flag counts for the six diagnostic cases | Order 22 auxiliary | [casos_flags.py.md](casos_flags.py.md) |
| `scripts/auxiliary/contar_flags.py` | Issue-flag counts by denominator | Order 22 auxiliary | [contar_flags.py.md](contar_flags.py.md) |
| `scripts/auxiliary/run_A15_pad010.py` | A15 with approved padding | Phase 20-H auxiliary | [run_A15_pad010.py.md](run_A15_pad010.py.md) |
| `scripts/config.py` | Central configuration | Configuration | [config.py.md](config.py.md) |
| `scripts/estilo_figuras.py` | Figure style module | Figures | [estilo_figuras.py.md](estilo_figuras.py.md) |
| `scripts/fig_a7_resiliencia.py` | Figure: M3 advantage across conditions | Figures | [fig_a7_resiliencia.py.md](fig_a7_resiliencia.py.md) |
| `scripts/fig_a8_prmi.py` | Figure: PRMI paired differences | Figures | [fig_a8_prmi.py.md](fig_a8_prmi.py.md) |
| `scripts/fig_biomassa.py` | Figure: final biomass by treatment | Figures | [fig_biomassa.py.md](fig_biomassa.py.md) |
| `scripts/fig_composicao.py` | Figure: M3 composition | Figures | [fig_composicao.py.md](fig_composicao.py.md) |
| `scripts/fig_deflash.py` | Figure: reflection conditioning example | Figures | [fig_deflash.py.md](fig_deflash.py.md) |
| `scripts/fig_deflash_supp.py` | Figure: reconstruction characterisation (SI) | Figures | [fig_deflash_supp.py.md](fig_deflash_supp.py.md) |
| `scripts/fig_disponibilidade.py` | Figure: multimodal availability matrix | Figures | [fig_disponibilidade.py.md](fig_disponibilidade.py.md) |
| `scripts/fig_glare_exemplos.py` | Figure: low and moderate glare examples | Figures | [fig_glare_exemplos.py.md](fig_glare_exemplos.py.md) |
| `scripts/fig_horizon.py` | Figure: MAE by horizon | Figures | [fig_horizon.py.md](fig_horizon.py.md) |
| `scripts/fig_horizonte_trat.py` | Figure: horizon ratio to treatment reference | Figures | [fig_horizonte_trat.py.md](fig_horizonte_trat.py.md) |
| `scripts/fig_importancia.py` | Figure: importance by modality | Figures | [fig_importancia.py.md](fig_importancia.py.md) |
| `scripts/fig_m3_refino.py` | Figure: M3 refinement example | Figures | [fig_m3_refino.py.md](fig_m3_refino.py.md) |
| `scripts/fig_optico_eletrico.py` | Figure: optical-electrical trajectory agreement | Figures | [fig_optico_eletrico.py.md](fig_optico_eletrico.py.md) |
| `scripts/fig_pred.py` | Figure: observed versus predicted mass | Figures | [fig_pred.py.md](fig_pred.py.md) |
| `scripts/fig_quant.py` | Figure: root quantification | Figures | [fig_quant.py.md](fig_quant.py.md) |
| `scripts/fig_segment_compare.py` | Figure: segmentation comparison | Figures | [fig_segment_compare.py.md](fig_segment_compare.py.md) |
| `scripts/fig_segment_quality.py` | Figure: assessment scores and acceptance | Figures | [fig_segment_quality.py.md](fig_segment_quality.py.md) |
| `scripts/fig_si.py` | Supporting Information figures | Figures | [fig_si.py.md](fig_si.py.md) |
| `scripts/fig_temporal.py` | Figure: temporal dynamics | Figures | [fig_temporal.py.md](fig_temporal.py.md) |
| `scripts/modelagem_incerteza.py` | Uncertainty of modelling and ablation | 13 Modelling | [modelagem_incerteza.py.md](modelagem_incerteza.py.md) |
| `tools/prepare_workspace.py` | Workspace preparation | Distribution helper | [prepare_workspace.py.md](prepare_workspace.py.md) |
| `tests/test_smoke.py` | Smoke tests and output comparison | Verification | [test_smoke.py.md](test_smoke.py.md) |
