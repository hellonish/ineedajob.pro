"""Resolve-person skill: merge two Person profiles into one using an LLM.

Takes two Person models (e.g. from resume and portfolio), sends both to the LLM
with strict instructions to merge without losing information: union list fields
with deduplication of same entities, choose best value for scalar conflicts.
Uses the same Person schema and normalization as extract_person.
"""

import json
from typing import Any, Protocol

from models.models import Person

from skills.extract_person import person_from_dict
from skills.resolve_person.prompts import RESOLVE_PERSON_SYSTEM


class BaseLlmClientProtocol(Protocol):
    """Protocol for LLM clients: only generate_structured is required."""

    def generate_structured(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]: ...


def _person_to_json_string(person: Person) -> str:
    """Serialize Person to a JSON string for the LLM. Uses model_dump for full fidelity."""
    return json.dumps(person.model_dump(mode="json"), indent=2, ensure_ascii=False)


def resolve_persons(
    person_a: Person,
    person_b: Person,
    llm: BaseLlmClientProtocol,
    model: str | None = None,
    **kwargs: Any,
) -> Person:
    """Merge two Person profiles into one canonical Person without losing information.

    The LLM evaluates both profiles, resolves discrepancies (e.g. name spelling,
    date format), merges list fields (experiences, educations, etc.) with
    deduplication when the same entity appears in both, and chooses the best
    value for scalar fields when they differ. No information from either
    profile should be dropped.

    Args:
        person_a: First Person profile (e.g. from resume).
        person_b: Second Person profile (e.g. from portfolio).
        llm: Any client implementing generate_structured (OpenAI, Anthropic, Gemini, DeepSeek).
        model: Optional model name; uses client default if None.
        **kwargs: Passed to llm.generate_structured (e.g. max_tokens, temperature).

    Returns:
        Single resolved Person with merged and deduplicated data.
    """
    profile_a = _person_to_json_string(person_a)
    profile_b = _person_to_json_string(person_b)
    user_content = f"""Merge these two profiles of the same person into one. Follow the rules in the system prompt: do not lose any information; merge lists and deduplicate only when the same entity appears twice; choose the best value for conflicting scalars.

Profile A:
{profile_a}

Profile B:
{profile_b}

Output the single merged Person as one JSON object only."""

    messages = [
        {"role": "system", "content": RESOLVE_PERSON_SYSTEM},
        {"role": "user", "content": user_content},
    ]
    out = llm.generate_structured(messages, model=model, **kwargs)
    if not isinstance(out, dict):
        out = {}
    return person_from_dict(out)
