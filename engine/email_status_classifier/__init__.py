"""Utilities for the job email status classifier."""

from .classifier import (
    LABELS,
    EmailStatusClassifier,
    EmailStatusExample,
    combine_email_fields,
    load_jsonl_dataset,
)

__all__ = [
    "LABELS",
    "EmailStatusClassifier",
    "EmailStatusExample",
    "combine_email_fields",
    "load_jsonl_dataset",
]
