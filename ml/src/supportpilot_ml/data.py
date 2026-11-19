"""Load, audit, and deterministically split the BANKING77 dataset.

The module deliberately uses only the Python standard library. Training
dependencies are optional, but dataset preparation must remain available in a
clean development environment and must not silently inspect the published
test split when creating validation data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

BANKING77_LABEL_COUNT = 77
DEFAULT_DATASET_NAME = "BANKING77"
DEFAULT_SOURCE_URL = "https://github.com/PolyAI-LDN/task-specific-datasets/tree/master/banking_data"
DEFAULT_SOURCE_LICENSE = "Verify the source dataset terms before redistribution."


@dataclass(frozen=True, slots=True)
class Example:
    """One labeled text example from a published dataset split."""

    text: str
    label: str


@dataclass(frozen=True, slots=True)
class TextLengthStats:
    minimum: int
    maximum: int
    mean: float


@dataclass(frozen=True, slots=True)
class DatasetAudit:
    """Small, JSON-serializable audit report for one dataset split."""

    rows: int
    unique_texts: int
    duplicate_text_rows: int
    conflicting_duplicate_texts: int
    blank_text_rows: int
    blank_label_rows: int
    label_counts: dict[str, int]
    text_length: TextLengthStats


class DatasetValidationError(ValueError):
    """Raised when source data violates a preparation invariant."""


def load_banking77_csv(path: Path) -> list[Example]:
    """Load a BANKING77-compatible CSV with ``text`` and ``category`` columns."""

    with path.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        fieldnames = set(reader.fieldnames or [])
        missing = {"text", "category"} - fieldnames
        if missing:
            missing_columns = ", ".join(sorted(missing))
            raise DatasetValidationError(f"{path} is missing required column(s): {missing_columns}")

        examples: list[Example] = []
        for row_number, row in enumerate(reader, start=2):
            text = row.get("text")
            label = row.get("category")
            if text is None or label is None:
                raise DatasetValidationError(f"{path}:{row_number} has a malformed row")
            examples.append(Example(text=text, label=label))
    return examples


def audit_examples(examples: Sequence[Example]) -> DatasetAudit:
    """Return integrity and distribution statistics without changing examples."""

    text_counts = Counter(example.text for example in examples)
    conflicting_labels: dict[str, set[str]] = defaultdict(set)
    for example in examples:
        conflicting_labels[example.text].add(example.label)

    lengths = [len(example.text) for example in examples]
    text_length = TextLengthStats(
        minimum=min(lengths, default=0),
        maximum=max(lengths, default=0),
        mean=round(sum(lengths) / len(lengths), 2) if lengths else 0.0,
    )
    return DatasetAudit(
        rows=len(examples),
        unique_texts=len(text_counts),
        duplicate_text_rows=sum(count - 1 for count in text_counts.values() if count > 1),
        conflicting_duplicate_texts=sum(
            1 for labels in conflicting_labels.values() if len(labels) > 1
        ),
        blank_text_rows=sum(not example.text.strip() for example in examples),
        blank_label_rows=sum(not example.label.strip() for example in examples),
        label_counts=dict(sorted(Counter(example.label for example in examples).items())),
        text_length=text_length,
    )


def validate_examples(
    examples: Sequence[Example],
    *,
    split_name: str,
    expected_label_count: int | None = None,
) -> None:
    """Validate required fields and label consistency for one source split."""

    if not examples:
        raise DatasetValidationError(f"{split_name} is empty")

    audit = audit_examples(examples)
    if audit.blank_text_rows:
        raise DatasetValidationError(
            f"{split_name} contains {audit.blank_text_rows} blank text row(s)"
        )
    if audit.blank_label_rows:
        raise DatasetValidationError(
            f"{split_name} contains {audit.blank_label_rows} blank label row(s)"
        )
    if audit.conflicting_duplicate_texts:
        raise DatasetValidationError(
            f"{split_name} contains {audit.conflicting_duplicate_texts} text(s) "
            "with conflicting labels"
        )
    if expected_label_count is not None and len(audit.label_counts) != expected_label_count:
        raise DatasetValidationError(
            f"{split_name} has {len(audit.label_counts)} labels; expected {expected_label_count}"
        )


def build_label_map(examples: Sequence[Example]) -> dict[str, int]:
    """Build the stable alphabetical label-to-id mapping used by later training."""

    labels = sorted({example.label for example in examples})
    if not labels:
        raise DatasetValidationError("Cannot build a label map from an empty dataset")
    return {label: index for index, label in enumerate(labels)}


def _split_groups(examples: Sequence[Example]) -> dict[str, list[list[Example]]]:
    grouped: dict[str, dict[str, list[Example]]] = defaultdict(lambda: defaultdict(list))
    for example in examples:
        grouped[example.label][example.text].append(example)
    return {
        label: [grouped[label][text] for text in sorted(grouped[label])]
        for label in sorted(grouped)
    }


def stratified_split(
    examples: Sequence[Example],
    *,
    validation_fraction: float = 0.2,
    seed: int = 42,
) -> tuple[list[Example], list[Example]]:
    """Create a deterministic label-stratified split from one published split.

    Duplicate texts are treated as indivisible groups, preventing the same
    utterance from appearing in both train and validation. A singleton label
    remains in train because it cannot support a meaningful validation example.
    """

    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be between 0 and 1")
    validate_examples(examples, split_name="published train")

    rng = random.Random(seed)
    train: list[Example] = []
    validation: list[Example] = []
    for groups in _split_groups(examples).values():
        shuffled_groups = list(groups)
        rng.shuffle(shuffled_groups)
        label_rows = sum(len(group) for group in shuffled_groups)
        target = round(label_rows * validation_fraction)
        target = min(max(target, 1), label_rows - 1) if label_rows > 1 else 0

        selected_rows = 0
        for group in shuffled_groups:
            remaining_rows = label_rows - selected_rows - len(group)
            should_select = (
                target > 0
                and selected_rows < target
                and remaining_rows >= 0
                and (selected_rows + len(group) <= target or selected_rows == 0)
            )
            if should_select and remaining_rows > 0:
                validation.extend(group)
                selected_rows += len(group)
            else:
                train.extend(group)

    if not train or not validation:
        raise DatasetValidationError(
            "stratified split must produce non-empty train and validation sets"
        )
    return train, validation


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a local source file."""

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_jsonl(path: Path, examples: Sequence[Example], label_map: dict[str, int]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as output:
        for example in examples:
            record = {
                "label": example.label,
                "label_id": label_map[example.label],
                "text": example.text,
            }
            output.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def prepare_dataset(
    *,
    train_csv: Path,
    test_csv: Path,
    output_dir: Path,
    source_url: str = DEFAULT_SOURCE_URL,
    source_revision: str,
    source_license: str = DEFAULT_SOURCE_LICENSE,
    validation_fraction: float = 0.2,
    seed: int = 42,
    dataset_name: str = DEFAULT_DATASET_NAME,
) -> Path:
    """Audit source files, create train/validation JSONL, and write a manifest."""

    published_train = load_banking77_csv(train_csv)
    published_test = load_banking77_csv(test_csv)
    expected_label_count = BANKING77_LABEL_COUNT if dataset_name == DEFAULT_DATASET_NAME else None
    validate_examples(
        published_train,
        split_name="published train",
        expected_label_count=expected_label_count,
    )
    validate_examples(
        published_test,
        split_name="published test",
        expected_label_count=expected_label_count,
    )

    train_labels = {example.label for example in published_train}
    test_labels = {example.label for example in published_test}
    if train_labels != test_labels:
        raise DatasetValidationError("published train and test label sets differ")

    train, validation = stratified_split(
        published_train,
        validation_fraction=validation_fraction,
        seed=seed,
    )
    label_map = build_label_map(published_train)
    output_dir.mkdir(parents=True, exist_ok=True)

    split_paths = {
        "train": output_dir / "train.jsonl",
        "validation": output_dir / "validation.jsonl",
        "test": output_dir / "test.jsonl",
    }
    _write_jsonl(split_paths["train"], train, label_map)
    _write_jsonl(split_paths["validation"], validation, label_map)
    _write_jsonl(split_paths["test"], published_test, label_map)

    manifest = {
        "dataset": dataset_name,
        "source": {
            "url": source_url,
            "revision": source_revision,
            "license_or_terms": source_license,
            "attribution": "PolyAI and the BANKING77 dataset authors",
        },
        "schema": {
            "text_column": "text",
            "label_column": "category",
            "label_count": len(label_map),
            "label_map": label_map,
        },
        "audit": {
            "published_train": asdict(audit_examples(published_train)),
            "published_test": asdict(audit_examples(published_test)),
        },
        "split": {
            "seed": seed,
            "validation_fraction": validation_fraction,
            "validation_source": "published train only",
            "published_test_used_for_model_selection": False,
        },
        "counts": {
            "train": len(train),
            "validation": len(validation),
            "test": len(published_test),
        },
        "source_files": {
            "train_csv": {"name": train_csv.name, "sha256": sha256_file(train_csv)},
            "test_csv": {"name": test_csv.name, "sha256": sha256_file(test_csv)},
        },
        "prepared_files": {
            name: {"name": path.name, "sha256": sha256_file(path)}
            for name, path in split_paths.items()
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-csv", type=Path, required=True)
    parser.add_argument("--test-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--source-license", default=DEFAULT_SOURCE_LICENSE)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dataset-name", default=DEFAULT_DATASET_NAME)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    manifest_path = prepare_dataset(
        train_csv=args.train_csv,
        test_csv=args.test_csv,
        output_dir=args.output_dir,
        source_url=args.source_url,
        source_revision=args.source_revision,
        source_license=args.source_license,
        validation_fraction=args.validation_fraction,
        seed=args.seed,
        dataset_name=args.dataset_name,
    )
    print(f"Wrote dataset manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
