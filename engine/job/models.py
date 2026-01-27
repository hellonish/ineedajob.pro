"""
Job Posting Models - Pydantic schemas for job parsing.

Provides structured output for extracting qualifications, skills, and keywords from job postings.
"""

from typing import List
from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """Structured extraction from a job posting."""
    
    # Job metadata
    job_title: str = Field(
        default="",
        description="The title of the job position"
    )
    company_name: str = Field(
        default="",
        description="Name of the company"
    )
    company_about: str = Field(
        default="",
        description="About the company - their mission, values, what they do"
    )
    location: str = Field(
        default="",
        description="Job location (city, state, remote, etc.)"
    )
    job_description: str = Field(
        default="",
        description="Overall job description summarizing the role"
    )
    
    # Qualifications
    required_qualifications: List[str] = Field(
        default_factory=list,
        description="Required qualifications explicitly stated in the job posting"
    )
    preferred_qualifications: List[str] = Field(
        default_factory=list,
        description="Preferred/nice-to-have qualifications"
    )
    
    # Skills
    technical_skills: List[str] = Field(
        default_factory=list,
        description="Explicitly mentioned technical skills (programming languages, tools, frameworks, etc.)"
    )
    soft_skills: List[str] = Field(
        default_factory=list,
        description="Implied or explicitly mentioned soft skills (communication, teamwork, leadership, etc.)"
    )
    
    # Keywords
    job_keywords: List[str] = Field(
        default_factory=list,
        description="Industry-specific keywords and buzzwords specific to this job"
    )
    
    # Additional context
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Key responsibilities and duties"
    )
    experience_level: str = Field(
        default="",
        description="Required experience level (entry-level, mid, senior, etc.)"
    )
    salary_range: str = Field(
        default="",
        description="Salary range if mentioned (e.g., $100K/yr, $80K-$120K)"
    )
    compensation_and_benefits: List[str] = Field(
        default_factory=list,
        description="Benefits and perks (medical, dental, 401k, PTO, etc.) - NOT including salary"
    )
