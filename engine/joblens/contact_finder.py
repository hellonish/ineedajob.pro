"""
JobLens Contact Finder

Generates a contact strategy based on company, role, and context.
"""

import logging
from typing import Optional, Dict, Any
from engine.models.llm import LLMClient
from .models import ContactStrategy, ParsedJD, CompanyIntel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a job search strategist specializing in tech industry networking.

Based on the company, role, and context provided, generate a concrete contact strategy.

For each contact target (3-5 people):
1. Title: Their likely title at this company (e.g., "Engineering Manager - Backend Team", "Senior Recruiter")
2. Why they matter: Why reaching out to them specifically helps
3. Priority: high/medium/low with reasoning
4. Where to find them: Give an EXACT LinkedIn search query the user can paste, plus any other channels
5. Outreach message: 60-70 words. MUST reference something specific about the company (product, tech blog post, recent launch). Include [YOUR_NAME] placeholder. Keep it natural, not salesy.
6. Approach: Recommend the best approach (cold message / mutual connection / comment on content / open source contribution)

Also provide:
- Communities: Specific Slack/Discord/meetup groups where this company's engineers are active
- Referral strategy: How to get a referral at THIS specific company
- Networking importance: Is this a company where networking matters a lot, or is applying directly fine?
- ai_verdict: Strategic networking plan with:
  - Top 2 actions to take this week
  - The single highest-ROI networking move
  - Whether to invest time in networking or just apply directly
  - Common mistakes to avoid when reaching out to this company

Be realistic about what's achievable. Don't suggest approaches that require months of relationship building if the user needs to apply soon."""


class ContactFinder:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def find(
        self,
        parsed_jd: ParsedJD,
        company_intel: Optional[CompanyIntel] = None,
        profile_summary: Optional[str] = None,
    ) -> ContactStrategy:
        """Generate contact strategy for a specific role and company."""
        context_parts = [
            f"ROLE: {parsed_jd.role_title} at {parsed_jd.company_name}",
            f"LEVEL: {parsed_jd.level}",
            f"LOCATION: {parsed_jd.location}",
        ]

        if company_intel:
            context_parts.append(f"\nCOMPANY INFO:\n{company_intel.model_dump_json(indent=2)}")

        if profile_summary:
            context_parts.append(f"\nCANDIDATE SUMMARY:\n{profile_summary}")

        context = "\n".join(context_parts)

        logger.info(f"Finding contacts for {parsed_jd.role_title} at {parsed_jd.company_name}")
        result = self.llm.complete(
            response_model=ContactStrategy,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Generate a contact strategy for this application:\n\n{context}"},
            ],
            temperature=0.5,
            max_tokens=4096,
        )
        logger.info(f"Contact strategy: {len(result.contacts)} targets, networking importance: {result.networking_importance}")
        return result


def find_contacts(
    parsed_jd: ParsedJD,
    llm: LLMClient,
    company_intel: Optional[CompanyIntel] = None,
    profile_summary: Optional[str] = None,
) -> ContactStrategy:
    """Convenience function."""
    return ContactFinder(llm).find(parsed_jd, company_intel, profile_summary)
