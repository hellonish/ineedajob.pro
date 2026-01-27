"""
Pydantic Schemas for API
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID


# Enums
class JobStatusEnum(str, Enum):
    tracked = "tracked"
    queued = "queued"
    analyzing = "analyzing"
    applied = "applied"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"


class CoverLetterModeEnum(str, Enum):
    professional = "professional"
    conversational = "conversational"
    concise = "concise"
    creative = "creative"
    storytelling = "storytelling"


# User Schemas
class UserBase(BaseModel):
    email: str
    name: str
    profile_picture: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_picture: Optional[str] = None


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Job Schemas
class JobCreate(BaseModel):
    job_posting: Dict[str, Any]
    resume: Dict[str, Any]
    unified_profile: Optional[Dict[str, Any]] = None


class JobUpdate(BaseModel):
    status: Optional[JobStatusEnum] = None
    user_notes: Optional[str] = None
    job_link: Optional[str] = None


class ResumeHistoryResponse(BaseModel):
    version: int
    resume_data: Dict[str, Any]
    score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: UUID
    job_posting: Dict[str, Any]
    analysis_result: Optional[Dict[str, Any]] = None
    status: JobStatusEnum
    user_notes: Optional[str] = None
    resume_history: List[ResumeHistoryResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    id: UUID
    job_posting: Dict[str, Any]
    status: JobStatusEnum
    final_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Re-evaluation Schemas
class ReEvaluateRequest(BaseModel):
    modified_resume: Dict[str, Any]


class ReEvaluateResponse(BaseModel):
    qualification_match_score: float
    skill_match_score: float
    formatting_score: int
    keyword_match_score: float
    final_score: float
    score_change: float
    improved: bool


# Cover Letter Schemas
class CoverLetterCreate(BaseModel):
    job_id: Optional[UUID] = None
    mode: CoverLetterModeEnum = CoverLetterModeEnum.professional


class CoverLetterUpdate(BaseModel):
    full_letter: Optional[str] = None
    content: Optional[Dict[str, Any]] = None


class CoverLetterResponse(BaseModel):
    id: UUID
    job_id: Optional[UUID] = None
    mode: str
    content: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Discrepancy Schemas
class DiscrepancyCreate(BaseModel):
    unified_profile: Dict[str, Any]


class DiscrepancyResponse(BaseModel):
    id: UUID
    unified_profile: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# News Schemas
class NewsArticleResponse(BaseModel):
    title: str
    description: str
    url: str
    source: str
    published_at: str


class NewsResponse(BaseModel):
    company_name: str
    articles: List[NewsArticleResponse]
    total_results: int

# Profile Schemas
class UserProfileResponse(BaseModel):
    id: UUID
    user_id: str
    
    # File Paths (Nullable)
    resume_path: Optional[str] = None
    linkedin_path: Optional[str] = None
    portfolio_path: Optional[str] = None
    
    # Parsed Data (Nullable)
    resume_data: Optional[Dict[str, Any]] = None
    linkedin_data: Optional[Dict[str, Any]] = None
    portfolio_data: Optional[Dict[str, Any]] = None
    
    # Final Profile
    unified_profile: Optional[Dict[str, Any]] = None
    
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProfileUploadResponse(BaseModel):
    file_type: str
    filename: str
    parsed_data: Dict[str, Any]
