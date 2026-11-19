# Week 02 — Dataset preparation

## Done

- Added a standard-library BANKING77 CSV loader and integrity audit.
- Added deterministic, label-stratified train/validation splitting with a fixed seed.
- Kept duplicate utterances in one split to avoid text leakage across train and validation.
- Added source checksums, label mapping, split policy, and provenance to `manifest.json`.
- Added unit tests for malformed data, duplicate labels, repeatability, and test-set isolation.

## Pending

The raw BANKING77 files are intentionally not included in this repository.
Before running preparation, verify the source terms and record an exact source
commit or snapshot using the command in `data/README.md`. No model selection or
test-set evaluation has been performed.
