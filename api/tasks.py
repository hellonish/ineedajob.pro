"""
Celery Tasks for Job Analysis
"""

import os
import sys
from datetime import date
from celery import current_task

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.celery_app import celery_app
from api.websocket import notify_job_status


@celery_app.task(bind=True)
def analyze_job_task(self, job_id: str, job_posting: dict, resume: dict, unified_profile: dict = None):
    """
    Background task to analyze a job.
    Sends WebSocket updates during processing.
    """
    from engine.analysis import analyze_resume
    from api.database import SessionLocal
    from api.models import Job, ResumeHistory
    
    # Notify: started
    notify_job_status(job_id, "processing", {"message": "Analysis started"})
    
    try:
        # Parse job posting if it only has raw_text (no structured data)
        if job_posting.get('raw_text') and not job_posting.get('required_qualifications'):
            from engine.job import parse_job_posting
            notify_job_status(job_id, "processing", {"message": "Parsing job posting..."})
            parsed = parse_job_posting(job_text=job_posting['raw_text'])
            # Merge parsed data into job_posting
            job_posting = {**job_posting, **parsed.model_dump()}
        
        # Run analysis
        notify_job_status(job_id, "processing", {"message": "Running qualification check..."})
        
        result = analyze_resume(
            job_posting=job_posting,
            resume=resume,
            unified_profile=unified_profile,
            today_date=date.today().isoformat()
        )
        
        # Update database
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.analysis_result = result.model_dump()
                job.job_posting = job_posting  # Save parsed job posting data
                job.status = "tracked"  # Update status from queued to tracked
                
                # Add to resume history
                history = ResumeHistory(
                    job_id=job_id,
                    version=1,
                    resume_data=resume,
                    score=result.final_score
                )
                db.add(history)
                db.commit()
        finally:
            db.close()
        
        # Notify: completed
        notify_job_status(job_id, "completed", {
            "message": "Analysis complete",
            "final_score": result.final_score
        })
        
        return {"status": "completed", "final_score": result.final_score}
        
    except Exception as e:
        # Delete the failed job from database
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                db.delete(job)
                db.commit()
                print(f"🗑️ Deleted failed job {job_id}")
        finally:
            db.close()
        
        # Notify: failed
        notify_job_status(job_id, "failed", {"message": str(e)})
        raise


@celery_app.task(bind=True)
def reevaluate_job_task(self, job_id: str, modified_resume: dict, previous_score: float = None):
    """
    Background task to re-evaluate a job with modified resume.
    """
    from engine.analysis.reevaluate import reevaluate_resume
    from api.database import SessionLocal
    from api.models import Job, ResumeHistory
    
    notify_job_status(job_id, "processing", {"message": "Re-evaluation started"})
    
    try:
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            # Run re-evaluation
            result = reevaluate_resume(
                job_posting=job.job_posting,
                modified_resume=modified_resume,
                previous_score=previous_score,
                today_date=date.today().isoformat()
            )
            
            # Get next version
            latest = db.query(ResumeHistory).filter(
                ResumeHistory.job_id == job_id
            ).order_by(ResumeHistory.version.desc()).first()
            next_version = (latest.version + 1) if latest else 1
            
            # Update database
            job.analysis_result = {
                **job.analysis_result,
                "final_score": result.final_score,
                "qualification_match_score": result.qualification_match_score,
                "skill_match_score": result.skill_match_score,
                "formatting_score": result.formatting_score,
                "keyword_match_score": result.keyword_match_score
            }
            
            history = ResumeHistory(
                job_id=job_id,
                version=next_version,
                resume_data=modified_resume,
                score=result.final_score
            )
            db.add(history)
            db.commit()
            
        finally:
            db.close()
        
        notify_job_status(job_id, "completed", {
            "message": "Re-evaluation complete",
            "final_score": result.final_score,
            "score_change": result.score_change,
            "improved": result.improved
        })
        
        return result.model_dump()
        
    except Exception as e:
        notify_job_status(job_id, "failed", {"message": str(e)})
        raise
