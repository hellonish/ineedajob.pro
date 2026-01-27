"""
Formatting Checker - LLM-based resume quality analysis.
"""

from typing import Dict, Optional
from engine.models import get_gemini_client
from .models import FormattingCheckResult


class FormattingChecker:
    """
    Analyzes resume for formatting and chronological issues.
    
    Checks for:
    - Formatting issues (grammar, consistency, clarity)
    - Chronological issues (gaps, overlaps, wrong order)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = get_gemini_client(self._api_key)
        return self._client
    
    def check(self, resume: Dict, today_date: str = None) -> FormattingCheckResult:
        """
        Check resume for formatting and chronological issues.
        
        Args:
            resume: Resume data (from unified_profile or sources.resume)
            today_date: Today's date in YYYY-MM-DD format for chronological validation
            
        Returns:
            FormattingCheckResult with issues found
        """
        print("🔍 Checking resume formatting...")
        
        if today_date is None:
            from datetime import date
            today_date = date.today().isoformat()
        
        result = self._run_check(resume, today_date)
        
        # Calculate summary counts
        result.total_formatting_issues = len(result.formatting_issues)
        result.total_chronological_issues = len(result.chronological_issues)
        
        print("✅ Formatting check complete!")
        return result
    
    def _get_system_prompt(self, today_date: str) -> str:
        return f"""You are a professional resume content reviewer.

TODAY'S DATE: {today_date}

Analyze the resume CONTENT for REAL issues only.

## CRITICAL RULES - DO NOT HALLUCINATE:
1. ONLY flag issues where the original text is ACTUALLY wrong
2. The suggestion MUST be DIFFERENT from the original text
3. Quote the EXACT text from the resume - do not paraphrase
4. If you're not 100% certain something is wrong, DO NOT flag it
5. "Change X to X" is NEVER valid - the before and after must differ

## 1. CONTENT ISSUES TO LOOK FOR:

**Weak/Missing Action Verbs:**
- "Responsible for managing" → "Managed" or "Led"
- "Worked on APIs" → "Built APIs" or "Developed APIs"

**Vague Descriptions (missing specifics/numbers):**
- "Improved performance" → "Improved performance by 40%"
- "Handled requests" → "Processed 500+ requests daily"

**Tense Inconsistency:**
- Resumes use IMPLIED 1st person (no "I", no "He/She")
- Current jobs (end_date="Present"): Use base verb form - "Lead", "Develop", "Help"
- Past jobs: Use past tense - "Led", "Developed", "Helped"
- WRONG: "Leads team" (3rd person) → RIGHT: "Lead team" (implied 1st person)
- WRONG: "Helped students" for current job → RIGHT: "Help students"

**Actual Typos/Errors:**
- Real misspellings only
- Grammar errors

## 2. CHRONOLOGICAL ISSUES (Reference: {today_date}):

**Employment Gaps > 3 months:**
- Job A ended 2023-06, Job B started 2024-01 = 6 month gap

**Date Overlaps:**
- Two jobs with overlapping date ranges

**Wrong Order:**
- Newer job appearing after older job

## OUTPUT FORMAT:
For each REAL issue:
- section: Exact location (e.g., "work_experience[0].description[0]")
- description: Quote the EXACT problematic text
- suggestion: The CORRECTED text (must be DIFFERENT from original)
- severity: low/medium/high

If resume has no issues, return empty lists. DO NOT invent problems.

Score: Start at 100, deduct per issue (high=-10, medium=-5, low=-2)"""

    def _run_check(self, resume: Dict, today_date: str) -> FormattingCheckResult:
        import time
        print("  🤖 Calling LLM...")
        start = time.time()
        
        result = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            response_model=FormattingCheckResult,
            messages=[
                {"role": "system", "content": self._get_system_prompt(today_date)},
                {"role": "user", "content": f"Analyze this resume:\n\n{resume}"}
            ],
            temperature=0.0,
            max_tokens=6000,
            max_retries=2,
        )
        
        print(f"  ⏱ LLM call took {time.time() - start:.1f}s")
        return result
