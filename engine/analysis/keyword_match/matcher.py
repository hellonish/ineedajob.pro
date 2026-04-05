"""
Keyword Matcher - LLM-based keyword matching and resume suggestions.
"""

from typing import Dict, Optional
from engine.models import get_gemini_client
from .models import KeywordMatchResult


class KeywordMatcher:
    """
    Matches job keywords against resume and suggests improvements.
    
    Outputs:
    - Keyword match score (percentage)
    - Suggestions to add missing keywords (ADD, UPDATE, DELETE)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = get_gemini_client(self._api_key)
        return self._client
    
    def match(
        self,
        job_posting: Dict,
        resume: Dict,
        unified_profile: Optional[Dict] = None
    ) -> KeywordMatchResult:
        """
        Match job keywords against resume.
        
        Args:
            job_posting: Parsed job posting JSON (with job_keywords)
            resume: Resume data
            unified_profile: Full unified profile for context (optional)
            
        Returns:
            KeywordMatchResult with score and suggestions
        """
        print("🔍 Matching keywords...")
        
        context = self._build_context(job_posting, resume, unified_profile)
        result = self._run_match(context)
        
        # Calculate summary
        result.total_keywords = len(result.keywords_found) + len(result.keywords_missing)
        result.matched_count = len(result.keywords_found)
        if result.total_keywords > 0:
            result.keyword_match_score = round(
                (result.matched_count / result.total_keywords) * 100, 1
            )
        
        print("✅ Keyword matching complete!")
        return result
    
    def _build_context(
        self,
        job_posting: Dict,
        resume: Dict,
        unified_profile: Optional[Dict]
    ) -> str:
        job_keywords = job_posting.get('job_keywords', [])
        
        context = f"""
JOB KEYWORDS TO FIND:
{job_keywords}

RESUME:
{resume}
"""
        if unified_profile:
            context += f"""

UNIFIED PROFILE (for context when making suggestions):
{unified_profile}
"""
        return context
    
    def _get_system_prompt(self) -> str:
        return """You are a resume keyword optimizer helping tailor resumes to job postings.

Given job keywords, resume, and unified profile (which contains LinkedIn & portfolio context):

1. **Find Keywords**: Check which job keywords are present in the resume
   - Look for exact matches AND semantic equivalents
   - Consider synonyms (e.g., "CI/CD" = "continuous integration")
   
2. **Identify Missing**: List keywords NOT found in the resume

3. **Calculate Score**: keyword_match_score = (found / total) * 100

4. **Generate SPECIFIC Suggestions**: For EACH missing keyword, provide an actionable suggestion:

   IMPORTANT - Section naming rules:
   - For work experience, use the JOB TITLE and COMPANY instead of array indices
   - Example: "Software Engineer at Acme Corp" NOT "work_experience[0]"
   - Example: "Product Manager at StartupXYZ - Achievements" NOT "work_experience[1].achievements"
   - For skills section, use "Skills"
   - For education, use "Education at [University Name]"
   
   For ADD suggestions:
   - section: Human-readable section name (e.g., "Software Engineer at Microsoft", "Skills")
   - target: Leave empty for ADD
   - suggestion: The EXACT text to add. Be specific, e.g., "Add bullet point: 'Implemented security monitoring dashboards using Grafana to detect and respond to threats'"
   - keyword_addressed: The job keyword this addresses
   - Use context from the unified_profile to ground suggestions in REAL experiences from LinkedIn/portfolio
   
   For UPDATE suggestions:
   - section: Human-readable section name with job title
   - target: The EXACT current line to modify (copy it exactly)
   - suggestion: The NEW version of that line with keyword incorporated
   - Example: Update "Built REST APIs" to "Built secure REST APIs following SDLC best practices"
   
   For DELETE suggestions (use sparingly):
   - section: Human-readable section name
   - target: The EXACT line to remove
   - suggestion: Brief explanation of why it should be removed
   - reason: How this makes room for more relevant content

CRITICAL:
- ALWAYS use job title + company for work experience sections (e.g., "Data Analyst at Google")
- NEVER use array indices like [0], [1], [2] in section names
- Suggestions must be SPECIFIC and ACTIONABLE - no vague advice
- Use actual experiences from the unified_profile to craft realistic suggestions
- The 'suggestion' field should contain EXACT text the person can copy-paste
- Be creative but truthful - only suggest adding things grounded in their actual experience"""
    
    def _run_match(self, context: str) -> KeywordMatchResult:
        import time
        print("  🤖 Calling LLM...")
        start = time.time()
        
        result = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            response_model=KeywordMatchResult,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": context}
            ],
            temperature=0.0,
            max_tokens=6000,
            max_retries=1,
        )
        
        print(f"  ⏱ LLM call took {time.time() - start:.1f}s")
        return result
