"""
Qualification Check - Compare job qualifications against resume.

Outputs check (✓) or cross (✗) for each qualification requirement.
"""

from typing import List
from pydantic import BaseModel, Field


class QualificationMatch(BaseModel):
    """Single qualification match result."""
    qualification: str = Field(description="The qualification being checked")
    matched: bool = Field(description="True if resume matches this qualification")
    evidence: str = Field(default="", description="Evidence from resume supporting the match")
    category: str = Field(default="required", description="required, preferred, technical_skill, soft_skill")


class QualificationCheckResult(BaseModel):
    """Complete qualification check result."""
    required_qualifications: List[QualificationMatch] = Field(default_factory=list)
    preferred_qualifications: List[QualificationMatch] = Field(default_factory=list)
    technical_skills: List[QualificationMatch] = Field(default_factory=list)
    soft_skills: List[QualificationMatch] = Field(default_factory=list)
    
    # Summary scores
    required_match_count: int = Field(default=0)
    required_total: int = Field(default=0)
    preferred_match_count: int = Field(default=0)
    preferred_total: int = Field(default=0)
    technical_match_count: int = Field(default=0)
    technical_total: int = Field(default=0)
    soft_match_count: int = Field(default=0)
    soft_total: int = Field(default=0)
