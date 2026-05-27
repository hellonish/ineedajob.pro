# HOW_TO_CODE

Rules to follow when coding in this project.

## General

- Keep code simple, clean, and minimal.
- Each file should generally contain only 1 class to maintain separation of responsibilities.
- Methods and functions must remain simple, focused, and clean.
- Keep the codebase DRY (Don't Repeat Yourself). Centralize common utility logic (e.g., Centralized warning deduplication `dedupe_warning_strings` in `engine/utils.py`).
- Remove anything unused or not required.
- After coding, review the files again for unnecessary logic, imports, models, helpers, or tests.
- Prefer small, readable modules with clear responsibilities.
- Encapsulate behavior in classes when logic grows beyond simple wrappers.
- Keep public functions thin when a class owns the implementation.

## LLM Clients and Service Initialization

- When initializing services or generators with LLM clients, use explicit `is None` checks instead of truthy/falsey checks (like `or`).
- This ensures that custom mock/fake LLMs (which may evaluate to falsey, e.g. via `__bool__`) are correctly accepted without triggering fallback initialization of live clients (such as `XAIStructuredClient`).

## Imports

- Keep all imports at the top of the file.
- Do not import inside functions or methods.
- Do not use `try/except` for module imports.
- Do not use `from __future__ import annotations`; newer Python is expected.
- Production code must not import from `documentation/`.

## Docstrings

- Always create docstrings.
- Add Google-style docstrings for modules, classes, public functions, and helper methods.
- Keep docstrings short, functional, and clear.

## Models

- Keep models minimal but effective.
- Avoid extra intermediate models unless they are genuinely needed.
- Model only the data the code actually uses.

## Profile Parser

- Ingestion should only read files into clean text blocks, links, metadata, and source evidence.
- Ingestion should stay programmatic and simple.
- Ingested blocks may be large source containers; extraction owns semantic section splitting.
- Extraction should use ingested content to create the unified profile.
- Keep LLM prompts in dedicated prompt files, not inline inside extraction logic.
- Capture all links, including embedded links and written links.
- Links for projects, portfolios, GitHub, LinkedIn, documents, anchors, and emails should be preserved clearly.
- Use injected fake LLM clients in tests when validating parser behavior without spending X.AI tokens.
- Unified profile output should use explicit top-level section keys and field names, not generic section/content wrappers.
- Unified profile models should be LinkedIn-style components with concrete Pydantic classes for each section/item.
- Job role targeting should be modeled as profile-native `job_role_potential` with five levels for role discovery, not JD/profile matching.
- Review-only source text belongs in `raw_text`; canonical fields must stay schema-shaped.

## Testing

- Unify all tests for a module in a `tests` subdirectory under that module's directory (e.g., `engine/company_intel/tests/`).
- Tests should use real files from `engine/profile/fixtures/` when validating ingestion/extraction behavior.
- Review outputs should be written to `engine/profile/review_outputs/` for inspection.
- Keep tests clear and focused on behavior.
- Always mock or fake the LLM clients in unit tests to avoid calling live APIs and incurring token costs.
