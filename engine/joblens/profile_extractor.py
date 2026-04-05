"""
JobLens Profile Extractor

Takes the user's unified profile (from the existing profile system)
and extracts a structured profile optimized for job applications.
"""

import logging
from typing import Dict, Any, Optional
from engine.models.llm import LLMClient
from .models import ExtractedProfile

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a career analyst. Given a candidate's profile data, extract a structured profile optimized for job applications.

Your task:
1. Identify their current title and years of experience
2. Classify their primary role type (SWE / AI-ML / Backend / Cloud / DevOps / Full-Stack / Frontend / Data / Mobile)
3. Group technical skills by category (languages, frameworks, databases, cloud, AI/ML, DevOps, other)
4. Select their top 3-5 work experiences with key achievements (prefer metrics and impact)
5. Identify notable projects with tech stacks
6. List open source contributions and publications/talks
7. Write a 2-3 sentence professional summary
8. Write an ai_verdict: a rich analysis of the candidate's profile including:
   - Their strongest selling points
   - How they should position themselves
   - What makes them stand out
   - Areas they could highlight more

Be specific and evidence-based. Use actual data from the profile, not generic statements."""


class ProfileExtractor:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def extract(self, unified_profile: Dict[str, Any], portfolio_notes: Optional[str] = None) -> ExtractedProfile:
        context_parts = [f"PROFILE DATA:\n{_format_profile(unified_profile)}"]
        if portfolio_notes:
            context_parts.append(f"\nPORTFOLIO / EXTRA CONTEXT:\n{portfolio_notes}")

        context = "\n".join(context_parts)

        logger.info("Extracting structured profile for job applications")
        result = self.llm.complete(
            response_model=ExtractedProfile,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract a job-application-optimized profile from this data:\n\n{context}"},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        logger.info(f"Profile extracted: {result.current_title}, {result.years_of_experience}y exp, {result.primary_role_type}")
        return result


def extract_profile(unified_profile: Dict[str, Any], llm: LLMClient, portfolio_notes: Optional[str] = None) -> ExtractedProfile:
    """Convenience function."""
    return ProfileExtractor(llm).extract(unified_profile, portfolio_notes)


def _format_profile(profile: Dict[str, Any]) -> str:
    """Format unified profile dict into readable text for LLM."""
    parts = []

    basics = profile.get("basics", {})
    if basics:
        parts.append(f"Name: {basics.get('name', 'Unknown')}")
        contact = basics.get("contact_info", {})
        if contact.get("email"):
            parts.append(f"Email: {contact['email']}")
        if basics.get("location"):
            parts.append(f"Location: {basics['location']}")

    work = profile.get("work_experience", [])
    if work:
        parts.append("\nWORK EXPERIENCE:")
        for item in work:
            title = item.get("job_title", "")
            company = item.get("company_name", "")
            start = item.get("start_date", "")
            end = item.get("end_date", "Present")
            parts.append(f"\n{title} at {company} ({start} - {end})")
            for desc in item.get("description", []):
                parts.append(f"  - {desc}")

    skills = profile.get("skills", [])
    if skills:
        parts.append(f"\nSKILLS: {', '.join(skills)}")

    education = profile.get("education", [])
    if education:
        parts.append("\nEDUCATION:")
        for item in education:
            inst = item.get("institution", "")
            degree = item.get("degree", "")
            major = item.get("major", "")
            year = item.get("graduation_year", "")
            parts.append(f"  {degree} in {major} from {inst} ({year})")

    dynamic = profile.get("dynamic_sections", {})
    if dynamic:
        for section_name, section_data in dynamic.items():
            parts.append(f"\n{section_name.upper()}:")
            if isinstance(section_data, list):
                for item in section_data:
                    parts.append(f"  - {item}")
            elif isinstance(section_data, str):
                parts.append(f"  {section_data}")
            elif isinstance(section_data, dict):
                for k, v in section_data.items():
                    parts.append(f"  {k}: {v}")

    return "\n".join(parts)
