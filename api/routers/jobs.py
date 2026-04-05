"""
Jobs Router - CRUD + Tracking + JobLens integration
"""

import sys
import os
import asyncio
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, BackgroundTasks
from sqlalchemy import or_
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ..database import get_db
from ..auth import get_current_user
from ..schemas import (
    JobCreate, JobTrackCreate, JobUpdate, JobResponse, JobListResponse, JobStatusEnum,
    ReEvaluateRequest, ReEvaluateResponse,
)
from ..models import User, Job, ResumeHistory, UserProfile, JobLensSession, JobStatus
from ..websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


# ============================================================================
# Background: run full pipeline
# ============================================================================

async def _run_pipeline_background(job_id: str, session_id: str, user_id: str,
                                    llm_provider: str, llm_model: Optional[str],
                                    jd_text: str, company_website: Optional[str]):
    """Run the 6-step JobLens pipeline in the background with WebSocket events."""
    from ..database import SessionLocal
    from engine.joblens import (
        extract_profile, parse_jd, analyze_company, analyze_match, find_contacts, plan_actions,
        ExtractedProfile, ParsedJD, CompanyIntel, MatchAnalysis, ContactStrategy,
    )
    from engine.models.llm import LLMClient

    loop = asyncio.get_event_loop()

    def emit(step: str, event: str, data: dict = None):
        asyncio.ensure_future(manager.send_to_user(user_id, {
            "type": event,
            "session_id": session_id,
            "job_id": job_id,
            "step": step,
            **(data or {}),
        }))

    def db_write(fn):
        """Open a fresh short-lived session, run fn(db), commit, close."""
        _db = SessionLocal()
        try:
            fn(_db)
            _db.commit()
        finally:
            _db.close()

    # ── Read profile data, then immediately release the connection ──
    _db = SessionLocal()
    try:
        profile_db = _db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        unified_profile = profile_db.unified_profile if profile_db else None
        additional_context = profile_db.additional_context if profile_db else None
        cached_extracted_profile = profile_db.extracted_profile if profile_db else None
    finally:
        _db.close()

    try:
        llm = LLMClient.from_user_settings({"llm_provider": llm_provider, "llm_model": llm_model})

        # ── STEP 1 + 2 in parallel ──
        emit("profile_extract", "joblens_step_started")
        emit("jd_parse", "joblens_step_started")

        extracted_profile_result = None
        parsed_jd_result = None

        async def run_step1():
            nonlocal extracted_profile_result
            try:
                if cached_extracted_profile:
                    from engine.joblens import ExtractedProfile
                    extracted_profile_result = ExtractedProfile(**cached_extracted_profile)
                    emit("profile_extract", "joblens_step_complete", {"data": cached_extracted_profile, "cached": True})
                    return
                result = await loop.run_in_executor(
                    None, lambda: extract_profile(unified_profile, llm, additional_context)
                    if unified_profile else None
                )
                extracted_profile_result = result
                if result:
                    result_data = result.model_dump()
                    def _cache(db): db.query(UserProfile).filter(UserProfile.user_id == user_id).update({"extracted_profile": result_data})
                    db_write(_cache)
                    emit("profile_extract", "joblens_step_complete", {"data": result_data})
                else:
                    emit("profile_extract", "joblens_step_failed", {"error": "No unified profile"})
            except Exception as e:
                emit("profile_extract", "joblens_step_failed", {"error": str(e)})

        async def run_step2():
            nonlocal parsed_jd_result
            try:
                result = await loop.run_in_executor(None, lambda: parse_jd(jd_text, llm))
                parsed_jd_result = result
                emit("jd_parse", "joblens_step_complete", {"data": result.model_dump()})
            except Exception as e:
                emit("jd_parse", "joblens_step_failed", {"error": str(e)})

        await asyncio.gather(run_step1(), run_step2())

        # Save wave 1 results
        def _save_wave1(db):
            session = db.query(JobLensSession).filter(JobLensSession.id == session_id).first()
            job = db.query(Job).filter(Job.id == job_id).first()
            if extracted_profile_result:
                session.extracted_profile = extracted_profile_result.model_dump()
                session.current_step = max(session.current_step, 1)
            if parsed_jd_result:
                session.parsed_jd = parsed_jd_result.model_dump()
                session.raw_jd_text = jd_text
                session.current_step = max(session.current_step, 2)
                if job:
                    job.job_posting = {
                        "job_title": parsed_jd_result.role_title,
                        "company_name": parsed_jd_result.company_name,
                        "location": parsed_jd_result.location,
                        "remote_policy": parsed_jd_result.remote_policy,
                        "level": parsed_jd_result.level,
                        "salary_range": parsed_jd_result.salary_range,
                        "required_qualifications": parsed_jd_result.required_skills,
                        "tech_stack": parsed_jd_result.tech_stack,
                    }
        db_write(_save_wave1)

        if not parsed_jd_result:
            logger.error(f"Pipeline aborted: JD parse failed for job {job_id}")
            return

        # ── STEP 3 + 4 + 5 in parallel ──
        company_intel_result = None
        match_result = None
        contact_result = None
        company_name = parsed_jd_result.company_name

        emit("company_intel", "joblens_step_started")
        emit("match_analysis", "joblens_step_started")
        emit("contact_strategy", "joblens_step_started")

        async def run_step3():
            nonlocal company_intel_result
            try:
                result = await loop.run_in_executor(
                    None, lambda: analyze_company(company_name=company_name, llm=llm, company_website=company_website, jd_context=jd_text)
                )
                company_intel_result = result
                emit("company_intel", "joblens_step_complete", {"data": result.model_dump()})
            except Exception as e:
                emit("company_intel", "joblens_step_failed", {"error": str(e)})

        async def run_step4():
            nonlocal match_result
            try:
                if not extracted_profile_result:
                    emit("match_analysis", "joblens_step_failed", {"error": "No profile"})
                    return
                result = await loop.run_in_executor(
                    None, lambda: analyze_match(profile=extracted_profile_result, parsed_jd=parsed_jd_result, llm=llm)
                )
                match_result = result
                emit("match_analysis", "joblens_step_complete", {"data": result.model_dump()})
            except Exception as e:
                emit("match_analysis", "joblens_step_failed", {"error": str(e)})

        async def run_step5():
            nonlocal contact_result
            try:
                profile_summary = None
                if extracted_profile_result:
                    ep = extracted_profile_result
                    profile_summary = f"{ep.current_title} with {ep.years_of_experience} years experience. {ep.professional_summary}"
                result = await loop.run_in_executor(
                    None, lambda: find_contacts(parsed_jd=parsed_jd_result, llm=llm, profile_summary=profile_summary)
                )
                contact_result = result
                emit("contact_strategy", "joblens_step_complete", {"data": result.model_dump()})
            except Exception as e:
                emit("contact_strategy", "joblens_step_failed", {"error": str(e)})

        await asyncio.gather(run_step3(), run_step4(), run_step5())

        # Save wave 2 results
        def _save_wave2(db):
            session = db.query(JobLensSession).filter(JobLensSession.id == session_id).first()
            job = db.query(Job).filter(Job.id == job_id).first()
            if company_intel_result:
                session.company_intel = company_intel_result.model_dump()
                session.current_step = max(session.current_step, 3)
            if match_result:
                session.match_analysis = match_result.model_dump()
                session.current_step = max(session.current_step, 4)
                if job:
                    job.analysis_result = {"final_score": match_result.overall_score}
            if contact_result:
                session.contact_strategy = contact_result.model_dump()
                session.current_step = max(session.current_step, 5)
        db_write(_save_wave2)

        # ── STEP 6 ──
        if extracted_profile_result and match_result:
            emit("action_plan", "joblens_step_started")
            try:
                action_result = await loop.run_in_executor(
                    None, lambda: plan_actions(
                        profile=extracted_profile_result,
                        parsed_jd=parsed_jd_result,
                        match_analysis=match_result,
                        llm=llm,
                        company_intel=company_intel_result,
                        contact_strategy=contact_result,
                    )
                )
                action_data = action_result.model_dump()
                def _save_step6(db):
                    session = db.query(JobLensSession).filter(JobLensSession.id == session_id).first()
                    session.action_plan = action_data
                    session.current_step = 6
                db_write(_save_step6)
                emit("action_plan", "joblens_step_complete", {"data": action_data})
            except Exception as e:
                emit("action_plan", "joblens_step_failed", {"error": str(e)})

        # Mark job complete
        def _finalize(db):
            job = db.query(Job).filter(Job.id == job_id).first()
            if job and job.status == JobStatus.ANALYZING:
                job.status = JobStatus.TRACKED
        db_write(_finalize)

        emit("pipeline", "joblens_pipeline_complete")

    except Exception as e:
        logger.exception(f"Pipeline error for job {job_id}: {e}")
        await manager.send_to_user(user_id, {
            "type": "joblens_pipeline_failed",
            "session_id": session_id,
            "job_id": job_id,
            "error": str(e),
        })
    finally:
        db.close()


# ============================================================================
# Routes
# ============================================================================

@router.post("", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job and kick off the JobLens pipeline."""
    # Create placeholder job
    job = Job(
        user_id=current_user.id,
        job_posting={
            "job_title": "Analyzing...",
            "company_name": "Pending",
            "raw_jd": job_data.jd_text[:500],
        },
        company_website=job_data.company_website,
        status=JobStatus.ANALYZING,
    )
    db.add(job)
    db.flush()  # get job.id

    # Create JobLens session
    session = JobLensSession(
        user_id=current_user.id,
        job_id=job.id,
        raw_jd_text=job_data.jd_text,
        company_website=job_data.company_website,
    )
    db.add(session)
    db.flush()

    job.joblens_session_id = session.id
    db.commit()
    db.refresh(job)

    # Kick off pipeline in background
    background_tasks.add_task(
        _run_pipeline_background,
        job.id, session.id, current_user.id,
        current_user.llm_provider or "grok", current_user.llm_model,
        job_data.jd_text, job_data.company_website,
    )

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

    result = []
    for job in jobs:
        final_score = None
        if job.analysis_result:
            final_score = job.analysis_result.get("final_score")
        job_dict = {
            "id": job.id,
            "job_posting": job.job_posting,
            "status": job.status,
            "final_score": final_score,
            "company_website": job.company_website,
            "joblens_session_id": job.joblens_session_id,
            "created_at": job.created_at,
        }
        result.append(JobListResponse(**job_dict))

    return result


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job with full data."""
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
    """Update job status or notes."""
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
        job_posting = dict(job.job_posting)
        if update.job_link == "":
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

    # JobLensSession references jobs.id; Job has no ORM cascade for sessions, so remove them first.
    session_filters = [JobLensSession.job_id == str(job_id)]
    if job.joblens_session_id:
        session_filters.append(JobLensSession.id == job.joblens_session_id)
    db.query(JobLensSession).filter(
        JobLensSession.user_id == current_user.id,
        or_(*session_filters),
    ).delete(synchronize_session=False)

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
    from datetime import date

    job = db.query(Job).filter(
        Job.id == str(job_id),
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    previous_score = job.analysis_result.get("final_score") if job.analysis_result else None

    result = reevaluate_resume(
        job_posting=job.job_posting,
        modified_resume=request.modified_resume,
        previous_score=previous_score,
        today_date=date.today().isoformat()
    )

    latest = db.query(ResumeHistory).filter(
        ResumeHistory.job_id == str(job_id)
    ).order_by(ResumeHistory.version.desc()).first()
    next_version = (latest.version + 1) if latest else 1

    history = ResumeHistory(
        job_id=job_id,
        version=next_version,
        resume_data=request.modified_resume,
        score=result.final_score
    )
    db.add(history)

    job.analysis_result = {
        **(job.analysis_result or {}),
        "final_score": result.final_score,
        "qualification_match_score": result.qualification_match_score,
        "skill_match_score": result.skill_match_score,
        "formatting_score": result.formatting_score,
        "keyword_match_score": result.keyword_match_score
    }

    db.commit()

    return result


@router.post("/track", response_model=JobResponse)
async def track_job(
    job_data: JobTrackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a simple tracked job without running the AI pipeline."""
    job = Job(
        user_id=current_user.id,
        job_posting={
            "job_title": job_data.job_title,
            "company_name": job_data.company_name,
            **({"job_link": job_data.job_url} if job_data.job_url else {}),
            **({"location": job_data.location} if job_data.location else {}),
        },
        status=job_data.status or "tracked",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/parse-resume")
async def parse_resume_for_job(
    job_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Parse a resume PDF for re-evaluation."""
    from engine.profile import parse_resume

    job = db.query(Job).filter(
        Job.id == str(job_id),
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    try:
        parsed_data = parse_resume(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    return {
        "success": True,
        "filename": file.filename,
        "parsed_resume": parsed_data
    }
