# Email Status Classifier

A small model that reads an email and predicts where it belongs in the job-search pipeline.

## Classes

- `Not Relevant`
  - Job alerts, recommendations, newsletters, hiring events, marketing emails, or generic recruiter spam.
  - The key idea: it is not about a real application that was already submitted.

- `Applied`
  - The company or platform confirms the application was submitted or received.
  - No interview, assessment, recruiter reply, or real next step yet.

- `InProgress`
  - Something happened after applying.
  - Examples: interview scheduling, assessment invite, recruiter reply, availability request, next-step email.

- `Rejected`
  - The company clearly says they are not moving forward.
  - Also covers role filled, not selected, hiring paused, or application path closed.

## What The Model File Contains

- Saved file: `classifier_model/model.pkl`
- Wrapper class: `EmailStatusClassifier`
- Inside it:
  - TensorFlow `TextVectorization` layer
  - scikit-learn `RandomForestClassifier`

Flow:

```text
email text -> TF-IDF vectorizer -> RandomForest -> class label
```

There is no rule-based guardrail layer now. The prediction is model output only.

## Usage

Terminal:

```bash
.venv/bin/python scripts/train_email_status_classifier.py \
  --model-path classifier_model/model.pkl \
  --subject "Update on your application" \
  --sender "recruiting@company.com" \
  --body "Unfortunately, we will not be moving forward with your application at this time."
```

Python:

```python
from engine.email_status_classifier import EmailStatusClassifier

clf = EmailStatusClassifier.load("classifier_model/model.pkl")

label = clf.predict_email(
    subject="Schedule your interview",
    sender="recruiting@company.com",
    body="Thanks for applying. We reviewed your application and would like to schedule your first interview.",
)

print(label)
```

Batch prediction:

```python
texts = [
    "Subject: Jobs for you\nSender: LinkedIn\nBody: Recommended jobs based on your activity. View all jobs.",
    "Subject: Application received\nSender: no-reply@company.com\nBody: Thank you for applying. Your application was submitted.",
]

labels = clf.predict_texts(texts)
print(labels)
```

## Size And Latency

- Model size: `820 KB`
- Load time: about `4.2 seconds`
- Predict 300 emails: about `0.064 seconds`
- Per email in a batch: about `0.21 ms`
- Single email after load: about `18 ms`

The slow part is loading TensorFlow and the saved vectorizer. After loading, prediction is fast.

Use it this way:

- Good: load once, predict many emails.
- Bad: load the model again for every single email.

## Current Test Result

- Accuracy: `1.0`
- Macro F1: `1.0`
- Postprocessing: `none`

This score is on the synthetic test dataset, not real Gmail data. For real quality, the next step is testing on real emails and adding missed patterns back into the labeled dataset.
