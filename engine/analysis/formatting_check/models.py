"""
Formatting Check - Analyze resume for formatting and chronological issues.
"""

from typing import List
from pydantic import BaseModel, Field


class FormattingIssue(BaseModel):
    """Single formatting issue found in resume."""
    issue_type: str = Field(description="Type: grammar, formatting, consistency, clarity")
    section: str = Field(description="Resume section where issue was found")
    description: str = Field(description="Description of the issue")
    suggestion: str = Field(default="", description="How to fix this issue")
    severity: str = Field(default="low", description="low, medium, high")


class ChronologicalIssue(BaseModel):
    """Chronological issue in resume timeline."""
    issue_type: str = Field(description="Type: gap, overlap, inconsistent_dates, wrong_order")
    description: str = Field(description="Description of the chronological issue")
    affected_items: List[str] = Field(default_factory=list, description="Jobs/education affected")
    suggestion: str = Field(default="", description="How to fix this issue")


class FormattingCheckResult(BaseModel):
    """Complete formatting check result."""
    formatting_issues: List[FormattingIssue] = Field(default_factory=list)
    chronological_issues: List[ChronologicalIssue] = Field(default_factory=list)
    
    # Summary
    total_formatting_issues: int = Field(default=0)
    total_chronological_issues: int = Field(default=0)
    overall_quality_score: int = Field(default=100, description="0-100 score")
