"""
JobLens Match Analyzer

Compares the candidate's extracted profile against the parsed JD
to produce match scores, strengths, gaps, and a verdict.
"""

import logging
from typing import Dict, Any
from engine.models.llm import LLMClient
from .models import MatchAnalysis, ExtractedProfile, ParsedJD

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a brutally honest career advisor comparing a candidate's profile against a job description.

Score the candidate on:
- Technical skills match (0-100): How well do their skills cover the required and nice-to-have tech stack?
- Experience level match (0-100): Do they have the right seniority and years of experience?
- Project/portfolio relevance (0-100): How relevant is their project work to this role?
- Culture and working style fit (0-100): Based on culture signals, does this person seem like a fit?
- Overall fit score (0-100): Weighted average considering how critical each dimension is for THIS role.

Rules:
1. STRENGTHS must reference SPECIFIC items from the profile that match SPECIFIC requirements in the JD. No generic "strong communicator" without evidence.
2. GAPS must include severity (critical/moderate/minor) and actionable remediation — either a quick fix before applying or how to address it in the interview.
3. UNIQUE ANGLES: What makes this candidate stand out vs typical applicants? Think about unusual combinations of skills, domain experience, or perspectives.
4. VERDICT: Be honest. Use one of: "Strong Fit" / "Good Fit" / "Stretch" / "Long Shot"
5. TAILORED PITCH: Write a 3-4 sentence first-person pitch they can use in cover letters. Must be specific to THIS company and role.
6. ai_verdict: Deep analysis including:
   - Whether to prioritize this application
   - Biggest risks and how to mitigate them
   - The single most important thing to emphasize
   - What the interviewer will probably focus on
   - Realistic assessment of chances

Be specific, not generic. Reference actual skills, projects, and requirements."""


class MatchAnalyzer:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def analyze(
        self,
        profile: ExtractedProfile,
        parsed_jd: ParsedJD,
        company_intel: Dict[str, Any] = None,
    ) -> MatchAnalysis:
        """Compare profile against JD and produce match analysis."""
        context_parts = [
            f"CANDIDATE PROFILE:\n{profile.model_dump_json(indent=2)}",
            f"\nJOB DESCRIPTION:\n{parsed_jd.model_dump_json(indent=2)}",
        ]

        if company_intel:
            context_parts.append(f"\nCOMPANY CONTEXT:\n{_format_dict(company_intel)}")

        context = "\n".join(context_parts)

        logger.info(f"Analyzing match: {profile.current_title} vs {parsed_jd.role_title} at {parsed_jd.company_name}")
        result = self.llm.complete(
            response_model=MatchAnalysis,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Compare this candidate against this job:\n\n{context}"},
            ],
            temperature=0.4,
            max_tokens=4096,
        )
        logger.info(f"Match analysis: {result.verdict} (overall: {result.overall_score}/100)")
        return result


def analyze_match(
    profile: ExtractedProfile,
    parsed_jd: ParsedJD,
    llm: LLMClient,
    company_intel: Dict[str, Any] = None,
) -> MatchAnalysis:
    """Convenience function."""
    return MatchAnalyzer(llm).analyze(profile, parsed_jd, company_intel)


def _format_dict(d: Dict[str, Any]) -> str:
    """Format a dict into readable key-value text."""
    parts = []
    for k, v in d.items():
        if isinstance(v, list):
            parts.append(f"{k}: {', '.join(str(x) for x in v)}")
        else:
            parts.append(f"{k}: {v}")
    return "\n".join(parts)
