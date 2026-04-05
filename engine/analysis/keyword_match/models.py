"""
Keyword Match - Match job keywords against resume and suggest improvements.
"""

from typing import List
from pydantic import BaseModel, Field


class ResumeSuggestion(BaseModel):
    """Single suggestion for resume improvement."""
    action: str = Field(description="ADD, UPDATE, or DELETE")
    section: str = Field(description="Resume section to modify (e.g., skills, work_experience)")
    target: str = Field(default="", description="The specific line/item to update or delete")
    suggestion: str = Field(description="The new content or modification")
    keyword_addressed: str = Field(description="Which job keyword this addresses")
    reason: str = Field(default="", description="Why this change will help")


class KeywordMatchResult(BaseModel):
    """Complete keyword matching result."""
    # Keywords found in resume
    keywords_found: List[str] = Field(default_factory=list, description="Job keywords found in resume")
    keywords_missing: List[str] = Field(default_factory=list, description="Job keywords NOT found in resume")
    
    # Match score
    keyword_match_score: float = Field(default=0.0, description="Percentage of keywords found (0-100)")
    
    # Suggestions to incorporate missing keywords
    suggestions: List[ResumeSuggestion] = Field(default_factory=list, description="How to add missing keywords")
    
    # Summary
    total_keywords: int = Field(default=0)
    matched_count: int = Field(default=0)
