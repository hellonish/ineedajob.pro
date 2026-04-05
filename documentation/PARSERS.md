# How the parsers are created and how they work

This document describes how the **resume** and **portfolio** parsers are built and how they behave end-to-end.

---

## Overview

There are two parsers:

| Parser        | Input              | Output (raw)     | Output (with skill) |
|---------------|--------------------|------------------|----------------------|
| **Resume**    | File path or stream (PDF/DOCX) | `Person` with only `summary` filled | `Person` (full)      |
| **Portfolio** | URL (string)       | `ParsedPortfolio` (title, description, links, sections) | `Person` (full)      |

Both can run in two modes:

1. **Raw mode** – Extract content only; no LLM. Resume returns a `Person` with `summary` set to the extracted text; portfolio returns a `ParsedPortfolio` object.
2. **Skill mode** – Same content extraction, then the **extract-person skill** (LLM) turns that content into a fully structured `Person`.

The output model is always `Person` from `models.models` (or `ParsedPortfolio` for portfolio in raw mode).

---

## Resume parser

**Location:** `parsers/resume/parser.py`

### How it is built

1. **Input handling**  
   The parser accepts a **source** that can be:
   - A **file path** (`str` or `pathlib.Path`) – for local scripts and tests.
   - A **binary stream** (e.g. `UploadFile` from FastAPI) – for API uploads.
   - **Raw bytes** (e.g. `await file.read()`) – for API use when you already have the file in memory.

2. **Format detection**  
   Format is detected from **magic bytes**, not the file extension:
   - `%PDF` → PDF (handled with `pypdf`).
   - `PK\x03\x04` (ZIP) → DOCX (handled with `python-docx`).  
   Anything else is treated as unsupported and raises `ValueError`.

3. **Text extraction**
   - **PDF:** `pypdf.PdfReader` reads the stream; text is taken from each page with `extract_text()` and concatenated with `"\n\n"`.
   - **DOCX:** `python-docx.Document` reads the stream; paragraph text is collected and joined with `"\n\n"`.

4. **Raw vs skill**
   - **`parse(source)`** – Returns a `Person` with `summary` set to the extracted text and all other fields empty (defaults).
   - **`parse_with_skill(source, llm, model=None, **kwargs)`** – Calls `parse(source)` to get that `Person`, then passes `person.summary` to the extract-person skill and returns the skill’s `Person` (fully structured).

### Flow (with skill)

```
source (path / stream / bytes)
    → read bytes, detect PDF vs DOCX
    → extract text (pypdf or python-docx)
    → Person(summary=raw_text)  [raw]
    → extract_person(raw_text, llm)  [skill]
    → Person (full)
```

### Usage

```python
from parsers import ResumeParser
from llm import GeminiClient  # or OpenAIClient, DeepSeekClient, AnthropicClient

parser = ResumeParser()

# Raw: only extracted text in Person.summary
person_raw = parser.parse("/path/to/resume.pdf")

# Full: structured Person via LLM
llm = GeminiClient()
person = parser.parse_with_skill("/path/to/resume.pdf", llm, model="gemini-2.0-flash")
```

For APIs, pass the uploaded file or its bytes:

```python
person = parser.parse_with_skill(upload_file, llm)  # or await upload_file.read() then parse_with_skill(bytes, llm)
```

---

## Portfolio parser

**Location:** `parsers/portfolio/parser.py`

### How it is built

1. **Input**  
   A single **URL** (`str`) that must start with `http://` or `https://`. Invalid URLs raise `ValueError`.

2. **Fetch and parse**
   - **httpx** is used to GET the URL (with redirects and a configurable timeout).
   - The response body is parsed as HTML with **BeautifulSoup** (`html.parser`).
   - From the DOM we extract:
     - **Title:** `<title>` text.
     - **Description:** `<meta name="description">` or `<meta property="og:description">`.
     - **Links:** All `<a href="...">`, normalized to absolute URLs, with `#`, `mailto:`, `tel:`, `javascript:` filtered out (up to `max_links`, default 200).
     - **Sections:** A linear walk over `<h1>`–`<h6>`, `<p>`, `<li>`; each heading starts a new section key, and following paragraphs/list items are concatenated as that section’s body. Result: `dict[str, str]` (heading → content).

3. **Content blob for the skill**  
   A single string is built for the extract-person skill: title, description, then each section as `## {heading}\n{body}`, then a truncated list of links. This string is what the LLM sees.

4. **Raw vs skill**
   - **`parse(url)`** – Returns a `ParsedPortfolio` (url, title, description, links, sections). No LLM.
   - **`parse_with_skill(url, llm, model=None, **kwargs)`** – Calls `parse(url)`, builds the content blob. If the blob is empty, returns a minimal `Person` (e.g. headline from title, summary from description, website from URL, social_media from links). Otherwise calls the extract-person skill and returns its `Person`.

### Flow (with skill)

```
url (string)
    → httpx.get(url) → HTML
    → BeautifulSoup → title, description, links, sections
    → ParsedPortfolio  [raw]
    → _portfolio_to_content(parsed) → single text blob
    → extract_person(content, llm)  [skill]
    → Person (full)
```

### Usage

```python
from parsers import PortfolioParser
from llm import GeminiClient

parser = PortfolioParser(timeout_seconds=15.0, max_links=200)

# Raw: structured scrape only
parsed = parser.parse("https://example.com")

# Full: Person via LLM
person = parser.parse_with_skill("https://example.com", llm, model="gemini-2.0-flash")
```

---

## Runner scripts and output

- **`python -m parsers.run_resume`** – Loads `.env`, uses `GeminiClient`, runs the resume parser with the skill on `profiles/sharma_nishant.pdf`, and writes the resulting `Person` to **`parsers/resume/output_resume.md`** (Markdown).
- **`python -m parsers.run_portfolio`** – Same idea for a fixed portfolio URL; writes to **`parsers/portfolio/output_portfolio.md`**.

The Markdown is generated by `_person_to_md(person)` in each parser: it dumps the full `Person` (no truncation) into a readable MD structure (headings, lists, links, etc.).

---

## Dependencies

- **Resume:** `pypdf`, `python-docx`
- **Portfolio:** `httpx`, `beautifulsoup4`
- **Both:** `models.models` (Person, SkillGroup, etc.), `skills.extract_person` (for `parse_with_skill`), and an LLM client when using the skill.

---

## Summary

| Aspect        | Resume parser                    | Portfolio parser                |
|---------------|-----------------------------------|---------------------------------|
| **Input**     | Path, stream, or bytes (PDF/DOCX)| URL string                      |
| **Detection** | Magic bytes (PDF vs DOCX)         | N/A                             |
| **Extraction**| pypdf / python-docx               | httpx + BeautifulSoup           |
| **Raw output**| `Person` (summary only)          | `ParsedPortfolio`               |
| **With skill**| `Person` (full)                   | `Person` (full)                 |
| **API use**   | Pass file or bytes               | Pass URL                        |

Both parsers are designed so that **content extraction** is separate from **structure extraction**: the former is deterministic (bytes/HTML → text); the latter is done by the extract-person skill (text + LLM → `Person`).
