"""
Discrepancy Models - Pydantic schemas for profile comparison.

Provides structured output for comparing Resume, LinkedIn, and Portfolio data.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# COMPARISON MODELS
# ============================================================================

class ProfileItem(BaseModel):
    """Single item with values from each source for comparison."""
    category: str = Field(
        description="Category of the item: skill, job_title, company, date, project, education, certification, achievement"
    )
    field: str = Field(
        description="The specific item being compared (e.g., 'Python', 'Current Role', 'Company X End Date')"
    )
    resume_value: Optional[str] = Field(
        default=None,
        description="Value from resume (empty string if not present)"
    )
    linkedin_value: Optional[str] = Field(
        default=None,
        description="Value from LinkedIn (empty string if not present)"
    )
    portfolio_value: Optional[str] = Field(
        default=None,
        description="Value from portfolio (empty string if not present)"
    )
    status: str = Field(
        default="match",
        description="Comparison status: 'match' (all same), 'mismatch' (different values), 'partial' (some missing)"
    )


class DiscrepancyItem(BaseModel):
    """Detailed discrepancy with explanation."""
    field: str = Field(description="What's being compared (e.g., 'Job Title', 'Dates')")
    resume: Optional[str] = Field(default=None, description="Value from resume")
    linkedin: Optional[str] = Field(default=None, description="Value from LinkedIn")
    portfolio: Optional[str] = Field(default=None, description="Value from portfolio")
    issue: str = Field(default="", description="Description of the discrepancy")
    severity: str = Field(default="low", description="low, medium, or high")


# ============================================================================
# LEGACY MODELS (kept for backward compatibility)
# ============================================================================


class SkillsAnalysis(BaseModel):
    """Optimized skill comparison to save tokens."""
    matching_skills: List[str] = Field(description="Skills present in multiple sources")
    missing_from_resume: List[str] = Field(description="Skills in LinkedIn/Portfolio but NOT in Resume")
    missing_from_linkedin: List[str] = Field(description="Skills in Resume/Portfolio but NOT in LinkedIn")
    missing_from_portfolio: List[str] = Field(description="Skills in Resume/LinkedIn but NOT in Portfolio")


# ============================================================================
# LEGACY MODELS (kept for backward compatibility but deprecated)
# ============================================================================

class SkillComparison(BaseModel):
    """Skills across all sources - kept for backward compatibility."""
    skill: str = Field(description="Skill name")
    in_resume: bool = Field(default=False)
    in_linkedin: bool = Field(default=False)
    in_portfolio: bool = Field(default=False)


# ============================================================================
# MAIN RESULT MODEL
# ============================================================================

class ProfileDiscrepancy(BaseModel):
    """Complete discrepancy analysis between profile sources."""
    
    # New granular comparison table (Exclude individual skills here to save tokens)
    comparison_table: List[ProfileItem] = Field(
        default_factory=list,
        description="Comparison of non-skill items (Job Titles, Companies, Dates, Education, Projects)"
    )
    
    # Optimized Skills Analysis
    skills_analysis: SkillsAnalysis = Field(
        description="Aggregated analysis of skills to reduce token usage"
    )
    
    # Filtered views
    mismatches: List[ProfileItem] = Field(
        default_factory=list,
        description="Items with different/conflicting values across sources"
    )
    partial_presence: List[ProfileItem] = Field(
        default_factory=list,
        description="Items missing from at least one source"
    )
    fully_consistent: List[ProfileItem] = Field(
        default_factory=list,
        description="Items that match across all available sources"
    )
    
    # Detailed discrepancies with explanations
    discrepancies: List[DiscrepancyItem] = Field(
        default_factory=list,
        description="Detailed discrepancy explanations with severity"
    )
    
    # Legacy skill comparison (for backward compatibility)
    skill_comparison: List[SkillComparison] = Field(
        default_factory=list,
        description="Skills matrix across sources"
    )
    
    # Summary metrics
    consistency_score: int = Field(
        default=100,
        description="Overall consistency percentage (0-100)"
    )
    
    # Actionable recommendations
    recommendations: List[str] = Field(
        default_factory=list,
        description="Specific fixes to improve consistency"
    )
