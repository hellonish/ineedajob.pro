#!/usr/bin/env python3
"""Train or use the job email status classifier.

Simple pipeline:
1. Read labeled emails from JSONL.
2. Combine subject + sender + body into one text string.
3. Convert text into TF-IDF vectors.
4. Train RandomForest on those vectors.
5. Save vectorizer + model together in model.pkl.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


# Let this script import the local engine package when run from repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
        precision_recall_fscore_support,
    )
except ImportError as exc:
    raise SystemExit(
        "Missing ML dependency. Run:\n"
        "  pip install -r requirements.txt\n\n"
        f"Import error: {exc}"
    ) from exc


from engine.email_status_classifier import LABELS, EmailStatusClassifier, load_jsonl_dataset
from engine.email_status_classifier.classifier import (
    build_vectorizer,
    combine_email_fields,
    ids_to_labels,
    labels_to_ids,
    write_json,
)


DEFAULT_TRAIN_PATH = PROJECT_ROOT / "data" / "email_status_dataset" / "train.jsonl"
DEFAULT_TEST_PATH = PROJECT_ROOT / "data" / "email_status_dataset" / "test.jsonl"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "models" / "email_status_classifier"


# =============================================================================
# CLI params
# =============================================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train, evaluate, or run the job email status classifier."
    )

    # Dataset paths. Each JSONL row should have subject, sender, body, and label.
    parser.add_argument("--train-path", type=Path, default=DEFAULT_TRAIN_PATH)
    parser.add_argument("--test-path", type=Path, default=DEFAULT_TEST_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)

    # Text vectorizer.
    # tensorflow = TensorFlow TextVectorization TF-IDF.
    # sklearn = scikit-learn TfidfVectorizer fallback.
    parser.add_argument("--vectorizer", choices=["tensorflow", "sklearn", "auto"], default="tensorflow")
    parser.add_argument(
        "--max-features",
        type=int,
        default=12000,
        help="Maximum vocabulary size. Bigger keeps more words, but can add noise.",
    )

    # RandomForest params.
    parser.add_argument("--seed", type=int, default=42, help="Makes training repeatable.")
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=300,
        help="Number of trees. More trees are slower but usually more stable.",
    )
    parser.add_argument(
        "--max-depth",
        type=optional_int,
        default=None,
        help="Tree depth. None lets trees grow fully; smaller values reduce overfit.",
    )
    parser.add_argument(
        "--min-samples-leaf",
        type=int,
        default=1,
        help="Minimum rows in a final tree leaf. Higher values reduce overfit.",
    )
    parser.add_argument(
        "--class-weight",
        default="balanced",
        help='Use "balanced" when classes may be uneven; use "none" to disable.',
    )

    # Inference mode. If any of these are present, the script predicts instead of training.
    parser.add_argument("--predict-text", default=None)
    parser.add_argument("--subject", default="")
    parser.add_argument("--sender", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--model-path", type=Path, default=None)

    return parser.parse_args()


# =============================================================================
# Main switch: train mode or prediction mode
# =============================================================================


def main() -> int:
    args = parse_args()
    model_path = args.model_path or args.output_dir / "model.pkl"

    if args.predict_text is not None or args.subject or args.sender or args.body:
        predict_one_email(args, model_path)
    else:
        train_and_evaluate(args, model_path)

    return 0


# =============================================================================
# Training
# =============================================================================


def train_and_evaluate(args: argparse.Namespace, model_path: Path) -> None:
    # 1. Read dataset rows.
    train_examples = load_jsonl_dataset(args.train_path)
    test_examples = load_jsonl_dataset(args.test_path)

    # 2. Convert each row into one text field:
    #    "Subject: ...\nSender: ...\nBody: ..."
    train_texts = [example.text for example in train_examples]
    test_texts = [example.text for example in test_examples]

    # 3. Convert labels into ids RandomForest can train on.
    #    Not Relevant -> 0, Applied -> 1, InProgress -> 2, Rejected -> 3.
    y_train = labels_to_ids([example.label or "" for example in train_examples])
    y_test = labels_to_ids([example.label or "" for example in test_examples])

    # 4. Build text vectorizer.
    #    fit_transform() learns vocabulary/IDF from training emails and converts train text.
    #    transform() converts test emails using the same learned vocabulary/IDF.
    vectorizer, warning = build_vectorizer(args.vectorizer, args.max_features)
    if vectorizer is None:
        raise SystemExit(warning)
    if warning:
        print(f"Note: {warning}", file=sys.stderr)

    x_train = vectorizer.fit_transform(train_texts)
    x_test = vectorizer.transform(test_texts)

    # 5. Train RandomForest.
    #    RandomForest sees only numeric TF-IDF vectors, not raw text.
    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_leaf=args.min_samples_leaf,
        class_weight=parse_class_weight(args.class_weight),
        random_state=args.seed,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    # 6. Predict test data.
    #    This is pure model output. No rule-based postprocessing is mixed in.
    raw_pred_ids = model.predict(x_test)
    predicted_labels = ids_to_labels(raw_pred_ids)
    predicted_ids = labels_to_ids(predicted_labels)

    # 7. Save everything needed later:
    #    model.pkl contains both vectorizer + trained RandomForest.
    classifier = EmailStatusClassifier(vectorizer=vectorizer, model=model)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    classifier.save(model_path)

    metrics = build_metrics(y_test, predicted_ids, args, vectorizer.name, warning)
    write_json(args.output_dir / "metrics.json", metrics)
    write_json(args.output_dir / "label_mapping.json", build_label_mapping())
    write_confusion_matrix(args.output_dir / "confusion_matrix.csv", y_test, predicted_ids)
    write_predictions(args.output_dir / "predictions.jsonl", test_examples, predicted_labels)

    print(f"Saved model: {model_path}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro F1: {metrics['macro']['f1']:.4f}")


# =============================================================================
# Prediction
# =============================================================================


def predict_one_email(args: argparse.Namespace, model_path: Path) -> None:
    if not model_path.exists():
        raise SystemExit(f"Model artifact not found: {model_path}")

    classifier = EmailStatusClassifier.load(model_path)

    if args.predict_text is not None:
        text = args.predict_text
    else:
        text = combine_email_fields(args.subject, args.sender, args.body)

    prediction = classifier.predict_texts([text])[0]
    print(prediction)


# =============================================================================
# Output files
# =============================================================================


def build_metrics(
    y_true: list[int],
    y_pred: list[int],
    args: argparse.Namespace,
    vectorizer_name: str,
    vectorizer_warning: str | None,
) -> dict[str, Any]:
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(range(len(LABELS))),
        average="macro",
        zero_division=0,
    )
    per_class = classification_report(
        y_true,
        y_pred,
        labels=list(range(len(LABELS))),
        target_names=LABELS,
        output_dict=True,
        zero_division=0,
    )

    return {
        "labels": LABELS,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro": {
            "precision": float(macro_precision),
            "recall": float(macro_recall),
            "f1": float(macro_f1),
        },
        "per_class": {
            label: {
                "precision": float(per_class[label]["precision"]),
                "recall": float(per_class[label]["recall"]),
                "f1": float(per_class[label]["f1-score"]),
                "support": int(per_class[label]["support"]),
            }
            for label in LABELS
        },
        "training": {
            "train_path": str(args.train_path),
            "test_path": str(args.test_path),
            "vectorizer_used": vectorizer_name,
            "vectorizer_warning": vectorizer_warning,
            "max_features": args.max_features,
            "n_estimators": args.n_estimators,
            "max_depth": args.max_depth,
            "min_samples_leaf": args.min_samples_leaf,
            "class_weight": args.class_weight,
            "seed": args.seed,
            "postprocessing": "none",
        },
    }


def write_confusion_matrix(path: Path, y_true: list[int], y_pred: list[int]) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=list(range(len(LABELS))))

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["actual\\predicted", *LABELS])
        for label, row in zip(LABELS, matrix):
            writer.writerow([label, *[int(value) for value in row]])


def write_predictions(
    path: Path,
    examples: list[Any],
    predicted_labels: list[str],
) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for example, predicted_label in zip(examples, predicted_labels):
            row = {
                "subject": example.subject,
                "sender": example.sender,
                "true_label": example.label,
                "prediction": predicted_label,
            }
            if example.metadata:
                row["metadata"] = example.metadata
            handle.write(json.dumps(row, sort_keys=True) + "\n")


# =============================================================================
# Tiny parsing helpers
# =============================================================================


def optional_int(value: str) -> int | None:
    if value.lower() in {"none", "null", ""}:
        return None
    return int(value)


def parse_class_weight(value: str) -> str | None:
    if value.lower() in {"none", "null", ""}:
        return None
    return value


def build_label_mapping() -> dict[str, Any]:
    return {
        "labels": LABELS,
        "label_to_id": {label: index for index, label in enumerate(LABELS)},
    }


if __name__ == "__main__":
    raise SystemExit(main())
