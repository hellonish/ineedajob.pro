"""
Auth Router — user profile endpoints (no OAuth in local mode).
"""

import logging
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session

_log = logging.getLogger(__name__)

from ..database import get_db
from ..auth import get_current_user
from ..schemas import UserResponse, UserUpdate
from ..models import User, ProfileFile
from ..limiter import limiter
from .. import storage

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _build_user_response(user: User, db: Session) -> UserResponse:
    has_profile = (
        db.query(ProfileFile).filter(ProfileFile.user_id == user.id).first() is not None
        or (user.profile is not None and user.profile.unified_profile is not None)
    )
    response = UserResponse.model_validate(user)
    response.has_profile = has_profile
    response.onboarding_completed = True  # no onboarding in local mode
    return response


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _build_user_response(current_user, db)


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _build_user_response(current_user, db)


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if update.name:
        current_user.name = update.name
    if update.profile_picture:
        current_user.profile_picture = update.profile_picture
    db.commit()
    db.refresh(current_user)
    return _build_user_response(current_user, db)


@router.post("/avatar", response_model=UserResponse)
@limiter.limit("10/minute", override_defaults=False)
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, or GIF images are allowed.")
    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="Image must be under 5 MB.")
    if current_user.profile_picture and "/object/public/avatars/" in current_user.profile_picture:
        storage.delete_avatar(current_user.profile_picture)
    ext = os.path.splitext(file.filename or "avatar")[1] or ".jpg"
    storage_path = f"{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    public_url = storage.upload_avatar(storage_path, contents, file.content_type or "image/jpeg")
    current_user.profile_picture = public_url
    db.commit()
    db.refresh(current_user)
    return _build_user_response(current_user, db)


@router.delete("/avatar", response_model=UserResponse)
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.profile_picture and "/object/public/avatars/" in current_user.profile_picture:
        storage.delete_avatar(current_user.profile_picture)
    current_user.profile_picture = None
    db.commit()
    db.refresh(current_user)
    return _build_user_response(current_user, db)
