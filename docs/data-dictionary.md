# Data dictionary

## BANKING77 preparation input

The offline preparation pipeline reads two published CSV files. Both files
must contain the following columns and UTF-8 text:

| Column     | Type   | Constraints                                                   |
| ---------- | ------ | ------------------------------------------------------------- |
| `text`     | string | Non-blank user utterance; used as the only classifier feature |
| `category` | string | Non-blank intent label; 77 labels for BANKING77               |

The source audit records row counts, unique texts, duplicate rows, conflicting
duplicate labels, blank values, label distribution, and text-length summary.
The stable label map is alphabetical and is stored in the generated manifest.

## Prepared files

Each generated JSONL record contains:

| Field      | Type    | Meaning                               |
| ---------- | ------- | ------------------------------------- |
| `text`     | string  | Original utterance                    |
| `label`    | string  | Original `category` value             |
| `label_id` | integer | Stable ID from the manifest label map |

`train.jsonl` and `validation.jsonl` are created only from the published
training file. `test.jsonl` is copied from the published test file and remains
untouched until the final evaluation decision is frozen. The manifest stores
the source revision, source-file SHA-256 digests, split seed, validation
fraction, counts, audits, and prepared-file digests.

## Application schema status

No product tables exist yet. The baseline migration initializes Alembic
history only. Define users, ticket ownership, predictions, policy
versions/chunks, drafts, reviews, and audit events with their migrations during
the database phase in the masterplan.
