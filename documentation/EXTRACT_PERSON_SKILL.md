# Extract-person skill

This document explains the **extract-person** skill: what it does, how it is built, and how to use it.

---

## What the skill does

The skill turns **unstructured text** (e.g. from a resume, portfolio page, or bio) into a **structured `Person`** object from `models.models`.

- **Input:** Raw text (string) and an LLM client that supports structured JSON output.
- **Output:** A single `Person` instance with all fields populated (or set to empty string / empty list when not found).

The skill does **not** fetch URLs or read files. It only takes text and an LLM; parsers (or other code) are responsible for producing that text.

---

## Why it is a “skill”

A **skill** here means a reusable, single-purpose capability that:

1. Has a **fixed contract:** input (content + LLM), output (`Person`).
2. **Encodes the task** in one place: system prompt, output schema, and normalization logic.
3. Is **LLM-agnostic:** it uses whatever client you pass in (OpenAI, Anthropic, Gemini, DeepSeek) as long as it implements `generate_structured(messages, model=..., **kwargs) -> dict`.
4. **Guarantees structure:** it always returns a valid `Person` by normalizing and validating the LLM’s JSON.

So the skill is more than “a prompt”: it is prompt + schema + parsing + validation in one unit.

---

## Components

The skill lives under `skills/extract_person/`:

| File / piece      | Role |
|-------------------|------|
| **`prompts.py`**  | Defines `EXTRACT_PERSON_SYSTEM`: the system prompt that describes the JSON schema and extraction rules (extract everything, preserve wording, use empty string/list when absent, consistent date format, etc.). |
| **`extractor.py`**| Implements `extract_person(content, llm, model=None, **kwargs) -> Person`. Builds messages, calls `llm.generate_structured(...)`, then normalizes the returned dict and constructs a `Person`. |
| **`SKILL.md`**    | Short Cursor/skill metadata and usage reminder. |

There is no separate “schema file”: the schema is described in the system prompt and in `models.models` (Person and nested types). The `Person` model uses `Field(description=...)` so each field’s meaning is clear for both humans and LLMs.

---

## How it works (flow)

1. **Messages**  
   - System: `EXTRACT_PERSON_SYSTEM` (full instructions + JSON shape).  
   - User: `"Extract structured profile data from this content:\n\n" + content`.

2. **LLM call**  
   `llm.generate_structured(messages, model=model, **kwargs)` is called. The client is expected to constrain the model to JSON (e.g. `response_format={"type": "json_object"}` where supported) and return a parsed `dict`.

3. **Normalization**  
   The returned dict may have missing keys, `null`, or wrong types. The extractor:
   - Uses helpers (`_ensure_str`, `_ensure_list`, `_ensure_dict_str_list`) to coerce values.
   - For list fields (educations, experiences, projects, etc.), keeps only elements that are dicts; builds one Pydantic model per dict (`_norm_education`, `_norm_experience`, etc.).
   - Builds a `SkillGroup` from the `skills` dict (category → list of skills).
   - Constructs a single `Person(...)` with these normalized values.

4. **Return**  
   The result is always a valid `Person`. If the LLM returns empty or invalid JSON, the normalizer still produces a `Person` with empty/default fields instead of raising.

---

## System prompt (high level)

`EXTRACT_PERSON_SYSTEM` in `prompts.py`:

- States the task: output one JSON object that matches the given schema.
- Tells the model to extract every fact, use `""` or `[]` when information is absent, preserve exact wording where it matters, and use a consistent date format.
- Describes the full JSON shape: top-level fields (name, headline, summary, location, company, title, email, phone, website, languages, social_media, skills, educations, experiences, projects, extracurriculars, certifications, awards) and the nested structure of each list (e.g. each education has school, degree, field_of_study, start_date, end_date, description, subjects).
- Asks for **only** the JSON object (no markdown or commentary).

The parsers and the skill do not inject the schema a second time; the single source of truth for “what each field means” is the prompt plus `models.models` (with `Field(description=...)` for robustness).

---

## Normalization details

- **Strings:** `None` or non-string → `""`; otherwise stripped.
- **Lists:** `None` or non-list → `[]`; list items that are not dicts are dropped when building nested models.
- **Skills:** Expected to be a dict of the form `{ "category_name": ["skill1", "skill2"] }`; normalized so keys are strings and values are lists of strings.
- **Optional fields** (e.g. `end_date`, `description` on Education/Experience): Kept as `None` when the LLM omits them or sends `null`; otherwise string/list as appropriate.

This keeps the skill robust to partial or messy LLM output while still returning a valid `Person`.

---

## LLM interface

The skill expects an object that implements:

```python
def generate_structured(
    self,
    messages: list[dict[str, str]],
    model: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]: ...
```

So any of the project’s LLM clients (`OpenAIClient`, `AnthropicClient`, `GeminiClient`, `DeepSeekClient`) can be used; the skill does not depend on a specific provider.

---

## Usage

**Standalone (you already have text):**

```python
from skills import extract_person
from llm import GeminiClient

llm = GeminiClient()
person = extract_person("Resume or portfolio text here...", llm)
```

**Via parsers (file or URL → text → Person):**

```python
from parsers import ResumeParser, PortfolioParser
from llm import GeminiClient

llm = GeminiClient()
person = ResumeParser().parse_with_skill("resume.pdf", llm)
person = PortfolioParser().parse_with_skill("https://example.com", llm)
```

Optional arguments (e.g. `model="gemini-2.0-flash"`, `max_tokens=4096`) can be passed as `**kwargs` to `extract_person` and are forwarded to `llm.generate_structured`.

---

## Summary

| Aspect           | Description |
|------------------|-------------|
| **Purpose**      | Unstructured text → structured `Person` (resume/portfolio/bio). |
| **Input**        | `content: str`, `llm`, optional `model` and `**kwargs`. |
| **Output**       | `Person` from `models.models`. |
| **Prompt**       | `prompts.EXTRACT_PERSON_SYSTEM` (schema + rules). |
| **Logic**        | `extractor.extract_person` + normalization in `extractor.py`. |
| **LLM**          | Any client with `generate_structured(...) -> dict`. |
| **Guarantee**    | Always returns a valid `Person`; invalid/missing JSON is normalized to empty/default fields. |

The extract-person skill is the single place that defines “how to turn profile text into a Person.” Parsers and other callers only need to pass text and an LLM.
