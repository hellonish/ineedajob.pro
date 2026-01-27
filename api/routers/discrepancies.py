"""
Discrepancy Router - CRD (no update)
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
from ..schemas import DiscrepancyCreate, DiscrepancyResponse
from ..models import User, Discrepancy

router = APIRouter(prefix="/api/discrepancies", tags=["Discrepancies"])


@router.post("", response_model=DiscrepancyResponse)
async def create_discrepancy(
    data: DiscrepancyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run discrepancy check."""
    from engine.discrepancy import DiscrepancyAnalyzer
    
    # Fetch full profile to get source data
    from ..models import UserProfile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please upload documents first.")

    analyzer = DiscrepancyAnalyzer()
    
    # Pass individual sources for comparison
    result = analyzer.analyze(
        resume=profile.resume_data,
        linkedin=profile.linkedin_data,
        portfolio=profile.portfolio_data
    )
    
    discrepancy = Discrepancy(
        user_id=current_user.id,
        unified_profile=data.unified_profile,
        result=result.model_dump() if hasattr(result, 'model_dump') else result
    )
    db.add(discrepancy)
    db.commit()
    db.refresh(discrepancy)
    
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
