"""
Cover Letter Generator - LLM-based cover letter creation.
"""

from typing import Dict, Optional, Literal
from engine.models import get_gemini_client
from .models import CoverLetter


CoverLetterMode = Literal["professional", "conversational", "concise", "creative", "storytelling"]


class CoverLetterGenerator:
    """
    Generates personalized cover letters using job description and profile.
    
    Modes:
    - professional: Formal, traditional corporate style
    - conversational: Friendly, approachable tone
    - concise: Brief, to-the-point (200 words)
    - creative: Standout, unique approach
    - storytelling: Narrative-driven, engaging
    """
    
    MODE_PROMPTS = {
        "professional": """
STYLE: Professional & Formal
- Use formal language and traditional structure
- Focus on qualifications and achievements
- Maintain corporate tone throughout
- Use industry terminology appropriately
- Length: 300-400 words""",
        
        "conversational": """
STYLE: Conversational & Friendly
- Use a warm, approachable tone
- Write as if speaking to a respected colleague
- Show personality while staying professional
- Use contractions naturally (I'm, I've, I'd)
- Length: 250-350 words""",
        
        "concise": """
STYLE: Concise & Direct
- Get straight to the point
- Maximum 200 words total
- One paragraph per section MAX
- Focus only on top 2-3 selling points
- No filler phrases""",
        
        "creative": """
STYLE: Creative & Standout
- Open with a unique hook or insight
- Show originality and fresh thinking
- Take calculated risks in language
- Demonstrate creative problem-solving
- Make them remember you
- Length: 250-350 words""",
        
        "storytelling": """
STYLE: Storytelling & Narrative
- Open with a brief, relevant story or anecdote
- Connect your journey to this opportunity
- Create emotional resonance
- Show, don't just tell
- End with forward-looking vision
- Length: 300-400 words"""
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = get_gemini_client(self._api_key)
        return self._client
    
    def generate(
        self,
        job_posting: Dict,
        unified_profile: Dict,
        mode: CoverLetterMode = "professional",
        applicant_name: Optional[str] = None,
        hiring_manager: Optional[str] = None
    ) -> CoverLetter:
        """
        Generate a cover letter.
        
        Args:
            job_posting: Parsed job posting JSON
            unified_profile: Complete unified profile
            applicant_name: Override name from profile
            hiring_manager: Hiring manager name if known
            
        Returns:
            CoverLetter with all paragraphs and full formatted letter
        """
        print(f"📝 Generating cover letter (mode: {mode})...")
        
        # Extract applicant name
        if applicant_name is None:
            applicant_name = unified_profile.get('basics', {}).get('name', 'Applicant')
        
        context = self._build_context(job_posting, unified_profile, applicant_name, hiring_manager)
        result = self._run_generation(context, mode)
        
        # Build full letter if not already set
        if not result.full_letter:
            result.full_letter = self._format_full_letter(result, applicant_name)
        
        print("✅ Cover letter generated!")
        return result
    
    def _build_context(
        self,
        job_posting: Dict,
        unified_profile: Dict,
        applicant_name: str,
        hiring_manager: Optional[str]
    ) -> str:
        return f"""
APPLICANT NAME: {applicant_name}
HIRING MANAGER: {hiring_manager or "Unknown"}

JOB POSTING:
- Title: {job_posting.get('job_title', 'Unknown')}
- Company: {job_posting.get('company_name', 'Unknown')}
- About Company: {job_posting.get('company_about', '')}
- Description: {job_posting.get('job_description', '')}
- Required Qualifications: {job_posting.get('required_qualifications', [])}
- Technical Skills: {job_posting.get('technical_skills', [])}
- Soft Skills: {job_posting.get('soft_skills', [])}
- Keywords: {job_posting.get('job_keywords', [])}

APPLICANT PROFILE:
{unified_profile}
"""
    
    def _get_system_prompt(self, mode: CoverLetterMode) -> str:
        mode_style = self.MODE_PROMPTS.get(mode, self.MODE_PROMPTS["professional"])
        
        return f"""You are a professional cover letter writer.

{mode_style}

Create a compelling, personalized cover letter with these sections:

1. **Opening Paragraph**: Express enthusiasm, mention the role, hook about fit
2. **Experience Paragraph**: 2-3 relevant experiences with specific achievements
3. **Skills Paragraph**: Match technical skills to job requirements
4. **Motivation Paragraph**: Why this company interests you
5. **Closing Paragraph**: Eagerness to discuss, thank them

RULES:
- Be genuine, not generic
- Reference SPECIFIC experiences from the profile
- Mirror keywords from the job posting naturally
- Set greeting to "Dear Hiring Manager," or "Dear [Name]," if known

Also generate full_letter with proper formatting including line breaks."""

    def _run_generation(self, context: str, mode: CoverLetterMode) -> CoverLetter:
        import time
        print("  🤖 Calling LLM...")
        start = time.time()
        
        # Adjust temperature based on mode
        temp = 0.8 if mode in ["creative", "storytelling"] else 0.6
        
        result = self.client.chat.completions.create(
            model="gemini-2.5-pro",
            response_model=CoverLetter,
            messages=[
                {"role": "system", "content": self._get_system_prompt(mode)},
                {"role": "user", "content": f"Generate a cover letter:\n\n{context}"}
            ],
            temperature=temp,
            max_tokens=4096,
            max_retries=2,
        )
        
        print(f"  ⏱ LLM call took {time.time() - start:.1f}s")
        return result
    
    def _format_full_letter(self, letter: CoverLetter, applicant_name: str) -> str:
        """Format the full letter with proper structure."""
        return f"""{letter.greeting}

{letter.opening_paragraph}

{letter.experience_paragraph}

{letter.skills_paragraph}

{letter.motivation_paragraph}

{letter.closing_paragraph}

{letter.sign_off}
{applicant_name}"""


# Convenience function
def generate_cover_letter(
    job_posting: Dict,
    unified_profile: Dict,
    mode: CoverLetterMode = "professional",
    applicant_name: Optional[str] = None,
    hiring_manager: Optional[str] = None,
    api_key: Optional[str] = None
) -> CoverLetter:
    """
    Convenience function to generate a cover letter.
    
    Modes:
    - professional: Formal, traditional corporate style
    - conversational: Friendly, approachable tone
    - concise: Brief, to-the-point (200 words)
    - creative: Standout, unique approach
    - storytelling: Narrative-driven, engaging
    """
    generator = CoverLetterGenerator(api_key)
    return generator.generate(job_posting, unified_profile, mode, applicant_name, hiring_manager)
