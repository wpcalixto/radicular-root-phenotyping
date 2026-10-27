# Changelog

## v1.0.0 — 2026-10-26 (minimal reproduction package; not published)

- 74 historical files (73 scripts and the 06B notebook) needed for the article results (from `resultados/Nova_versao/scripts.zip`) and 4 auxiliary scripts.
- Excluded (Order 26): 21 backup files, 8 earlier-manuscript scripts, 1 review-support script, administrative or
  redundant files (00_inventario, 05B, 08C, 06C/08A notebooks, run_A5_sem_render, tabelas_20G) and the training
  checkpoints (final_state.pt, dev_last.pt; same tensors as the distributed weights, hashes recorded).
- Protocol-15 headers and docstrings; executable code unchanged (AST without docstrings identical).
- tools/prepare_workspace.py adapted to the minimal Dataset; tests/expected_outputs_sha256.csv added.
