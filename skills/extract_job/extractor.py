"""Extract-job skill: turns raw job posting text into a JobListing using an LLM.

Uses the same BaseLlmClient contract as extract_person so any provider can be used.
Designed for high-quality extraction to support comparing an applicant's profile (Person) to the job.
"""

from typing import Any, Protocol

from models.models import (
    Company,
    Compensation,
    FundingInfo,
    H1BSponsorship,
    JobListing,
    Leadership,
    NewsArticle,
    PlatformMetadata,
)

from skills.extract_job.prompts import EXTRACT_JOB_SYSTEM


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


def _optional_str(x: Any) -> str | None:
    if x is None or (isinstance(x, str) and not x.strip()):
        return None
    return str(x).strip()


def _optional_float(x: Any) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _optional_int(x: Any) -> int | None:
    if x is None:
        return None
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def _optional_bool(x: Any) -> bool | None:
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    if s in ("true", "yes", "1"):
        return True
    if s in ("false", "no", "0"):
        return False
    return None


def _norm_compensation(d: dict[str, Any] | None) -> Compensation | None:
    if not d or not isinstance(d, dict):
        return None
    return Compensation(
        min_salary=_optional_float(d.get("min_salary")),
        max_salary=_optional_float(d.get("max_salary")),
        currency=_ensure_str(d.get("currency")) or "USD",
        details=_optional_str(d.get("details")),
    )


def _norm_funding_info(d: dict[str, Any] | None) -> FundingInfo | None:
    if not d or not isinstance(d, dict):
        return None
    return FundingInfo(
        stage=_optional_str(d.get("stage")),
        total_funding_amount=_optional_str(d.get("total_funding_amount")),
        key_investors=[_ensure_str(x) for x in _ensure_list(d.get("key_investors"))],
        recent_events=[_ensure_str(x) for x in _ensure_list(d.get("recent_events"))],
    )


def _norm_leadership(d: dict[str, Any]) -> Leadership:
    return Leadership(
        name=_ensure_str(d.get("name")),
        role=_ensure_str(d.get("role")),
    )


def _norm_news_article(d: dict[str, Any]) -> NewsArticle:
    return NewsArticle(
        title=_ensure_str(d.get("title")),
        source=_optional_str(d.get("source")),
        date=_optional_str(d.get("date")),
    )


def _norm_company(d: dict[str, Any] | None) -> Company:
    if not d or not isinstance(d, dict):
        return Company(name="")
    raw_funding = d.get("funding_info")
    funding = _norm_funding_info(raw_funding) if isinstance(raw_funding, dict) else None
    raw_leadership = _ensure_list(d.get("leadership_team"))
    leadership_team = [
        _norm_leadership(x) for x in raw_leadership if isinstance(x, dict)
    ]
    raw_news = _ensure_list(d.get("recent_news"))
    recent_news = [
        _norm_news_article(x) for x in raw_news if isinstance(x, dict)
    ]
    return Company(
        name=_ensure_str(d.get("name")),
        about=_optional_str(d.get("about")),
        founded_year=_optional_int(d.get("founded_year")),
        headquarters=_optional_str(d.get("headquarters")),
        employee_count=_optional_str(d.get("employee_count")),
        glassdoor_rating=_optional_float(d.get("glassdoor_rating")),
        website=_optional_str(d.get("website")),
        funding_info=funding,
        leadership_team=leadership_team,
        recent_news=recent_news,
    )


def _norm_h1b(d: dict[str, Any] | None) -> H1BSponsorship | None:
    if not d or not isinstance(d, dict):
        return None
    raw_trends = d.get("historical_trends")
    historical_trends: dict[str, int] | None = None
    if isinstance(raw_trends, dict):
        historical_trends = {}
        for k, v in raw_trends.items():
            vi = _optional_int(v)
            if vi is not None:
                historical_trends[str(k)] = vi
    return H1BSponsorship(
        likely_sponsor=_optional_bool(d.get("likely_sponsor")),
        historical_trends=historical_trends,
    )


def _norm_platform_metadata(d: dict[str, Any] | None) -> PlatformMetadata | None:
    if not d or not isinstance(d, dict):
        return None
    return PlatformMetadata(
        match_percentage=_optional_int(d.get("match_percentage")),
        exp_level_match=_optional_int(d.get("exp_level_match")),
        skill_match=_optional_int(d.get("skill_match")),
        industry_exp_match=_optional_int(d.get("industry_exp_match")),
        insider_connections_count=_optional_int(d.get("insider_connections_count")),
    )


def _dict_to_job_listing(raw: dict[str, Any]) -> JobListing:
    """Normalize LLM output dict and build a validated JobListing."""
    raw_company = raw.get("company")
    company = _norm_company(raw_company) if isinstance(raw_company, dict) else Company(name="")
    return JobListing(
        job_title=_ensure_str(raw.get("job_title")),
        company=company,
        location=_ensure_str(raw.get("location")),
        url=_optional_str(raw.get("url")),
        posted_at=_optional_str(raw.get("posted_at")),
        job_type=_optional_str(raw.get("job_type")),
        work_model=_optional_str(raw.get("work_model")),
        experience_level=_optional_str(raw.get("experience_level")),
        compensation=_norm_compensation(raw.get("compensation")),
        about_the_role=_optional_str(raw.get("about_the_role")),
        responsibilities=[_ensure_str(x) for x in _ensure_list(raw.get("responsibilities"))],
        qualifications_required=[_ensure_str(x) for x in _ensure_list(raw.get("qualifications_required"))],
        qualifications_preferred=[_ensure_str(x) for x in _ensure_list(raw.get("qualifications_preferred"))],
        skills_tags=[_ensure_str(x) for x in _ensure_list(raw.get("skills_tags"))],
        benefits=[_ensure_str(x) for x in _ensure_list(raw.get("benefits"))],
        application_instructions=_optional_str(raw.get("application_instructions")),
        h1b_sponsorship=_norm_h1b(raw.get("h1b_sponsorship")),
        platform_metadata=_norm_platform_metadata(raw.get("platform_metadata")),
    )


class BaseLlmClientProtocol(Protocol):
    """Protocol for LLM clients: only generate_structured is required by this skill."""

    def generate_structured(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]: ...


def job_listing_from_dict(raw: dict[str, Any]) -> JobListing:
    """Build a validated JobListing from a dict (e.g. LLM output)."""
    if not isinstance(raw, dict):
        raw = {}
    return _dict_to_job_listing(raw)


def extract_job(
    content: str,
    llm: BaseLlmClientProtocol,
    model: str | None = None,
    **kwargs: Any,
) -> JobListing:
    """Extract a JobListing from raw job posting text using the given LLM.

    Args:
        content: Raw text from a job posting (pasted text, scraped HTML text, etc.).
        llm: LLM client implementing generate_structured(messages, model=..., **kwargs) -> dict.
        model: Optional model name; uses client default if None.
        **kwargs: Passed to llm.generate_structured (e.g. max_tokens, temperature).

    Returns:
        JobListing populated from the extracted JSON, suitable for comparing to a Person profile.
    """
    messages = [
        {"role": "system", "content": EXTRACT_JOB_SYSTEM},
        {"role": "user", "content": f"Extract structured job data from this job posting:\n\n{content}"},
    ]
    out = llm.generate_structured(messages, model=model, **kwargs)
    if not isinstance(out, dict):
        out = {}
    return _dict_to_job_listing(out)
