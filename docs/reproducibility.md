# Reproducibility

Verification of 2026-10-26 in an isolated workspace built only from Dataset_Radicular_v1.0.0 (minimal) and this Software
(Python 3.9.6, macOS arm64, `requirements.txt`).

| Check | Result |
|---|---|
| Pipeline steps (usage.md, orders 1 and 4-10) | 66 executed, 0 errors |
| Regenerated outputs vs archived results (`tests/expected_outputs_sha256.csv`) | 557/557 byte-identical (`sha256`); A7_logistico.csv differs by at most 1.05e-4 (relative) in GLMM estimates, no difference at the published precision (`tolerance`) |
| Images and masks | converted (82), registered (82), M1 (82), residual glare (82), M3 pre-refinement (82), final M3 (82): identical; final M3 also matches the 82 MD5 of the masks assessed and quantified |
| Figure files | 114/114 pixel-identical at 72 dpi with identical page size (SHA-256 differs only in PDF metadata) |
| Blinded assessment | 08B regenerates review_key.csv identical to the distributed key and 246/246 overlays identical to those assessed |
| Auxiliary outputs | issue-flag counts (Table 5, Table S14) and beta_PM1 = -1.090 [-2.042; -0.099] identical |
| Tables without own CSV | Tables 8, 9, 14 and S18 recomputed exactly from distributed or regenerated files |
| M2 re-inference (06C) | tested in the Order 25 verification with the same weights and inputs: median Dice 0.9996 (not bit-exact; environment differs from the original Colab run) |
| Smoke tests | compile, notebooks, config, Dataset checksums, A9b reproduction: pass |

Not re-executed: 06B training, 05A LaMa conditioning, PRMI-dependent scripts (06A, 08A, A8), A9 and A11 (M2 re-inference),
A6 (timing). Their outputs are distributed in the Dataset (`tabular_data/non_regenerable_results/`, conditioned images,
reconstruction and M2 masks).
