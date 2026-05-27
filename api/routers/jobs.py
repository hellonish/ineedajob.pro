"""Jobs Router - CRUD, tracking, and analysis pipeline."""

import asyncio
import json
import logging
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, BackgroundTasks
from sqlalchemy import or_
from sqlalchemy.orm import Session

from engine.joblens.company_intel import CompanyIntelInput, CompanyIntelService
from engine.joblens.job_description import JobDescriptionBreakdownResult, break_down_job_description
from engine.joblens.job_match import JobMatchResult, match_profile_to_job
from engine.joblens.reachout import ReachoutInput, ReachoutService
from engine.profile.models import UnifiedProfile
from engine.profile.unification import create_unified_profile, merge_profile_sources

from ..database import SessionLocal, get_db
from ..auth import get_current_user
from ..llm import get_llm
from ..schemas import (
    JobCreate, JobTrackCreate, JobUpdate, JobResponse, JobListResponse, JobStatusEnum, JobLensSessionResponse,
)
from ..models import User, Job, JobLensSession, JobStatus, UserProfile, ProfileFile
from ..websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


def _collect_profile_sources(
    db: Session,
    profile: UserProfile,
    user_id: str,
) -> tuple[dict[str, Any], list[ProfileFile]]:
    """Collect parsed profile sources from profile files, with legacy fallback."""

    profile_files = (
        db.query(ProfileFile)
        .filter(ProfileFile.user_id == user_id, ProfileFile.parsed_data.isnot(None))
        .all()
    )
    sources: dict[str, Any] = {}
    type_counters: dict[str, int] = {}

    for profile_file in profile_files:
        file_type = profile_file.file_type
        type_counters[file_type] = type_counters.get(file_type, 0) + 1
        sources[f"{file_type}_{type_counters[file_type]}"] = profile_file.parsed_data

    if sources:
        return sources, profile_files

    for key in ("resume", "linkedin", "portfolio"):
        legacy_val = getattr(profile, f"{key}_data", None)
        if isinstance(legacy_val, str):
            try:
                legacy_val = json.loads(legacy_val)
            except (json.JSONDecodeError, TypeError):
                continue
        if isinstance(legacy_val, dict):
            sources[f"{key}_1"] = legacy_val

    return sources, profile_files


def _fallback_unified_profile(sources: dict[str, Any]) -> dict[str, Any]:
    if len(sources) == 1:
        return next(iter(sources.values()))

    type_sources = {}
    for key, value in sources.items():
        lower = key.lower()
        if "resume" in lower:
            type_sources["resume"] = value
        elif "linkedin" in lower:
            type_sources["linkedin"] = value
        elif "portfolio" in lower:
            type_sources["portfolio"] = value
    return create_unified_profile(type_sources) if type_sources else next(iter(sources.values()))


def _get_or_create_unified_profile(user_id: str) -> UnifiedProfile:
    """Load the user's unified profile or create/cache it from parsed profile files."""

    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)

        if profile.unified_profile:
            return UnifiedProfile.model_validate(profile.unified_profile)

        sources, profile_files = _collect_profile_sources(db, profile, user_id)
        if not sources:
            raise ValueError("No parsed profile files found. Upload profile files before creating a job.")

        try:
            per_file_ctx = {
                profile_file.filename: profile_file.additional_context
                for profile_file in profile_files
                if profile_file.additional_context
            }
            unified, _ = merge_profile_sources(
                sources,
                get_llm("profile"),
                global_context=profile.additional_context,
                per_file_context=per_file_ctx,
            )
        except Exception as error:
            logger.warning("LLM profile unification failed for user %s: %s", user_id, error)
            unified = _fallback_unified_profile(sources)

        profile.unified_profile = unified
        profile.extracted_profile = unified
        db.commit()
        return UnifiedProfile.model_validate(unified)
    finally:
        db.close()


def _gather_company_intel(job_description: JobDescriptionBreakdownResult, company_website: Optional[str]):
    """Company intel section: derive lookup handles and collect company intelligence."""

    return CompanyIntelService(llm=get_llm("company_intel")).collect(
        CompanyIntelInput(
            company_name=job_description.breakdown.metadata.company_name,
            website=company_website,
        )
    )


def _calculate_match(profile: Optional[UnifiedProfile], job_description: JobDescriptionBreakdownResult):
    """Match section: compare unified profile against the processed job."""

    if not profile:
        raise ValueError("No unified profile available.")

    return match_profile_to_job(
        profile=profile,
        job_description=job_description,
        llm=get_llm("job_match"),
    )


def _discover_reachout(
    profile: UnifiedProfile,
    job_description: JobDescriptionBreakdownResult,
    company_website: Optional[str],
):
    """Reachout section: derive roles/schools and discover candidate contacts."""

    breakdown = job_description.breakdown
    roles = [
        breakdown.metadata.job_title,
        breakdown.role_classification.role_family,
        breakdown.role_classification.primary_track,
    ]
    roles.extend(skill.name for skill in breakdown.primary_skills[:3])
    target_roles = [role for role in roles if role]
    schools = [item.institution for item in profile.education if item.institution]

    return ReachoutService(llm=get_llm("reachout")).discover(
        ReachoutInput(
            company_name=breakdown.metadata.company_name,
            company_website=company_website,
            target_roles=target_roles,
            location=breakdown.metadata.location,
            schools=schools,
        )
    )


def _job_posting_summary(job_description: JobDescriptionBreakdownResult) -> dict:
    """Build the durable Job.job_posting from the parsed job description."""

    breakdown = job_description.breakdown
    metadata = breakdown.metadata
    return {
        "job_title": metadata.job_title or "Untitled role",
        "company_name": metadata.company_name or "Unknown company",
        "location": metadata.location,
        "work_mode": metadata.work_mode.value,
        "employment_type": metadata.employment_type.value,
        "seniority_level": metadata.seniority_level.value,
        "years_of_experience_min": metadata.years_of_experience_min,
        "years_of_experience_max": metadata.years_of_experience_max,
        "role_family": breakdown.role_classification.role_family,
        "primary_track": breakdown.role_classification.primary_track,
        "primary_skills": [skill.name for skill in breakdown.primary_skills],
        "secondary_skills": [skill.name for skill in breakdown.secondary_skills],
        "responsibilities": [
            " ".join(part for part in (item.action, item.object, item.context) if part)
            for item in breakdown.responsibilities
        ],
        "constraints": [item.text for item in breakdown.constraints],
        "keywords": breakdown.keywords,
    }


def _analysis_summary(match: JobMatchResult) -> dict:
    """Build the durable Job.analysis_result from match output."""

    return {
        "final_score": match.summary.total_score,
        "match_band": match.summary.match_band.value,
        "headline": match.summary.headline,
        "strongest_matches": match.summary.strongest_matches,
        "biggest_gaps": match.summary.biggest_gaps,
    }


def _emit(user_id: str, session_id: str, job_id: Optional[str], step: str, event: str, data: Optional[dict] = None) -> None:
    asyncio.create_task(
        manager.send_to_user(
            user_id,
            {
                "type": event,
                "session_id": session_id,
                "job_id": job_id,
                "step": step,
                **(data or {}),
            },
        )
    )


def _db_write(fn) -> None:
    db = SessionLocal()
    try:
        fn(db)
        db.commit()
    finally:
        db.close()


async def run_job_analysis_background(
    job_id: str,
    session_id: str,
    user_id: str,
    jd_text: str,
    company_website: Optional[str],
) -> None:
    """Run the job analysis flow from profile + parsed job description."""

    profile_snapshot = None
    job_description = None
    company_intel = None
    match_analysis = None
    reachout = None

    try:
        _emit(user_id, session_id, job_id, "profile", "joblens_step_started")
        _emit(user_id, session_id, job_id, "job_description", "joblens_step_started")

        async def run_profile() -> None:
            nonlocal profile_snapshot
            try:
                profile_snapshot = await asyncio.to_thread(lambda: _get_or_create_unified_profile(user_id))
                _emit(
                    user_id,
                    session_id,
                    job_id,
                    "profile",
                    "joblens_step_complete",
                    {"data": profile_snapshot.model_dump(mode="json")},
                )
            except Exception as error:
                _emit(user_id, session_id, job_id, "profile", "joblens_step_failed", {"error": str(error)})

        async def run_job_description() -> None:
            nonlocal job_description
            try:
                job_description = await asyncio.to_thread(
                    lambda: break_down_job_description(
                        job_text=jd_text,
                        llm=get_llm("job_description"),
                        source_id=job_id,
                    )
                )
                _emit(
                    user_id,
                    session_id,
                    job_id,
                    "job_description",
                    "joblens_step_complete",
                    {"data": job_description.model_dump(mode="json")},
                )
            except Exception as error:
                _emit(user_id, session_id, job_id, "job_description", "joblens_step_failed", {"error": str(error)})

        await asyncio.gather(run_profile(), run_job_description())

        def save_first_wave(db: Session) -> None:
            session = db.query(JobLensSession).filter(JobLensSession.id == session_id).first()
            job = db.query(Job).filter(Job.id == job_id).first()
            if not session:
                return
            if profile_snapshot:
                session.profile_snapshot = profile_snapshot.model_dump(mode="json")
                session.current_step = max(session.current_step, 1)
            if job_description:
                session.job_description = job_description.model_dump(mode="json")
                session.raw_jd_text = jd_text
                session.current_step = max(session.current_step, 2)
                if job:
                    job.job_posting = _job_posting_summary(job_description)

        _db_write(save_first_wave)

        if not job_description:
            logger.error("Job analysis aborted: job description failed for job %s", job_id)
            def mark_job_tracked(db: Session) -> None:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job and job.status == JobStatus.ANALYZING:
                    job.status = JobStatus.TRACKED

            _db_write(mark_job_tracked)
            return

        async def run_parallel_section(step: str, fn):
            _emit(user_id, session_id, job_id, step, "joblens_step_started")
            try:
                result = await asyncio.to_thread(fn)
                _emit(
                    user_id,
                    session_id,
                    job_id,
                    step,
                    "joblens_step_complete",
                    {"data": result.model_dump(mode="json")},
                )
                return result
            except Exception as error:
                _emit(user_id, session_id, job_id, step, "joblens_step_failed", {"error": str(error)})
                return None

        # Three independent post-processing sections. One /api/jobs hit triggers this fan-out.
        company_intel, match_analysis, reachout = await asyncio.gather(
            run_parallel_section(
                "company_intel",
                lambda: _gather_company_intel(job_description, company_website),
            ),
            run_parallel_section(
                "match_analysis",
                lambda: _calculate_match(profile_snapshot, job_description),
            ),
            run_parallel_section(
                "reachout",
                lambda: _discover_reachout(profile_snapshot or UnifiedProfile(), job_description, company_website),
            ),
        )

        def save_second_wave(db: Session) -> None:
            session = db.query(JobLensSession).filter(JobLensSession.id == session_id).first()
            job = db.query(Job).filter(Job.id == job_id).first()
            if not session:
                return
            if company_intel:
                session.company_intel = company_intel.model_dump(mode="json")
                session.current_step = max(session.current_step, 3)
            if match_analysis:
                session.match_analysis = match_analysis.model_dump(mode="json")
                session.current_step = max(session.current_step, 4)
                if job:
                    job.analysis_result = _analysis_summary(match_analysis)
            if reachout:
                session.reachout = reachout.model_dump(mode="json")
                session.current_step = max(session.current_step, 5)
            if job and job.status == JobStatus.ANALYZING:
                job.status = JobStatus.TRACKED

        _db_write(save_second_wave)
        _emit(user_id, session_id, job_id, "pipeline", "joblens_pipeline_complete")

    except Exception as error:
        logger.exception("Job analysis pipeline error for job %s: %s", job_id, error)
        def mark_job_tracked(db: Session) -> None:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job and job.status == JobStatus.ANALYZING:
                job.status = JobStatus.TRACKED

        _db_write(mark_job_tracked)
        _emit(user_id, session_id, job_id, "pipeline", "joblens_pipeline_failed", {"error": str(error)})


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
    """Create a new job and kick off the analysis pipeline."""
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

    # Create internal analysis session
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
        run_job_analysis_background,
        job.id, session.id, current_user.id,
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


@router.get("/{job_id}/analysis", response_model=JobLensSessionResponse)
async def get_job_analysis(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the internal analysis session linked to a job."""

    session = db.query(JobLensSession).filter(
        JobLensSession.job_id == str(job_id),
        JobLensSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Job analysis not found")

    return session


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
