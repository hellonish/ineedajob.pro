"""
Qualification Checker - LLM-based qualification matching.
"""

from typing import Dict, Optional
from engine.models import get_gemini_client
from .models import QualificationCheckResult


class QualificationChecker:
    """
    Checks resume against job qualifications.
    
    Outputs ✓ or ✗ for each:
    - Required qualifications
    - Preferred qualifications
    - Technical skills
    - Soft skills
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = get_gemini_client(self._api_key)
        return self._client
    
    def check(self, job_posting: Dict, resume: Dict) -> QualificationCheckResult:
        """
        Check resume against job qualifications.
        
        Args:
            job_posting: Parsed job posting JSON
            resume: Resume data (from unified_profile or sources.resume)
            
        Returns:
            QualificationCheckResult with match status for each item
        """
        print("🔍 Checking qualifications...")
        
        context = self._build_context(job_posting, resume)
        result = self._run_check(context)
        
        # Calculate summary counts
        result.required_total = len(result.required_qualifications)
        result.required_match_count = sum(1 for q in result.required_qualifications if q.matched)
        result.preferred_total = len(result.preferred_qualifications)
        result.preferred_match_count = sum(1 for q in result.preferred_qualifications if q.matched)
        result.technical_total = len(result.technical_skills)
        result.technical_match_count = sum(1 for q in result.technical_skills if q.matched)
        result.soft_total = len(result.soft_skills)
        result.soft_match_count = sum(1 for q in result.soft_skills if q.matched)
        
        print("✅ Qualification check complete!")
        return result
    
    def _build_context(self, job_posting: Dict, resume: Dict) -> str:
        return f"""
JOB POSTING:
- Required Qualifications: {job_posting.get('required_qualifications', [])}
- Preferred Qualifications: {job_posting.get('preferred_qualifications', [])}
- Technical Skills: {job_posting.get('technical_skills', [])}
- Soft Skills: {job_posting.get('soft_skills', [])}

RESUME:
{resume}
"""
    
    def _get_system_prompt(self) -> str:
        return """You are a resume analyzer comparing qualifications against job requirements.

For EACH item in the job posting (required qualifications, preferred qualifications, technical skills, soft skills):
1. Check if the resume demonstrates this qualification/skill
2. Set matched=true if found, matched=false if not found
3. **ALWAYS provide evidence**:
   - If MATCHED: Quote specific text/experience from resume that demonstrates this
   - If NOT MATCHED: Explain what the resume is missing or why it doesn't qualify

Be thorough but fair:
- Technical skills: Look for exact matches or equivalent technologies
- Soft skills: Look for evidence in experience descriptions, not just keyword matches
- Qualifications: Check education, experience level, certifications

IMPORTANT: The evidence field must NEVER be empty. 
- For matches: "Resume shows X which demonstrates this qualification"
- For non-matches: "Resume lacks X" or "No mention of Y industry experience"

Output ALL items from the job posting with their match status and evidence."""
    
    def _run_check(self, context: str) -> QualificationCheckResult:
        import time
        print("  🤖 Calling LLM...")
        start = time.time()
        
        result = self.client.chat.completions.create(
            model="gemini-2.5-pro",
            response_model=QualificationCheckResult,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": context}
            ],
            temperature=0.0,
            max_tokens=8192,
            max_retries=2,
        )
        
        print(f"  ⏱ LLM call took {time.time() - start:.1f}s")
        return result
