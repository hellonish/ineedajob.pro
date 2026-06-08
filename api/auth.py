"""
Auth — single local dev user (no login required).

All endpoints that previously required a JWT now use get_current_user, which
always returns the same local user, creating it on first run.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

_DEV_USER_EMAIL = "dev@local"
_DEV_USER_NAME = "Local User"


async def get_current_user(db: Session = Depends(get_db)) -> User:
    """Return the single local dev user, creating it on first run."""
    user = db.query(User).filter(User.email == _DEV_USER_EMAIL).first()
    if not user:
        user = User(email=_DEV_USER_EMAIL, name=_DEV_USER_NAME)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
