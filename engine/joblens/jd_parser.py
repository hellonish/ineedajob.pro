"""
JobLens JD Parser

Parses a job description text into structured fields for analysis and display.
"""

import logging
from typing import Optional
from engine.models.llm import LLMClient
from .models import ParsedJD

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a job description analyst specializing in tech roles. Parse the given job description and extract every detail into structured fields.

Rules:
1. Separate REQUIRED skills from NICE-TO-HAVE skills carefully. Only mark as required what the JD explicitly requires.
2. Extract the FULL tech stack mentioned anywhere in the JD.
3. For ATS keywords: include exact phrases from the JD that an ATS system would match on. Include both acronyms and full forms.
4. Green flags: specific positive signals (good benefits, growth opportunity, interesting tech, strong team).
5. Red flags: vague language, unrealistic expectations, missing info, "wear many hats" at non-startup, "fast-paced" overuse.
6. Culture signals: what the JD reveals about the team and working style.
7. Role summary: 2 sentences capturing what the role REALLY needs (not what the JD says superficially).
8. For ai_verdict: provide a deep analysis including:
   - What the JD reveals between the lines
   - Hidden requirements not explicitly stated
   - Whether the role seems well-defined or a "catch-all"
   - Recommendations for how to approach this application
   - Any inconsistencies or interesting patterns in the JD

Be thorough and honest. If information isn't in the JD, say "Not specified" rather than guessing."""


class JDParser:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def parse(self, jd_text: str, job_posting: Optional[dict] = None) -> ParsedJD:
        """Parse a job description into structured fields.

        Args:
            jd_text: Raw job description text
            job_posting: Optional pre-parsed job posting dict (from existing Job model)
        """
        context = jd_text
        if job_posting:
            context = _format_job_posting(job_posting, jd_text)

        logger.info("Parsing job description")
        result = self.llm.complete(
            response_model=ParsedJD,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Parse this job description:\n\n{context}"},
            ],
            temperature=0.2,
            max_tokens=4096,
        )
        logger.info(f"JD parsed: {result.role_title} at {result.company_name} ({result.level})")
        return result


def parse_jd(jd_text: str, llm: LLMClient, job_posting: Optional[dict] = None) -> ParsedJD:
    """Convenience function."""
    return JDParser(llm).parse(jd_text, job_posting)


def _format_job_posting(job_posting: dict, raw_jd: str = "") -> str:
    """Combine structured job_posting data with raw JD text."""
    parts = []
    if job_posting.get("job_title"):
        parts.append(f"Job Title: {job_posting['job_title']}")
    if job_posting.get("company_name"):
        parts.append(f"Company: {job_posting['company_name']}")
    if job_posting.get("location"):
        parts.append(f"Location: {job_posting['location']}")
    if job_posting.get("salary_range"):
        parts.append(f"Salary: {job_posting['salary_range']}")

    if raw_jd:
        parts.append(f"\nFULL JOB DESCRIPTION:\n{raw_jd}")
    else:
        # Use structured fields
        if job_posting.get("required_qualifications"):
            parts.append(f"\nRequired Qualifications: {', '.join(job_posting['required_qualifications'])}")
        if job_posting.get("preferred_qualifications"):
            parts.append(f"Preferred Qualifications: {', '.join(job_posting['preferred_qualifications'])}")
        if job_posting.get("technical_skills"):
            parts.append(f"Technical Skills: {', '.join(job_posting['technical_skills'])}")
        if job_posting.get("description"):
            parts.append(f"\nDescription:\n{job_posting['description']}")

    return "\n".join(parts)
