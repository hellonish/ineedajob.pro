"""
Cover Letter Models - Pydantic schemas for cover letter generation.
"""

from pydantic import BaseModel, Field


class CoverLetter(BaseModel):
    """Generated cover letter content."""
    
    # Header
    greeting: str = Field(
        default="Dear Hiring Manager,",
        description="Opening greeting"
    )
    
    # Body paragraphs
    opening_paragraph: str = Field(
        default="",
        description="Introduction - role interest and how you found it"
    )
    experience_paragraph: str = Field(
        default="",
        description="Relevant experience and achievements"
    )
    skills_paragraph: str = Field(
        default="",
        description="Key skills matching the job requirements"
    )
    motivation_paragraph: str = Field(
        default="",
        description="Why this company/role interests you"
    )
    closing_paragraph: str = Field(
        default="",
        description="Call to action and thank you"
    )
    
    # Sign off
    sign_off: str = Field(
        default="Best regards,",
        description="Closing salutation"
    )
    
    # Full formatted letter
    full_letter: str = Field(
        default="",
        description="Complete formatted cover letter"
    )
