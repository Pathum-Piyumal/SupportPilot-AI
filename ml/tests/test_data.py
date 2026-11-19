import csv
import json
from pathlib import Path

import pytest
from supportpilot_ml.data import (
    DatasetValidationError,
    Example,
    audit_examples,
    prepare_dataset,
    stratified_split,
    validate_examples,
)


def test_audit_reports_duplicates_and_text_lengths() -> None:
    examples = [
        Example("same", "a"),
        Example("same", "a"),
        Example("other", "b"),
    ]

    audit = audit_examples(examples)

    assert audit.rows == 3
    assert audit.unique_texts == 2
    assert audit.duplicate_text_rows == 1
    assert audit.conflicting_duplicate_texts == 0
    assert audit.text_length.minimum == 4
    assert audit.text_length.maximum == 5


def test_conflicting_duplicate_labels_are_rejected() -> None:
    examples = [Example("same", "a"), Example("same", "b")]

    with pytest.raises(DatasetValidationError, match="conflicting labels"):
        validate_examples(examples, split_name="fixture")


def test_stratified_split_is_repeatable_and_keeps_duplicate_texts_together() -> None:
    examples = [
        Example("a1", "a"),
        Example("a2", "a"),
        Example("a2", "a"),
        Example("a3", "a"),
        Example("b1", "b"),
        Example("b2", "b"),
        Example("b3", "b"),
        Example("b4", "b"),
    ]

    first = stratified_split(examples, validation_fraction=0.25, seed=7)
    second = stratified_split(examples, validation_fraction=0.25, seed=7)

    assert first == second
    train, validation = first
    assert {example.text for example in train}.isdisjoint(example.text for example in validation)
    assert {example.label for example in train} == {"a", "b"}
    assert {example.label for example in validation} == {"a", "b"}


def _write_source_csv(path: Path, rows: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["text", "category"])
        writer.writeheader()
        writer.writerows({"text": text, "category": label} for text, label in rows)


def test_prepare_dataset_writes_reproducible_manifest_without_using_test_for_validation(
    tmp_path: Path,
) -> None:
    train_csv = tmp_path / "train.csv"
    test_csv = tmp_path / "test.csv"
    output_dir = tmp_path / "prepared"
    _write_source_csv(
        train_csv,
        [("a1", "a"), ("a2", "a"), ("a3", "a"), ("b1", "b"), ("b2", "b"), ("b3", "b")],
    )
    _write_source_csv(test_csv, [("a-test", "a"), ("b-test", "b")])

    manifest_path = prepare_dataset(
        train_csv=train_csv,
        test_csv=test_csv,
        output_dir=output_dir,
        source_url="fixture://banking77",
        source_revision="fixture-revision",
        source_license="fixture-only",
        validation_fraction=0.34,
        seed=11,
        dataset_name="fixture",
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["split"]["published_test_used_for_model_selection"] is False
    assert manifest["split"]["validation_source"] == "published train only"
    assert manifest["counts"]["test"] == 2
    assert manifest["source"]["revision"] == "fixture-revision"
    assert (output_dir / "train.jsonl").exists()
    assert (output_dir / "validation.jsonl").exists()
    assert (output_dir / "test.jsonl").exists()
