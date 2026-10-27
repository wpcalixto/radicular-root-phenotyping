# Limitations

- The U-Net weights were produced by a 25-epoch execution whose script version was not preserved; the archived
  06B script declares 40 epochs (docs/06B_training_provenance.md).
- The library versions of the original executions were not recorded; the verification environment differs.
- M2 inference is reproducible within a small tolerance, not bit-exactly, in a different environment.
- LaMa conditioning (05A) depends on weights downloaded at run time; it was not re-executed in v1.0.0.
- PRMI-dependent scripts require the external PRMI archive, not redistributed here.
- Timing results (A6) depend on hardware.
- Only scripts needed to reproduce the article are distributed; earlier-manuscript, backup and administrative scripts are excluded (Order 26).
- Code comments and original module notes are in Portuguese; headers and added docstrings are in English.
- Parameter types are not annotated in the original code; docstrings describe roles, not enforced types.
