"""
JobLens Action Planner

Builds a concrete action plan to maximize application chances.
This is the final step that synthesizes all previous analyses.
"""

import logging
from typing import Optional
from engine.models.llm import LLMClient
from .models import (
    ActionPlan, ExtractedProfile, ParsedJD,
    MatchAnalysis, CompanyIntel, ContactStrategy,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a career coach building a concrete, actionable application plan.

Based on the candidate's profile, the job description, match analysis, and company intel, create a step-by-step plan.

BEFORE APPLYING:
1. Resume edits: Give SPECIFIC bullet-point-level changes. Not "tailor your resume" — give actual text to add/update/remove tied to JD keywords.
2. Portfolio updates: What to add, update, or highlight
3. Quick gap closers: Things they can do THIS WEEK to address critical gaps

COVER LETTER:
1. Opening hook: A first sentence that would grab THIS hiring manager's attention. Not generic.
2. Key points: 3 specific points tied DIRECTLY to JD requirements, with evidence from the profile.
3. Closing line: Strong, specific to the company.

INTERVIEW PREP:
1. Top 5 technical topics for THIS specific role and company
2. For each: a realistic question they'd actually ask, and what they're evaluating (not just "technical skills" — be specific about what dimension)

AFTER APPLYING:
1. Follow-up strategy with specific timelines (Day 3, Day 7, Day 14)
2. Who to follow up with and exact message templates

PREP DAYS NEEDED:
- Be realistic. Consider the gaps identified and what needs to be done.

ai_verdict should be an executive summary:
- Prioritized timeline (what to do first, second, third)
- The single most impactful thing they can do
- Realistic assessment of how ready they are
- What to focus on vs what to skip"""


class ActionPlanner:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def plan(
        self,
        profile: ExtractedProfile,
        parsed_jd: ParsedJD,
        match_analysis: MatchAnalysis,
        company_intel: Optional[CompanyIntel] = None,
        contact_strategy: Optional[ContactStrategy] = None,
    ) -> ActionPlan:
        """Build a comprehensive action plan."""
        context_parts = [
            f"CANDIDATE: {profile.current_title} ({profile.years_of_experience}y exp)",
            f"ROLE: {parsed_jd.role_title} at {parsed_jd.company_name} ({parsed_jd.level})",
            f"\nMATCH VERDICT: {match_analysis.verdict} (Score: {match_analysis.overall_score}/100)",
            f"\nPROFILE:\n{profile.model_dump_json(indent=2)}",
            f"\nJOB DESCRIPTION:\n{parsed_jd.model_dump_json(indent=2)}",
            f"\nMATCH ANALYSIS:\n{match_analysis.model_dump_json(indent=2)}",
        ]

        if company_intel:
            context_parts.append(f"\nCOMPANY INTEL:\n{company_intel.model_dump_json(indent=2)}")

        if contact_strategy:
            context_parts.append(f"\nCONTACT STRATEGY:\n{contact_strategy.model_dump_json(indent=2)}")

        context = "\n".join(context_parts)

        logger.info(f"Building action plan for {parsed_jd.role_title} at {parsed_jd.company_name}")
        result = self.llm.complete(
            response_model=ActionPlan,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Build a complete action plan for this application:\n\n{context}"},
            ],
            temperature=0.5,
            max_tokens=8192,
        )
        logger.info(f"Action plan: {result.prep_days_needed} days prep, {len(result.resume_edits)} resume edits, {len(result.interview_prep)} interview topics")
        return result


def plan_actions(
    profile: ExtractedProfile,
    parsed_jd: ParsedJD,
    match_analysis: MatchAnalysis,
    llm: LLMClient,
    company_intel: Optional[CompanyIntel] = None,
    contact_strategy: Optional[ContactStrategy] = None,
) -> ActionPlan:
    """Convenience function."""
    return ActionPlanner(llm).plan(profile, parsed_jd, match_analysis, company_intel, contact_strategy)
