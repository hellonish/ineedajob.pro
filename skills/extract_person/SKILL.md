---
name: extract-person
description: Extracts structured Person (name, education, experience, skills, etc.) from raw text using an LLM. Use when parsing resumes, portfolio pages, or bios into the project's Person model; use parsers.resume.ResumeParser.parse_with_skill (file/stream) or parsers.portfolio.PortfolioParser.parse_with_skill (URL) for entry points.
---

# Extract Person

## Purpose

Takes raw content (resume text, portfolio HTML text, bio) and an LLM client, returns a fully populated `Person` from `models.models`. Uses the base LLM interface so any provider (OpenAI, Anthropic, Gemini, DeepSeek) can be used.

## Usage

**Skill only (you have raw text):**
```python
from skills import extract_person
from llm import OpenAIClient  # or AnthropicClient, GeminiClient, DeepSeekClient

llm = OpenAIClient()
person = extract_person("Resume or bio text here...", llm)
```

**Entry points (file/stream or URL):**
```python
from parsers import ResumeParser, PortfolioParser

person = ResumeParser().parse_with_skill("resume.pdf", llm)   # or file stream / bytes for API
person = PortfolioParser().parse_with_skill("https://example.com", llm)
```

## Implementation

- Prompt and schema live in `skills/extract_person/prompts.py`.
- Extraction and dict→Person normalization in `skills/extract_person/extractor.py`.
- Resume parser uses the skill in `parsers/resume/parser.py` (parse_with_skill); portfolio in `parsers/portfolio/parser.py` (parse_with_skill).
