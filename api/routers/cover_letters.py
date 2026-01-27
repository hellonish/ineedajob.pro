"""
Cover Letters Router - CRUD
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
from ..schemas import CoverLetterCreate, CoverLetterUpdate, CoverLetterResponse
from ..models import User, Job, CoverLetter, UserProfile

router = APIRouter(prefix="/api/cover-letters", tags=["Cover Letters"])


@router.post("", response_model=CoverLetterResponse)
async def create_cover_letter(
    data: CoverLetterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate cover letter."""
    from engine.cover_letter import generate_cover_letter
    
    # Get job if provided
    job = None
    job_posting = {}
    
    if data.job_id:
        job = db.query(Job).filter(
            Job.id == str(data.job_id),
            Job.user_id == current_user.id
        ).first()
        if job:
            job_posting = job.job_posting
    
    # Get User Profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    unified_profile = profile.unified_profile if profile else {}
    
    # Generate cover letter
    result = generate_cover_letter(
        job_posting=job_posting,
        unified_profile=unified_profile,  
        mode=data.mode.value
    )
    
    # Save to database
    cover_letter = CoverLetter(
        user_id=current_user.id,
        job_id=str(data.job_id) if data.job_id else None,
        mode=data.mode.value,
        content=result.model_dump()
    )
    db.add(cover_letter)
    db.commit()
    db.refresh(cover_letter)
    
    return cover_letter


@router.get("", response_model=List[CoverLetterResponse])
async def list_cover_letters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's cover letters."""
    letters = db.query(CoverLetter).filter(
        CoverLetter.user_id == current_user.id
    ).order_by(CoverLetter.updated_at.desc()).all()
    
    return letters


@router.get("/{letter_id}", response_model=CoverLetterResponse)
async def get_cover_letter(
    letter_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cover letter."""
    letter = db.query(CoverLetter).filter(
        CoverLetter.id == str(letter_id),
        CoverLetter.user_id == current_user.id
    ).first()
    
    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    return letter


@router.patch("/{letter_id}", response_model=CoverLetterResponse)
async def update_cover_letter(
    letter_id: UUID,
    update: CoverLetterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cover letter."""
    letter = db.query(CoverLetter).filter(
        CoverLetter.id == str(letter_id),
        CoverLetter.user_id == current_user.id
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
    db: Session = Depends(get_db)
):
    """Delete cover letter."""
    letter = db.query(CoverLetter).filter(
        CoverLetter.id == str(letter_id),
        CoverLetter.user_id == current_user.id
    ).first()
    
    if not letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    db.delete(letter)
    db.commit()
    return {"message": "Cover letter deleted"}
