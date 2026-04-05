"""Extract-person skill: turns raw content into a Person using an LLM.

Uses BaseLlmClient so any provider (OpenAI, Anthropic, Gemini, DeepSeek) can be
plugged in. Designed for high-quality extraction from resume or portfolio text.
"""

from typing import Any, Protocol

from models.models import (
    Award,
    Certification,
    Education,
    Experience,
    Extracurricular,
    Person,
    Project,
    SkillGroup,
)

from skills.extract_person.prompts import EXTRACT_PERSON_SYSTEM


def _ensure_list(x: Any) -> list[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return []


def _ensure_str(x: Any) -> str:
    if x is None:
        return ""
    return str(x).strip()


def _ensure_dict_str_list(x: Any) -> dict[str, list[str]]:
    if x is None or not isinstance(x, dict):
        return {}
    out: dict[str, list[str]] = {}
    for k, v in x.items():
        out[str(k)] = _ensure_list(v) if isinstance(v, list) else [str(v)] if v else []
    return out


def _norm_education(d: dict[str, Any]) -> dict[str, Any]:
    return {
        "school": _ensure_str(d.get("school")),
        "degree": _ensure_str(d.get("degree")),
        "field_of_study": _ensure_str(d.get("field_of_study")),
        "start_date": _ensure_str(d.get("start_date")),
        "end_date": d.get("end_date") if d.get("end_date") is not None else None,
        "description": d.get("description") if d.get("description") is not None else None,
        "subjects": _ensure_list(d.get("subjects")),
    }


def _norm_experience(d: dict[str, Any]) -> dict[str, Any]:
    return {
        "company": _ensure_str(d.get("company")),
        "title": _ensure_str(d.get("title")),
        "location": _ensure_str(d.get("location")),
        "start_date": _ensure_str(d.get("start_date")),
        "end_date": d.get("end_date") if d.get("end_date") is not None else None,
        "description": d.get("description") if d.get("description") is not None else None,
        "urls": _ensure_list(d.get("urls")),
        "skills": _ensure_list(d.get("skills")),
    }


def _norm_project(d: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": _ensure_str(d.get("name")),
        "description": _ensure_str(d.get("description")),
        "urls": _ensure_list(d.get("urls")),
        "skills": _ensure_list(d.get("skills")),
    }


def _norm_extracurricular(d: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": _ensure_str(d.get("name")),
        "description": _ensure_str(d.get("description")),
        "urls": _ensure_list(d.get("urls")),
        "skills": _ensure_list(d.get("skills")),
    }


def _norm_certification(d: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": _ensure_str(d.get("name")),
        "description": _ensure_str(d.get("description")),
        "urls": _ensure_list(d.get("urls")),
        "skills": _ensure_list(d.get("skills")),
        "datetime": _ensure_str(d.get("datetime")),
    }


def _norm_award(d: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": _ensure_str(d.get("name")),
        "description": _ensure_str(d.get("description")),
        "urls": _ensure_list(d.get("urls")),
        "skills": _ensure_list(d.get("skills")),
        "datetime": _ensure_str(d.get("datetime")),
    }


def _dict_to_person(raw: dict[str, Any]) -> Person:
    """Normalize LLM output dict and build a validated Person."""
    skills_raw = raw.get("skills")
    skills = SkillGroup(skills=_ensure_dict_str_list(skills_raw))

    def _only_dicts(items: Any) -> list[dict[str, Any]]:
        return [x for x in _ensure_list(items) if isinstance(x, dict)]

    educations = [Education(**_norm_education(d)) for d in _only_dicts(raw.get("educations"))]
    experiences = [Experience(**_norm_experience(d)) for d in _only_dicts(raw.get("experiences"))]
    projects = [Project(**_norm_project(d)) for d in _only_dicts(raw.get("projects"))]
    extracurriculars = [
        Extracurricular(**_norm_extracurricular(d))
        for d in _only_dicts(raw.get("extracurriculars"))
    ]
    certifications = [
        Certification(**_norm_certification(d)) for d in _only_dicts(raw.get("certifications"))
    ]
    awards = [Award(**_norm_award(d)) for d in _only_dicts(raw.get("awards"))]

    return Person(
        name=_ensure_str(raw.get("name")),
        headline=_ensure_str(raw.get("headline")),
        summary=_ensure_str(raw.get("summary")),
        location=_ensure_str(raw.get("location")),
        company=_ensure_str(raw.get("company")),
        title=_ensure_str(raw.get("title")),
        email=_ensure_str(raw.get("email")),
        phone=_ensure_str(raw.get("phone")),
        website=_ensure_str(raw.get("website")),
        languages=[_ensure_str(x) for x in _ensure_list(raw.get("languages"))],
        social_media=[_ensure_str(x) for x in _ensure_list(raw.get("social_media"))],
        skills=skills,
        educations=educations,
        experiences=experiences,
        projects=projects,
        extracurriculars=extracurriculars,
        certifications=certifications,
        awards=awards,
    )


class BaseLlmClientProtocol(Protocol):
    """Protocol for LLM clients: only generate_structured is required by this skill."""

    def generate_structured(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]: ...


def person_from_dict(raw: dict[str, Any]) -> Person:
    """Build a validated Person from a dict (e.g. LLM output). Reused by resolve_person skill."""
    if not isinstance(raw, dict):
        raw = {}
    return _dict_to_person(raw)


def extract_person(
    content: str,
    llm: BaseLlmClientProtocol,
    model: str | None = None,
    **kwargs: Any,
) -> Person:
    """Extract a Person from raw text using the given LLM (any BaseLlmClient implementation).

    Args:
        content: Raw text from a resume, portfolio page, or bio.
        llm: LLM client (OpenAI, Anthropic, Gemini, DeepSeek, etc.) implementing
            generate_structured(messages, model=..., **kwargs) -> dict.
        model: Optional model name; uses client default if None.
        **kwargs: Passed to llm.generate_structured (e.g. max_tokens, temperature).

    Returns:
        Person populated from the extracted JSON.
    """
    messages = [
        {"role": "system", "content": EXTRACT_PERSON_SYSTEM},
        {"role": "user", "content": f"Extract structured profile data from this content:\n\n{content}"},
    ]
    out = llm.generate_structured(messages, model=model, **kwargs)
    if not isinstance(out, dict):
        out = {}
    return _dict_to_person(out)
