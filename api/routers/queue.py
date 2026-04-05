"""
Queue Router - Job Queue Management
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..auth import get_current_user
from ..models import User, Job, JobStatus
from ..tasks import analyze_job_task


router = APIRouter(prefix="/api/queue", tags=["Queue"])


class QueueJobRequest(BaseModel):
    """Request to add job to queue."""
    job_posting: dict
    resume: dict
    unified_profile: Optional[dict] = None


class QueueJobResponse(BaseModel):
    """Response after queuing a job."""
    job_id: str
    task_id: str
    position: int
    status: str


class QueueStatusResponse(BaseModel):
    """Queue status for a user."""
    queued: int
    processing: int
    jobs: List[dict]


@router.post("/jobs", response_model=QueueJobResponse)
async def queue_job(
    request: QueueJobRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a job to the analysis queue."""
    
    # Create job in database with queued status
    job = Job(
        user_id=current_user.id,
        job_posting=request.job_posting,
        status="queued"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Submit to Celery queue
    task = analyze_job_task.delay(
        job_id=str(job.id),
        job_posting=request.job_posting,
        resume=request.resume,
        unified_profile=request.unified_profile
    )
    
    # Count position in queue
    queued_count = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.status.in_(["queued", "processing"])
    ).count()
    
    return QueueJobResponse(
        job_id=str(job.id),
        task_id=task.id,
        position=queued_count,
        status="queued"
    )


@router.post("/jobs/batch", response_model=List[QueueJobResponse])
async def queue_multiple_jobs(
    requests: List[QueueJobRequest],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add multiple jobs to the queue at once."""
    results = []
    
    for i, request in enumerate(requests):
        job = Job(
            user_id=current_user.id,
            job_posting=request.job_posting,
            status="queued"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        task = analyze_job_task.delay(
            job_id=str(job.id),
            job_posting=request.job_posting,
            resume=request.resume,
            unified_profile=request.unified_profile
        )
        
        results.append(QueueJobResponse(
            job_id=str(job.id),
            task_id=task.id,
            position=i + 1,
            status="queued"
        ))
    
    return results


@router.get("/status", response_model=QueueStatusResponse)
async def get_queue_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current queue status for user."""
    
    queued = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.status == "queued"
    ).count()
    
    processing = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.status == "processing"
    ).count()
    
    jobs = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.status.in_(["queued", "processing"])
    ).order_by(Job.created_at).all()
    
    return QueueStatusResponse(
        queued=queued,
        processing=processing,
        jobs=[
            {
                "id": str(j.id),
                "status": j.status,
                "job_title": j.job_posting.get("job_title", "Unknown"),
                "company": j.job_posting.get("company_name", "Unknown")
            }
            for j in jobs
        ]
    )


@router.delete("/jobs/{job_id}")
async def cancel_queued_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a queued job (only if not yet processing)."""
    
    job = db.query(Job).filter(
        Job.id == str(job_id),
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "queued":
        raise HTTPException(status_code=400, detail="Can only cancel queued jobs")
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job cancelled"}
