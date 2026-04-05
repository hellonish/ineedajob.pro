---
name: extract-job
description: Extracts structured JobListing (title, company, qualifications, skills, responsibilities) from raw job posting text using an LLM. Use when parsing job postings into the project's JobListing model for comparing an applicant's profile (Person) to the job; call extract_job(content, llm) or use job_listing_from_dict(raw) for dict-to-model conversion.
---

# Extract Job

## Purpose

Takes raw job posting content (pasted text, scraped HTML text, or API response) and an LLM client, and returns a fully populated `JobListing` from `models.models`. The extraction is tuned for **profile comparison**: qualifications (required and preferred), skills tags, and responsibilities are extracted so they can be matched against a candidate's `Person` profile (education, experience, skills).

## Usage

```python
from skills import extract_job
from llm import OpenAIClient  # or AnthropicClient, GeminiClient, DeepSeekClient

llm = OpenAIClient()
job = extract_job("Job posting text here...", llm)
# Compare to Person:
# - job.qualifications_required / qualifications_preferred vs person educations, experiences, skills
# - job.skills_tags vs person.skills
# - job.responsibilities vs person experiences[].description
# - job.experience_level vs person experience tenure
```

From a dict (e.g. cached or from another source):

```python
from skills import job_listing_from_dict

job = job_listing_from_dict({"job_title": "Engineer", "company": {"name": "Acme"}, ...})
```

## Implementation

- **Prompt and schema:** `skills/extract_job/prompts.py` — `EXTRACT_JOB_SYSTEM` defines the output JSON schema and rules for profile-comparison quality (one requirement per item, all skills/tags, distinct responsibilities).
- **Extraction and normalization:** `skills/extract_job/extractor.py` — `extract_job(content, llm, ...)` calls the LLM and normalizes the response into `JobListing` (including nested `Company`, `Compensation`, `H1BSponsorship`, `PlatformMetadata`). `job_listing_from_dict(raw)` builds `JobListing` from a dict.
- **Contract:** Same as extract-person: any client with `generate_structured(messages, model=..., **kwargs) -> dict` works.

## Key fields for profile comparison

| JobListing field | Compare against Person |
|------------------|------------------------|
| `qualifications_required` | Education (degree, field), experience (years, title), certifications, skills |
| `qualifications_preferred` | Same as above; treat as softer match |
| `skills_tags` | `person.skills` (SkillGroup), experiences[].skills, projects[].skills |
| `responsibilities` | experiences[].description, projects[].description |
| `experience_level` | Inferred from experiences (start_date/end_date), title seniority |

## High-quality extraction rules (in prompt)

- One requirement per list item for `qualifications_required` and `qualifications_preferred`; do not merge.
- Extract every technology/tool/keyword into `skills_tags` for matching.
- Each distinct duty as its own string in `responsibilities`.
- Do not infer requirements not stated; use `[]` or `null` when unknown.
