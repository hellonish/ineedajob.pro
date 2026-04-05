---
name: resolve-person
description: Merges two Person profiles (e.g. from resume and portfolio) into one canonical Person without losing information. Use when you have two structured profiles of the same person and need a single resolved profile; the LLM evaluates discrepancies (names, dates, duplicates) and merges list fields while choosing best values for conflicting scalars.
---

# Resolve Person

## Purpose

Takes **two** `Person` models (from `models.models`) that describe the same person—e.g. one from a resume and one from a portfolio—and produces **one** merged `Person` in which:

- **No information is lost:** Every distinct education, experience, project, certification, award, and extracurricular from both inputs appears in the output. Duplicates (same real-world entity in both) are merged into a single, best version.
- **Scalar conflicts are resolved:** For name, email, headline, etc., the LLM chooses the best or most complete value when the two profiles differ.
- **Skills, languages, social_media:** Union of both; deduplicated.

## Usage

```python
from skills import resolve_persons
from llm import GeminiClient  # or OpenAIClient, DeepSeekClient, AnthropicClient
from parsers import ResumeParser, PortfolioParser

person_resume = ResumeParser().parse_with_skill("resume.pdf", llm)
person_portfolio = PortfolioParser().parse_with_skill("https://example.com", llm)

llm = GeminiClient()
resolved = resolve_persons(person_resume, person_portfolio, llm)
```

## Implementation

- **Prompt:** `skills/resolve_person/prompts.py` – `RESOLVE_PERSON_SYSTEM` defines merge rules and the output JSON schema.
- **Logic:** `skills/resolve_person/resolver.py` – serializes both Persons to JSON, calls `llm.generate_structured`, then builds a `Person` via `person_from_dict` from the extract-person skill.
- **Contract:** Same as extract-person: any client with `generate_structured(messages, model=..., **kwargs) -> dict` works.

## High-stakes rules (in prompt)

1. List fields: merge both lists; deduplicate only when the same entity (e.g. same job, same degree) appears in both; keep every distinct item.
2. Scalars: when values differ, choose the most complete or canonical value.
3. Summary: combine or keep the richer one so no factual content is dropped.
4. Output: single JSON object matching the Person schema; no markdown.
