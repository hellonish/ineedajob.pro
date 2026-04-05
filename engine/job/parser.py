"""
Job Posting Parser - LLM-based extraction from job postings.

Extracts structured data from raw job posting text.
"""

from typing import Optional
from engine.models import get_gemini_client
from .models import JobPosting


class JobParser:
    """
    Parses job postings using LLM to extract structured data.
    
    Extracts:
    - Required and preferred qualifications
    - Technical and soft skills
    - Job-specific keywords
    - Responsibilities and metadata
    
    Example:
        >>> parser = JobParser()
        >>> result = parser.parse(job_text)
        >>> print(result.technical_skills)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the parser with optional API key.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self._api_key = api_key
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the LLM client."""
        if self._client is None:
            self._client = get_gemini_client(self._api_key)
        return self._client
    
    def parse(self, job_text: str) -> JobPosting:
        """
        Parse a job posting and extract structured data.
        
        Args:
            job_text: Raw job posting text
            
        Returns:
            JobPosting with extracted fields
        """
        print("🔍 Parsing job posting...")
        
        if not job_text or not job_text.strip():
            raise ValueError("Job posting text cannot be empty")
        
        result = self._run_extraction(job_text)
        
        print("✅ Job posting parsed!")
        return result
    
    def parse_file(self, file_path: str) -> JobPosting:
        """
        Parse a job posting from a file.
        
        Args:
            file_path: Path to the job posting text file
            
        Returns:
            JobPosting with extracted fields
        """
        with open(file_path, 'r') as f:
            job_text = f.read()
        return self.parse(job_text)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for extraction."""
        return """You are a job posting analyzer. Extract structured information from the job posting.

For each field, carefully analyze the job posting:

1. **job_title**: The job position title
2. **company_name**: Name of the company
3. **company_about**: About the company - their mission, values, industry, what they do
4. **location**: Job location (city, state, remote status)
5. **job_description**: A concise summary of what this role is about (2-3 sentences)
6. **required_qualifications**: Education requirements, must-have certifications, years of experience explicitly required
7. **preferred_qualifications**: Nice-to-have items, "preferred" or "bonus" qualifications
8. **technical_skills**: Specific technologies, programming languages, frameworks, tools, platforms explicitly mentioned
   - Examples: Python, Java, AWS, Docker, SQL, React, etc.
9. **soft_skills**: Communication, teamwork, problem-solving, leadership, and other interpersonal skills (both implied and explicit)
   - Examples: "strong communication", "collaborative", "self-motivated", "fast-paced environment"
10. **job_keywords**: Industry-specific terms, buzzwords, and keywords that define this specific job
    - Examples: "asset management", "Agile", "CI/CD", "SDLC", "vulnerability management"
11. **responsibilities**: Key duties and what the person will do day-to-day
12. **experience_level**: Entry-level, junior, mid, senior, lead, etc.
13. **salary_range**: The salary or salary range if mentioned. **IMPORTANT:** If NOT explicitly mentioned, provide a realistic market estimate based on the job title, location, and company, labeled clearly as "(Estimated: $Xk - $Yk)".
14. **compensation_and_benefits**: List benefits and perks EXCLUDING salary - medical, dental, vision, 401k, PTO, bonuses, etc.

Be thorough but avoid duplicates. Extract exactly what's in the posting."""
    
    def _run_extraction(self, job_text: str) -> JobPosting:
        """Run the LLM extraction and return structured result."""
        import time
        print("  🤖 Calling LLM for extraction...")
        start = time.time()
        
        result = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            response_model=JobPosting,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Parse this job posting:\n\n{job_text}"}
            ],
            temperature=0.0,
            max_tokens=6000,
            max_retries=2,
        )
        
        elapsed = time.time() - start
        print(f"  ⏱ LLM call took {elapsed:.1f}s")
        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def parse_job_posting(
    job_text: str = None,
    file_path: str = None,
    api_key: Optional[str] = None
) -> JobPosting:
    """
    Convenience function to parse a job posting.
    
    Args:
        job_text: Raw job posting text (provide this OR file_path)
        file_path: Path to job posting file (provide this OR job_text)
        api_key: Optional API key
        
    Returns:
        JobPosting result
    """
    parser = JobParser(api_key)
    
    if file_path:
        return parser.parse_file(file_path)
    elif job_text:
        return parser.parse(job_text)
    else:
        raise ValueError("Provide either job_text or file_path")
