"""
Re-evaluation Models - Scoring-only analysis results.
"""

from typing import List, Dict
from pydantic import BaseModel, Field


class ReEvaluationResult(BaseModel):
    """Result from re-evaluating a modified resume - scores only, no suggestions."""
    
    # Qualification scores
    required_qualifications_matched: int = Field(default=0)
    required_qualifications_total: int = Field(default=0)
    qualification_match_score: float = Field(default=0.0, description="Percentage 0-100")
    
    # Skill scores
    technical_skills_matched: int = Field(default=0)
    technical_skills_total: int = Field(default=0)
    soft_skills_matched: int = Field(default=0)
    soft_skills_total: int = Field(default=0)
    skill_match_score: float = Field(default=0.0, description="Percentage 0-100")
    
    # Formatting score
    formatting_score: int = Field(default=100, description="0-100")
    formatting_issues_count: int = Field(default=0)
    
    # Keyword score
    keyword_match_score: float = Field(default=0.0, description="Percentage 0-100")
    keywords_found: int = Field(default=0)
    keywords_total: int = Field(default=0)
    
    # Final weighted score
    final_score: float = Field(default=0.0, description="Weighted average 0-100")
    
    # Score changes from previous (optional)
    score_change: float = Field(default=0.0, description="Change from previous score")
    improved: bool = Field(default=False, description="True if score improved")
