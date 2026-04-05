"""
JobLens Router - 6-step job application intelligence pipeline.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Job, UserProfile, JobLensSession
from ..schemas import (
    JobLensSessionCreate, JobLensSessionResponse,
    ExtractProfileRequest, ParseJDRequest, CompanyIntelRequest,
    MatchAnalysisRequest, ContactStrategyRequest, ActionPlanRequest,
)

from engine.models.llm import LLMClient
from engine.joblens import (
    extract_profile, parse_jd, analyze_company, analyze_match, find_contacts, plan_actions,
    ExtractedProfile, ParsedJD, CompanyIntel, MatchAnalysis, ContactStrategy,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/joblens", tags=["JobLens"])


def _get_llm(user: User) -> LLMClient:
    """Create LLM client from user settings."""
    return LLMClient.from_user_settings({
        "llm_provider": user.llm_provider or "grok",
        "llm_model": user.llm_model,
    })


def _get_session(session_id: str, user_id: str, db: Session) -> JobLensSession:
    """Get a JobLens session owned by the user."""
    session = db.query(JobLensSession).filter(
        JobLensSession.id == session_id,
        JobLensSession.user_id == user_id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# ============================================================================
# Session CRUD
# ============================================================================

@router.post("/sessions", response_model=JobLensSessionResponse)
async def create_session(
    data: JobLensSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new JobLens session."""
    session = JobLensSession(
        user_id=current_user.id,
        job_id=str(data.job_id) if data.job_id else None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=list[JobLensSessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all JobLens sessions for the current user."""
    sessions = db.query(JobLensSession).filter(
        JobLensSession.user_id == current_user.id
    ).order_by(JobLensSession.updated_at.desc()).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=JobLensSessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific JobLens session."""
    return _get_session(session_id, current_user.id, db)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a JobLens session."""
    session = _get_session(session_id, current_user.id, db)
    db.delete(session)
    db.commit()
    return {"detail": "Session deleted"}


# ============================================================================
# Step 1: Extract Profile
# ============================================================================

@router.post("/sessions/{session_id}/extract-profile", response_model=JobLensSessionResponse)
async def step_extract_profile(
    session_id: str,
    data: ExtractProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Step 1: Extract structured profile from user's unified profile."""
    session = _get_session(session_id, current_user.id, db)

    # Get user's unified profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile or not profile.unified_profile:
        raise HTTPException(status_code=400, detail="No unified profile found. Upload your resume first.")

    llm = _get_llm(current_user)
    result = extract_profile(profile.unified_profile, llm, data.portfolio_notes)

    session.extracted_profile = result.model_dump()
    session.current_step = max(session.current_step, 1)
    db.commit()
    db.refresh(session)
    return session


# ============================================================================
# Step 2: Parse JD
# ============================================================================

@router.post("/sessions/{session_id}/parse-jd", response_model=JobLensSessionResponse)
async def step_parse_jd(
    session_id: str,
    data: ParseJDRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Step 2: Parse job description into structured fields."""
    session = _get_session(session_id, current_user.id, db)

    # If job_id provided, get existing job posting for extra context
    job_posting = None
    if data.job_id:
        job = db.query(Job).filter(Job.id == str(data.job_id), Job.user_id == current_user.id).first()
        if job:
            job_posting = job.job_posting
            # Link session to job
            session.job_id = str(data.job_id)

    llm = _get_llm(current_user)
    result = parse_jd(data.jd_text, llm, job_posting)

    session.parsed_jd = result.model_dump()
    session.raw_jd_text = data.jd_text
    session.current_step = max(session.current_step, 2)
    db.commit()
    db.refresh(session)
    return session


# ============================================================================
# Step 3: Company Intel
# ============================================================================

@router.post("/sessions/{session_id}/company-intel", response_model=JobLensSessionResponse)
async def step_company_intel(
    session_id: str,
    data: CompanyIntelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Step 3: Research company from website and context."""
    session = _get_session(session_id, current_user.id, db)

    # Use JD context if available
    jd_context = session.raw_jd_text

    llm = _get_llm(current_user)
    result = analyze_company(
        company_name=data.company_name,
        llm=llm,
        company_website=data.company_website,
        jd_context=jd_context,
        additional_notes=data.additional_notes,
    )

    session.company_intel = result.model_dump()
    session.company_website = data.company_website
    session.current_step = max(session.current_step, 3)
    db.commit()
    db.refresh(session)
    return session


# ============================================================================
# Step 4: Match Analysis
# ============================================================================

@router.post("/sessions/{session_id}/match-analysis", response_model=JobLensSessionResponse)
async def step_match_analysis(
    session_id: str,
    data: MatchAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Step 4: Compare profile against JD with scoring."""
    session = _get_session(session_id, current_user.id, db)

    if not session.extracted_profile:
        raise HTTPException(status_code=400, detail="Run Step 1 (Extract Profile) first")
    if not session.parsed_jd:
        raise HTTPException(status_code=400, detail="Run Step 2 (Parse JD) first")

    profile = ExtractedProfile(**session.extracted_profile)
    parsed_jd = ParsedJD(**session.parsed_jd)

    llm = _get_llm(current_user)
    result = analyze_match(
        profile=profile,
        parsed_jd=parsed_jd,
        llm=llm,
        company_intel=session.company_intel,
    )

    session.match_analysis = result.model_dump()
    session.current_step = max(session.current_step, 4)
    db.commit()
    db.refresh(session)
    return session


# ============================================================================
# Step 5: Contact Strategy
# ============================================================================

@router.post("/sessions/{session_id}/contacts", response_model=JobLensSessionResponse)
async def step_contacts(
    session_id: str,
    data: ContactStrategyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Step 5: Generate contact strategy."""
    session = _get_session(session_id, current_user.id, db)

    if not session.parsed_jd:
        raise HTTPException(status_code=400, detail="Run Step 2 (Parse JD) first")

    parsed_jd = ParsedJD(**session.parsed_jd)
    company_intel = CompanyIntel(**session.company_intel) if session.company_intel else None

    # Build profile summary for context
    profile_summary = None
    if session.extracted_profile:
        ep = session.extracted_profile
        profile_summary = f"{ep.get('current_title', '')} with {ep.get('years_of_experience', '')} years experience. {ep.get('professional_summary', '')}"

    llm = _get_llm(current_user)
    result = find_contacts(
        parsed_jd=parsed_jd,
        llm=llm,
        company_intel=company_intel,
        profile_summary=profile_summary,
    )

    session.contact_strategy = result.model_dump()
    session.current_step = max(session.current_step, 5)
    db.commit()
    db.refresh(session)
    return session


# ============================================================================
# Step 6: Action Plan
# ============================================================================

@router.post("/sessions/{session_id}/action-plan", response_model=JobLensSessionResponse)
async def step_action_plan(
    session_id: str,
    data: ActionPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Step 6: Build comprehensive action plan."""
    session = _get_session(session_id, current_user.id, db)

    if not session.extracted_profile:
        raise HTTPException(status_code=400, detail="Run Step 1 (Extract Profile) first")
    if not session.parsed_jd:
        raise HTTPException(status_code=400, detail="Run Step 2 (Parse JD) first")
    if not session.match_analysis:
        raise HTTPException(status_code=400, detail="Run Step 4 (Match Analysis) first")

    profile = ExtractedProfile(**session.extracted_profile)
    parsed_jd = ParsedJD(**session.parsed_jd)
    match = MatchAnalysis(**session.match_analysis)
    company_intel = CompanyIntel(**session.company_intel) if session.company_intel else None
    contact_strategy = ContactStrategy(**session.contact_strategy) if session.contact_strategy else None

    llm = _get_llm(current_user)
    result = plan_actions(
        profile=profile,
        parsed_jd=parsed_jd,
        match_analysis=match,
        llm=llm,
        company_intel=company_intel,
        contact_strategy=contact_strategy,
    )

    session.action_plan = result.model_dump()
    session.current_step = max(session.current_step, 6)
    db.commit()
    db.refresh(session)
    return session
