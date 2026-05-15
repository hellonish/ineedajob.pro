"""Training and inference helpers for job email status classification.

The primary model is a RandomForest classifier. TensorFlow is optional and is
only used as a TF-IDF feature builder through Keras TextVectorization when the
runtime has TensorFlow installed. The scikit-learn TF-IDF path stays available
because TensorFlow is a heavy dependency for this project.
"""

from __future__ import annotations

import json
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


LABELS = ["Not Relevant", "Applied", "InProgress", "Rejected"]
LABEL_TO_ID = {label: index for index, label in enumerate(LABELS)}
ID_TO_LABEL = {index: label for label, index in LABEL_TO_ID.items()}


@dataclass(frozen=True)
class EmailStatusExample:
    subject: str
    sender: str
    body: str
    label: str | None = None
    metadata: dict[str, Any] | None = None

    @property
    def text(self) -> str:
        return combine_email_fields(self.subject, self.sender, self.body)


def combine_email_fields(subject: str = "", sender: str = "", body: str = "") -> str:
    """Create a stable text representation from email fields."""
    return "\n".join(
        [
            f"Subject: {_clean_text(subject)}",
            f"Sender: {_clean_text(sender)}",
            f"Body: {_clean_text(body)}",
        ]
    )


def load_jsonl_dataset(path: str | Path, require_label: bool = True) -> list[EmailStatusExample]:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    examples: list[EmailStatusExample] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{dataset_path}:{line_number} is not valid JSON") from exc

            label = _extract_label(row)
            if require_label and label is None:
                raise ValueError(f"{dataset_path}:{line_number} is missing a label/status field")
            if label is not None and label not in LABEL_TO_ID:
                raise ValueError(
                    f"{dataset_path}:{line_number} has unsupported label {label!r}; "
                    f"expected one of {LABELS}"
                )

            examples.append(
                EmailStatusExample(
                    subject=str(row.get("subject") or ""),
                    sender=str(row.get("sender") or row.get("from") or ""),
                    body=str(row.get("body") or row.get("text") or ""),
                    label=label,
                    metadata={key: value for key, value in row.items() if key not in {"subject", "sender", "from", "body", "text", "label", "status"}},
                )
            )

    if not examples:
        raise ValueError(f"Dataset file has no examples: {dataset_path}")
    return examples


class SklearnTfidfVectorizer:
    name = "sklearn"

    def __init__(self, max_features: int):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            min_df=1,
            strip_accents="unicode",
            lowercase=True,
            sublinear_tf=True,
        )

    def fit_transform(self, texts: Sequence[str]):
        return self.vectorizer.fit_transform(texts)

    def transform(self, texts: Sequence[str]):
        return self.vectorizer.transform(texts)


class TensorFlowTfidfVectorizer:
    name = "tensorflow"

    def __init__(self, max_features: int):
        import tensorflow as tf

        # max_features = max vocabulary size.
        # Example: 12000 means keep up to 12k useful words/tokens from training emails.
        self.max_features = max_features
        self._tf = tf
        self.vectorizer = self._build_layer()

    def __getstate__(self) -> dict[str, Any]:
        # pickle cannot safely store the whole TensorFlow layer state by itself.
        # So we manually save the two things needed for future predictions:
        # 1. vocabulary: word -> vector position
        # 2. idf_weights: word importance for TF-IDF
        idf_weights = None
        lookup_layer = getattr(self.vectorizer, "_lookup_layer", None)
        if lookup_layer is not None and getattr(lookup_layer, "idf_weights", None) is not None:
            idf_weights = lookup_layer.idf_weights.numpy().tolist()
        return {
            "max_features": self.max_features,
            "vocabulary": self.vectorizer.get_vocabulary(),
            "idf_weights": idf_weights,
        }

    def __setstate__(self, state: dict[str, Any]) -> None:
        import tensorflow as tf

        # Rebuild the TensorFlow vectorizer when model.pkl is loaded.
        # Then put back the exact same vocabulary + IDF weights from training.
        self.max_features = state["max_features"]
        self._tf = tf
        self.vectorizer = self._build_layer()
        idf_weights = state.get("idf_weights")
        if idf_weights is not None:
            self.vectorizer.set_vocabulary(
                state["vocabulary"],
                idf_weights=self._tf.constant(idf_weights, dtype=self._tf.float32),
            )
        else:
            self.vectorizer.set_vocabulary(state["vocabulary"])

    def _build_layer(self):
        # output_mode="tf_idf" means the vector is not just word count.
        # It gives more weight to words that are important/rare across emails.
        # ngrams=(1, 2) keeps single words and two-word phrases.
        # That matters for this task because "moving forward", "job alert",
        # and "application received" carry more meaning than each word alone.
        return self._tf.keras.layers.TextVectorization(
            max_tokens=self.max_features,
            ngrams=(1, 2),
            output_mode="tf_idf",
            standardize="lower_and_strip_punctuation",
        )

    def fit_transform(self, texts: Sequence[str]):
        # Training only:
        # adapt() reads the training emails and learns vocabulary + IDF weights.
        # batch(128) just feeds emails to TensorFlow in chunks instead of one by one.
        dataset = self._tf.data.Dataset.from_tensor_slices(list(texts)).batch(128)
        self.vectorizer.adapt(dataset)
        return self.transform(texts)

    def transform(self, texts: Sequence[str]):
        # Prediction/test:
        # use the vocabulary + IDF already learned by adapt().
        # Do not call adapt() here, or vector positions would change.
        features = self.vectorizer(self._tf.constant(list(texts)))
        return features.numpy()


class EmailStatusClassifier:
    """Serializable RandomForest email status classifier."""

    def __init__(self, vectorizer: Any, model: Any):
        self.vectorizer = vectorizer
        self.model = model

    def predict_texts(self, texts: Sequence[str]) -> list[str]:
        # Text -> TF-IDF vector -> RandomForest class id -> label name.
        features = self.vectorizer.transform(texts)
        raw_ids = self.model.predict(features)
        return [ID_TO_LABEL[int(label_id)] for label_id in raw_ids]

    def predict_email(
        self,
        subject: str = "",
        sender: str = "",
        body: str = "",
    ) -> str:
        text = combine_email_fields(subject=subject, sender=sender, body=body)
        return self.predict_texts([text])[0]

    def save(self, path: str | Path) -> None:
        with Path(path).open("wb") as handle:
            pickle.dump(self, handle)

    @classmethod
    def load(cls, path: str | Path) -> "EmailStatusClassifier":
        with Path(path).open("rb") as handle:
            loaded = pickle.load(handle)
        if not isinstance(loaded, cls):
            raise TypeError(f"Artifact at {path} is not an EmailStatusClassifier")
        return loaded


def build_vectorizer(choice: str, max_features: int):
    normalized = choice.lower()
    if normalized == "sklearn":
        return SklearnTfidfVectorizer(max_features=max_features), None
    if normalized == "tensorflow":
        try:
            return TensorFlowTfidfVectorizer(max_features=max_features), None
        except ImportError as exc:
            return None, (
                "TensorFlow is not installed, so Keras TextVectorization cannot be used. "
                "Install TensorFlow separately or run with --vectorizer sklearn."
            )
    if normalized == "auto":
        try:
            return TensorFlowTfidfVectorizer(max_features=max_features), None
        except ImportError:
            return SklearnTfidfVectorizer(max_features=max_features), (
                "TensorFlow is not installed; using scikit-learn TF-IDF fallback."
            )
    raise ValueError("vectorizer must be one of: auto, tensorflow, sklearn")


def labels_to_ids(labels: Iterable[str]) -> list[int]:
    return [LABEL_TO_ID[label] for label in labels]


def ids_to_labels(label_ids: Iterable[int]) -> list[str]:
    return [ID_TO_LABEL[int(label_id)] for label_id in label_ids]


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _extract_label(row: dict[str, Any]) -> str | None:
    raw_label = row.get("label", row.get("status"))
    if raw_label is None:
        return None
    label = str(raw_label).strip()
    aliases = {
        "not_relevant": "Not Relevant",
        "not relevant": "Not Relevant",
        "irrelevant": "Not Relevant",
        "applied": "Applied",
        "in_progress": "InProgress",
        "inprogress": "InProgress",
        "in progress": "InProgress",
        "interview": "InProgress",
        "assessment": "InProgress",
        "rejected": "Rejected",
        "rejection": "Rejected",
    }
    return aliases.get(label.lower(), label)


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()
