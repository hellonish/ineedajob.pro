"""
Discrepancy Analyzer - Main analysis class using LLM.

Compares Resume, LinkedIn, and Portfolio profiles to find inconsistencies.
"""

from typing import Dict, List, Optional
from engine.models.llm import LLMClient
from .models import ProfileDiscrepancy


class DiscrepancyAnalyzer:
    """
    Analyzes profile discrepancies using LLM.

    Compares Resume, LinkedIn, and Portfolio to identify:
    - Mismatches: Different values for the same field
    - Partial presence: Items missing from some sources
    - Full consistency: Items that match across all sources

    Example:
        >>> from engine.models.llm import LLMClient
        >>> llm = LLMClient.from_user_settings({"llm_provider": "grok", "llm_model": "grok-3"})
        >>> analyzer = DiscrepancyAnalyzer(llm)
        >>> result = analyzer.analyze(resume_data, linkedin_data, portfolio_data)
        >>> print(result.consistency_score)
    """

    def __init__(self, llm: LLMClient):
        """
        Initialize the analyzer with an LLM client.

        Args:
            llm: LLMClient instance (created via LLMClient.from_user_settings)
        """
        self._llm = llm

    def analyze(
        self,
        resume: Optional[Dict] = None,
        linkedin: Optional[Dict] = None,
        portfolio: Optional[Dict] = None
    ) -> ProfileDiscrepancy:
        """
        Analyze discrepancies between profile sources.
        
        Args:
            resume: Parsed resume data
            linkedin: Parsed LinkedIn profile data
            portfolio: Parsed portfolio data
            
        Returns:
            ProfileDiscrepancy with comparison table and recommendations
            
        Raises:
            ValueError: If fewer than 2 sources are provided
        """
        print("🔍 Comparing profile sources for discrepancies...")
        
        # Validate sources
        sources = self._validate_sources(resume, linkedin, portfolio)
        if len(sources) < 2:
            print("  ⚠️ Only 1 source available. Skipping discrepancy check.")
            return ProfileDiscrepancy(
                consistency_score=100,
                recommendations=["Insufficient data for comparison. Please upload at least two sources (Resume, LinkedIn, or Portfolio) to run a discrepancy check."]
            )
        
        print(f"  📄 Comparing: {', '.join(sources)}")
        
        # Build context and analyze
        context = self._build_context(resume, linkedin, portfolio)
        result = self._run_analysis(context)
        
        print("✅ Discrepancy analysis complete!")
        return result
    
    def _validate_sources(
        self,
        resume: Optional[Dict],
        linkedin: Optional[Dict],
        portfolio: Optional[Dict]
    ) -> List[str]:
        """Validate and return list of provided sources."""
        sources = []
        if resume:
            sources.append("resume")
        if linkedin:
            sources.append("linkedin")
        if portfolio:
            sources.append("portfolio")
        return sources
    
    def _build_context(
        self,
        resume: Optional[Dict],
        linkedin: Optional[Dict],
        portfolio: Optional[Dict]
    ) -> str:
        """Build the comparison context string for LLM."""
        return f"""
PROFILE SOURCES TO COMPARE:

=== RESUME ===
{resume if resume else "Not provided"}

=== LINKEDIN ===
{linkedin if linkedin else "Not provided"}

=== PORTFOLIO ===
{portfolio if portfolio else "Not provided"}
"""
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for analysis."""
        return """You are analyzing profile consistency across sources (Resume, LinkedIn, Portfolio).

CRITICAL INSTRUCTION - ALIGNMENT IS KEY:
You must FIRST align entities (Jobs, Education, Projects) across sources based on semantic similarity of Company Name, Job Title, or Institution.
- Do NOT simply compare the first item of Resume with the first item of LinkedIn. They may be in different orders!
- Example: If Resume has [Job A, Job B] and LinkedIn has [Job C, Job A], you must find Job A in both and compare them. Job B and Job C are separate "partial" entries.
- "Ingelt Board" and "InGelt Board" are the SAME company. Align them.
- "New York University" and "NYU" are the SAME institution. Align them.

YOUR TASK:
1. Compare Non-Skill Items (Jobs, Education, Projects) for `comparison_table`:
   - For each ALIGNED entity, create separate `ProfileItem` entries for its properties:
     - Job Title
     - Company Name
     - Start Date / End Date
   - If an entity exists in Source A but not Source B, create items where Source B value is null (Status: "partial").
   - Status Rules:
     - "match": Values are identical or semantically equivalent (e.g., "NYU" == "New York Univ").
     - "mismatch": Values clearly contradict (e.g., Dates differ by months, completely different Company name for what you matched as the same role).
     - "partial": Entire entity is missing from one source.

2. Analyze Skills for `skills_analysis`:
   - Do NOT create `ProfileItem` objects for individual skills.
   - Populate `skills_analysis` string lists:
     - `matching_skills`: Present in >= 2 sources.
     - `missing_from_[source]`: Present in others but missing here.

3. Identify Discrepancies:
   - Generate `DiscrepancyItem` ONLY for "mismatch" status or significant "partial" issues.
   - Ignore trivial formatting (e.g. "NYU" vs "New York University" is NOT a discrepancy).

4. Score & Recommendations:
   - `consistency_score` (0-100).
   - `recommendations`: Actionable advice.

OUTPUT FORMAT:
Return strictly valid JSON matching the `ProfileDiscrepancy` schema.
"""
    
    def _run_analysis(self, context: str) -> ProfileDiscrepancy:
        """Run the LLM analysis and return structured result."""
        print("  🤖 Calling LLM for analysis...")
        import time
        start = time.time()

        result = self._llm.complete(
            response_model=ProfileDiscrepancy,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": context}
            ],
            temperature=0.0,
            max_tokens=32000,
            max_retries=1,
        )

        elapsed = time.time() - start
        print(f"  ⏱ LLM call took {elapsed:.1f}s")
        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def analyze_discrepancies(
    resume: Optional[Dict] = None,
    linkedin: Optional[Dict] = None,
    portfolio: Optional[Dict] = None,
    llm: Optional[LLMClient] = None
) -> ProfileDiscrepancy:
    """
    Convenience function to analyze discrepancies.

    Args:
        resume: Parsed resume data
        linkedin: Parsed LinkedIn profile data
        portfolio: Parsed portfolio data
        llm: LLMClient instance (uses user's preferred provider/model)

    Returns:
        ProfileDiscrepancy result
    """
    if llm is None:
        llm = LLMClient.from_user_settings({"llm_provider": "grok"})
    analyzer = DiscrepancyAnalyzer(llm)
    return analyzer.analyze(resume, linkedin, portfolio)
