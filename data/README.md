# Data

Raw datasets and prepared examples stay local and are ignored by Git. Do not
commit BANKING77, customer data, model artifacts, or generated experiment
logs.

## BANKING77 provenance

The preparation code expects the published BANKING77 CSV shape:

| Column | Meaning |
| --- | --- |
| `text` | User utterance used as the classifier input |
| `category` | One of the 77 intent labels |

Source: [PolyAI task-specific datasets](https://github.com/PolyAI-LDN/task-specific-datasets/tree/master/banking_data).
Record the exact source commit or dataset snapshot, source checksums, and the
terms shown by the source before using the data outside local development.
This repository does not relicense or redistribute the dataset.

Place the downloaded files at `data/raw/banking77/train.csv` and
`data/raw/banking77/test.csv`. The raw directory is intentionally ignored.

## Reproducible preparation

From the repository root, after verifying the source terms:

```powershell
uv run python -m supportpilot_ml.data `
  --train-csv data/raw/banking77/train.csv `
  --test-csv data/raw/banking77/test.csv `
  --output-dir data/prepared/banking77 `
  --source-revision <exact-source-commit-or-snapshot> `
  --source-license <verified-source-terms>
```

The equivalent command works in bash with `\` line continuations. The command
validates required columns, blank rows, conflicting duplicates, label sets and
the expected 77 labels. It creates deterministic `train.jsonl`,
`validation.jsonl`, `test.jsonl`, and `manifest.json` files. Validation is
stratified from the published training split only; the published test split is
copied for the later, single final evaluation and is never used for model
selection.
