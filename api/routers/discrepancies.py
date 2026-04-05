"""
Discrepancy Router - CRD (no update)
"""

import sys
import os
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ..database import get_db
from ..auth import get_current_user
from ..schemas import DiscrepancyCreate, DiscrepancyResponse
from ..models import User, Discrepancy
from engine.models.llm import LLMClient

router = APIRouter(prefix="/api/discrepancies", tags=["Discrepancies"])


async def _run_discrepancy_background(
    discrepancy_id: str,
    user_id: str,
    llm_provider: str,
    llm_model: str,
):
    """Run discrepancy analysis in the background and save result."""
    from ..database import SessionLocal
    from ..models import UserProfile
    from ..websocket import manager
    from engine.discrepancy import DiscrepancyAnalyzer

    import asyncio

    # ── Phase 1: read needed data, then release the DB connection ──
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        has_discrepancy = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).count() > 0
        if not profile or not has_discrepancy:
            return
        # Snapshot the data we need; close session so no lock is held during LLM call
        resume_data = profile.resume_data
        linkedin_data = profile.linkedin_data
        portfolio_data = profile.portfolio_data
    finally:
        db.close()

    # ── Phase 2: long LLM work — no DB session open ──
    try:
        analyzer = DiscrepancyAnalyzer(
            LLMClient.from_user_settings({
                "llm_provider": llm_provider or "grok",
                "llm_model": llm_model,
            })
        )
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: analyzer.analyze(
                resume=resume_data,
                linkedin=linkedin_data,
                portfolio=portfolio_data,
            )
        )
        result_data = result.model_dump() if hasattr(result, 'model_dump') else result
    except Exception as e:
        await manager.send_to_user(user_id, {
            "type": "discrepancy_failed",
            "discrepancy_id": discrepancy_id,
            "error": str(e),
        })
        return

    # ── Phase 3: write result — fresh DB session ──
    db = SessionLocal()
    try:
        discrepancy = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).first()
        if discrepancy:
            discrepancy.result = result_data
            db.commit()
    finally:
        db.close()

    await manager.send_to_user(user_id, {
        "type": "discrepancy_complete",
        "discrepancy_id": discrepancy_id,
        "result": result_data,
    })


@router.post("", response_model=DiscrepancyResponse)
async def create_discrepancy(
    data: DiscrepancyCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a pending discrepancy record and kick off analysis in the background."""
    from ..models import UserProfile

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please upload documents first.")

    discrepancy = Discrepancy(
        user_id=current_user.id,
        unified_profile=data.unified_profile,
        result=None,
    )
    db.add(discrepancy)
    db.commit()
    db.refresh(discrepancy)

    background_tasks.add_task(
        _run_discrepancy_background,
        discrepancy_id=discrepancy.id,
        user_id=current_user.id,
        llm_provider=current_user.llm_provider or "grok",
        llm_model=current_user.llm_model,
    )

    return discrepancy


@router.get("", response_model=List[DiscrepancyResponse])
async def list_discrepancies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List discrepancy reports."""
    reports = db.query(Discrepancy).filter(
        Discrepancy.user_id == current_user.id
    ).order_by(Discrepancy.created_at.desc()).all()
    
    return reports


@router.get("/{discrepancy_id}", response_model=DiscrepancyResponse)
async def get_discrepancy(
    discrepancy_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get discrepancy report."""
    report = db.query(Discrepancy).filter(
        Discrepancy.id == str(discrepancy_id),
        Discrepancy.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Discrepancy not found")
    
    return report


@router.delete("/{discrepancy_id}")
async def delete_discrepancy(
    discrepancy_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete discrepancy report."""
    report = db.query(Discrepancy).filter(
        Discrepancy.id == str(discrepancy_id),
        Discrepancy.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Discrepancy not found")
    
    db.delete(report)
    db.commit()
    return {"message": "Discrepancy deleted"}
