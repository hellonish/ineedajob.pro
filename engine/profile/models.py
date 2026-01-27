"""
Profile Models - Shared Pydantic schemas for all parsers.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ============================================================================
# HYBRID SCHEMAS
# ============================================================================

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class Basics(BaseModel):
    name: str
    contact_info: ContactInfo
    location: Optional[str] = Field(None, description="City, State, Country")

class WorkExperienceItem(BaseModel):
    job_title: str
    company_name: str
    start_date: str = Field(..., description="YYYY-MM")
    end_date: Optional[str] = Field(None, description="YYYY-MM or 'Present'")
    is_current: bool
    description: List[str] = Field(default_factory=list, description="Bullet points of responsibilities and achievements")

class EducationItem(BaseModel):
    institution: str
    degree: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[str] = None

class HybridResume(BaseModel):
    """
    Hybrid Resume Model:
    - Strictly typed 'Core' sections for reliable analytics.
    - Flexible 'Dynamic' bucket for context preservation.
    """
    basics: Basics
    work_experience: List[WorkExperienceItem]
    skills: List[str]
    education: List[EducationItem]
    dynamic_sections: Dict[str, Any] = Field(
        default_factory=dict,
        description="Non-standard sections (e.g., Awards, Publications) with section header as key"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Return model as dictionary."""
        return self.model_dump()
