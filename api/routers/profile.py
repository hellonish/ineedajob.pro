"""
Profile Router
"""

import os
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..schemas import UserProfileResponse, ProfileUploadResponse, AdditionalContextUpdate
from ..models import User, UserProfile

from engine.profile.parsers import ResumeParser, LinkedInParser, PortfolioParser
from engine.profile.unifier import create_unified_profile

router = APIRouter(prefix="/api/profile", tags=["Profile"])

UPLOAD_DIR = "api/uploads"

def _get_or_create_profile(db: Session, user_id: str) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.get("", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile status."""
    return _get_or_create_profile(db, current_user.id)

@router.post("/upload", response_model=ProfileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    type: str = Form(...),  # resume, linkedin, portfolio
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a profile file."""
    if type not in ["resume", "linkedin", "portfolio"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Create upload directory
    user_dir = os.path.join(UPLOAD_DIR, current_user.id)
    os.makedirs(user_dir, exist_ok=True)

    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{type}{file_ext}"
    file_path = os.path.join(user_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse file
    try:
        # Re-read file logic
        with open(file_path, "rb") as f:
            file_content = f.read()

        if type == "resume":
            parser = ResumeParser()
        elif type == "linkedin":
            parser = LinkedInParser()
        elif type == "portfolio":
            parser = PortfolioParser()
        
        parsed_result = parser.parse(file_content)
        parsed_data = parsed_result.model_dump() if hasattr(parsed_result, "model_dump") else parsed_result.dict()

    except Exception as e:
        # cleanup file? maybe keep for debugging
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    # Update DB
    profile = _get_or_create_profile(db, current_user.id)
    
    if type == "resume":
        profile.resume_path = file_path
        profile.resume_data = parsed_data
    elif type == "linkedin":
        profile.linkedin_path = file_path
        profile.linkedin_data = parsed_data
    elif type == "portfolio":
        profile.portfolio_path = file_path
        profile.portfolio_data = parsed_data
    
    db.commit()
    
    return {
        "file_type": type,
        "filename": file.filename,
        "parsed_data": parsed_data
    }

@router.get("/file/{file_type}")
async def get_profile_file(
    file_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Serve a profile file securely."""
    if file_type not in ["resume", "linkedin", "portfolio"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    profile = _get_or_create_profile(db, current_user.id)
    file_path = None

    if file_type == "resume":
        file_path = profile.resume_path
    elif file_type == "linkedin":
        file_path = profile.linkedin_path
    elif file_type == "portfolio":
        file_path = profile.portfolio_path

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


@router.post("/unified", response_model=UserProfileResponse)
async def create_unified(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Unified Profile from uploaded files, then auto-extract structured profile."""
    profile = _get_or_create_profile(db, current_user.id)

    sources = {}
    if profile.resume_data:
        sources["resume"] = profile.resume_data
    if profile.linkedin_data:
        sources["linkedin"] = profile.linkedin_data
    if profile.portfolio_data:
        sources["portfolio"] = profile.portfolio_data

    if not sources:
        raise HTTPException(status_code=400, detail="No files uploaded to unify")

    if len(sources) == 1:
        unified = list(sources.values())[0]
    else:
        unified = create_unified_profile(sources)

    profile.unified_profile = unified
    db.commit()

    # Auto-extract structured profile for JobLens
    try:
        from engine.joblens import extract_profile
        from engine.models.llm import LLMClient
        llm = LLMClient.from_user_settings({
            "llm_provider": current_user.llm_provider or "grok",
            "llm_model": current_user.llm_model,
        })
        extracted = extract_profile(unified, llm, profile.additional_context)
        profile.extracted_profile = extracted.model_dump()
        db.commit()
    except Exception as e:
        # Non-fatal — unified profile still saved
        import logging
        logging.getLogger(__name__).warning(f"Auto-extract profile failed: {e}")

    db.refresh(profile)
    return profile


@router.patch("/additional-context", response_model=UserProfileResponse)
async def update_additional_context(
    data: AdditionalContextUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save user-supplied additional context (links, achievements, portfolio notes)."""
    profile = _get_or_create_profile(db, current_user.id)
    profile.additional_context = data.additional_context
    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/{file_type}", response_model=UserProfileResponse)
async def delete_file(
    file_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file and its data."""
    if file_type not in ["resume", "linkedin", "portfolio"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
        
    profile = _get_or_create_profile(db, current_user.id)
    
    if file_type == "resume":
        if profile.resume_path and os.path.exists(profile.resume_path):
            os.remove(profile.resume_path)
        profile.resume_path = None
        profile.resume_data = None
        
    elif file_type == "linkedin":
        if profile.linkedin_path and os.path.exists(profile.linkedin_path):
            os.remove(profile.linkedin_path)
        profile.linkedin_path = None
        profile.linkedin_data = None
        
    elif file_type == "portfolio":
        if profile.portfolio_path and os.path.exists(profile.portfolio_path):
            os.remove(profile.portfolio_path)
        profile.portfolio_path = None
        profile.portfolio_data = None
    
    db.commit()
    db.refresh(profile)
    return profile
