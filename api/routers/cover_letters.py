"""
Cover Letters Router - CRUD + JD Analysis
"""

import sys
import os
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ..database import get_db
from ..auth import get_current_user
from ..schemas import (
    CoverLetterCreate, CoverLetterUpdate, CoverLetterResponse,
    JDToneAnalysisResponse,
)
from ..models import User, Job, CoverLetter, UserProfile
from engine.models import LLMClient

router = APIRouter(prefix="/api/cover-letters", tags=["Cover Letters"])


def _get_user_llm(user: User) -> LLMClient:
    return LLMClient.from_user_settings({
        "llm_provider": user.llm_provider or "grok",
        "llm_model": user.llm_model,
    })


def _parse_jd_text(jd_text: str, company_name: str = None) -> dict:
    """Parse raw JD text into a structured job_posting dict."""
    from engine.job.parser import JobParser
    parsed = JobParser().parse(jd_text)
    job_posting = parsed.model_dump()
    if company_name:
        job_posting["company_name"] = company_name
    return job_posting


@router.post("/analyze-jd", response_model=JDToneAnalysisResponse)
async def analyze_jd(
    data: CoverLetterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze a job description and recommend the best cover letter mode."""
    from engine.cover_letter import analyze_jd_tone

    job_posting = {}
    if data.job_id:
        job = db.query(Job).filter(
            Job.id == str(data.job_id),
            Job.user_id == current_user.id,
        ).first()
        if job:
            job_posting = job.job_posting
    elif data.jd_text:
        job_posting = _parse_jd_text(data.jd_text, data.company_name)

    if not job_posting:
        raise HTTPException(status_code=400, detail="Job posting required for JD analysis")

    llm = _get_user_llm(current_user)
    result = analyze_jd_tone(job_posting, llm)
    return JDToneAnalysisResponse(
        recommended_mode=result.recommended_mode,
        confidence=result.confidence,
        tone_signals=result.tone_signals,
        culture_indicators=result.culture_indicators,
        formality_level=result.formality_level,
        industry=result.industry,
        reasoning=result.reasoning,
    )


@router.post("", response_model=CoverLetterResponse)
async def create_cover_letter(
    data: CoverLetterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a cover letter."""
    from engine.cover_letter import generate_cover_letter

    job = None
    job_posting = {}

    if data.job_id:
        job = db.query(Job).filter(
            Job.id == str(data.job_id),
            Job.user_id == current_user.id,
        ).first()
        if job:
            job_posting = job.job_posting
    elif data.jd_text:
        job_posting = _parse_jd_text(data.jd_text, data.company_name)

    if not job_posting:
        raise HTTPException(
            status_code=400,
            detail="Provide either job_id or jd_text to generate a cover letter.",
        )

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id,
    ).first()
    unified_profile = profile.unified_profile if profile else {}

    company_news = None
    if data.include_news and job_posting.get("company_name"):
        try:
            from engine.news import fetch_company_news
            news_result = fetch_company_news(job_posting["company_name"], 5)
            company_news = [a.model_dump() for a in news_result.articles]
        except Exception:
            company_news = None

    llm = _get_user_llm(current_user)

    result = generate_cover_letter(
        job_posting=job_posting,
        unified_profile=unified_profile,
        llm=llm,
        mode=data.mode.value,
        custom_prompt=data.custom_prompt,
        company_news=company_news,
    )

    result_dict = result.model_dump()
    result_dict["job_title"] = job_posting.get("job_title", "")
    result_dict["company_name"] = job_posting.get("company_name", "")

    cover_letter = CoverLetter(
        user_id=current_user.id,
        job_id=str(data.job_id) if data.job_id else None,
        mode=data.mode.value,
        content=result_dict,
        custom_prompt=data.custom_prompt,
    )
    db.add(cover_letter)
    db.commit()
    db.refresh(cover_letter)

    return cover_letter


@router.get("", response_model=List[CoverLetterResponse])
async def list_cover_letters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's cover letters."""
    letters = db.query(CoverLetter).filter(
        CoverLetter.user_id == current_user.id,
    ).order_by(CoverLetter.updated_at.desc()).all()
    return letters


@router.get("/{letter_id}", response_model=CoverLetterResponse)
async def get_cover_letter(
    letter_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get cover letter."""
    letter = db.query(CoverLetter).filter(
        CoverLetter.id == str(letter_id),
        CoverLetter.user_id == current_user.id,
    ).first()

    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")

    return letter


@router.patch("/{letter_id}", response_model=CoverLetterResponse)
async def update_cover_letter(
    letter_id: UUID,
    update: CoverLetterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update cover letter."""
    letter = db.query(CoverLetter).filter(
        CoverLetter.id == str(letter_id),
        CoverLetter.user_id == current_user.id,
    ).first()

    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")

    if update.full_letter:
        letter.content = {**letter.content, "full_letter": update.full_letter}
    if update.content:
        letter.content = {**letter.content, **update.content}

    db.commit()
    db.refresh(letter)
    return letter


@router.delete("/{letter_id}")
async def delete_cover_letter(
    letter_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete cover letter."""
    letter = db.query(CoverLetter).filter(
        CoverLetter.id == str(letter_id),
        CoverLetter.user_id == current_user.id,
    ).first()

    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")

    db.delete(letter)
    db.commit()
    return {"message": "Cover letter deleted"}
