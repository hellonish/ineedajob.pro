"""
Jobs Router - CRUD + Tracking + Re-evaluation
"""

import sys
import os
from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session

# Add engine to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ..database import get_db
from ..auth import get_current_user
from ..schemas import (
    JobCreate, JobUpdate, JobResponse, JobListResponse,
    ReEvaluateRequest, ReEvaluateResponse, JobStatusEnum
)
from ..models import User, Job, ResumeHistory, JobStatus

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new job analysis."""
    from engine.analysis import analyze_resume
    
    # Run analysis
    result = analyze_resume(
        job_posting=job_data.job_posting,
        resume=job_data.resume,
        unified_profile=job_data.unified_profile,
        today_date=date.today().isoformat()
    )
    
    # Create job record
    job = Job(
        user_id=current_user.id,
        job_posting=job_data.job_posting,
        analysis_result=result.model_dump(),
        status=JobStatus.TRACKED
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Add initial resume to history
    history = ResumeHistory(
        job_id=job.id,
        version=1,
        resume_data=job_data.resume,
        score=result.final_score
    )
    db.add(history)
    db.commit()
    
    return job


@router.get("", response_model=List[JobListResponse])
async def list_jobs(
    status: Optional[JobStatusEnum] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user's jobs, optionally filtered by status."""
    query = db.query(Job).filter(Job.user_id == current_user.id)
    
    if status:
        query = query.filter(Job.status == status.value)
    
    jobs = query.order_by(Job.updated_at.desc()).all()
    
    # Add final score from analysis result
    result = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "job_posting": job.job_posting,
            "status": job.status,
            "final_score": job.analysis_result.get("final_score") if job.analysis_result else None,
            "created_at": job.created_at
        }
        result.append(JobListResponse(**job_dict))
    
    return result


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job with full data including resume history."""
    job = db.query(Job).filter(
        Job.id == str(job_id),
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    update: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update job status, notes, or job link."""
    job = db.query(Job).filter(
        Job.id == str(job_id),
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if update.status:
        job.status = update.status.value
    if update.user_notes is not None:
        job.user_notes = update.user_notes
    if update.job_link is not None:
        # Update job_link within the job_posting JSON
        job_posting = dict(job.job_posting)
        if update.job_link == "":
            # Remove job_link if empty string (delete)
            job_posting.pop("job_link", None)
        else:
            job_posting["job_link"] = update.job_link
        job.job_posting = job_posting
    
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
async def delete_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete job."""
    job = db.query(Job).filter(
        Job.id == str(job_id),
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}


@router.post("/{job_id}/reevaluate", response_model=ReEvaluateResponse)
async def reevaluate_job(
    job_id: UUID,
    request: ReEvaluateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Re-evaluate job with modified resume."""
    from engine.analysis.reevaluate import reevaluate_resume
    
    job = db.query(Job).filter(
        Job.id == str(job_id),
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get previous score
    previous_score = job.analysis_result.get("final_score") if job.analysis_result else None
    
    # Run re-evaluation
    result = reevaluate_resume(
        job_posting=job.job_posting,
        modified_resume=request.modified_resume,
        previous_score=previous_score,
        today_date=date.today().isoformat()
    )
    
    # Get next version number
    latest = db.query(ResumeHistory).filter(
        ResumeHistory.job_id == str(job_id)
    ).order_by(ResumeHistory.version.desc()).first()
    next_version = (latest.version + 1) if latest else 1
    
    # Add to resume history
    history = ResumeHistory(
        job_id=job_id,
        version=next_version,
        resume_data=request.modified_resume,
        score=result.final_score
    )
    db.add(history)
    
    # Update job analysis result
    job.analysis_result = {
        **job.analysis_result,
        "final_score": result.final_score,
        "qualification_match_score": result.qualification_match_score,
        "skill_match_score": result.skill_match_score,
        "formatting_score": result.formatting_score,
        "keyword_match_score": result.keyword_match_score
    }
    
    db.commit()
    
    return result


@router.post("/{job_id}/parse-resume")
async def parse_resume_for_job(
    job_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parse a resume PDF for re-evaluation without saving to user's main profile.
    Returns the parsed resume data that can be used in the Resume Editor.
    """
    from engine.profile import parse_resume
    
    # Verify job exists and belongs to user
    job = db.query(Job).filter(
        Job.id == str(job_id),
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Parse resume
    try:
        parsed_data = parse_resume(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
    
    return {
        "success": True,
        "filename": file.filename,
        "parsed_resume": parsed_data
    }
