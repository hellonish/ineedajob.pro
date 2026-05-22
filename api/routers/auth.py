"""
Authentication Router - Google OAuth + User Settings
"""

import os
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.config import Config

from ..database import get_db
from ..auth import oauth, create_access_token, get_or_create_user, get_current_user
from ..schemas import TokenResponse, UserResponse, UserUpdate, AvailableProvidersResponse, ProviderModelInfo
from ..models import User
from engine.models import LLMClient

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _clear_google_oauth_state(request: Request) -> None:
    """Remove stale Authlib state entries before starting a new OAuth flow."""
    for key in list(request.session.keys()):
        if key.startswith("_state_google_"):
            request.session.pop(key, None)


@router.get("/google")
async def google_login(request: Request):
    """Redirect to Google OAuth."""
    _clear_google_oauth_state(request)
    # Use explicit redirect URI to match Google Console config
    redirect_uri = "http://localhost:8000/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        # Get or create user
        user = get_or_create_user(
            db=db,
            email=user_info['email'],
            name=user_info.get('name', user_info['email']),
            picture=user_info.get('picture')
        )
        
        # Create JWT token
        access_token = create_access_token({"sub": str(user.id)})
        
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?{urlencode({'token': access_token})}"
        )
        
    except Exception as e:
        # Redirect to frontend with error
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?{urlencode({'error': str(e)})}"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user


@router.post("/logout")
async def logout():
    """Logout - client should discard token."""
    return {"message": "Logged out successfully"}


# User profile routes
@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get user profile."""
    return current_user


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    if update.name:
        current_user.name = update.name
    if update.profile_picture:
        current_user.profile_picture = update.profile_picture
    if update.llm_provider is not None:
        current_user.llm_provider = update.llm_provider
    if update.llm_model is not None:
        current_user.llm_model = update.llm_model
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/profile")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user account."""
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}


@router.get("/llm/providers", response_model=AvailableProvidersResponse)
async def get_llm_providers():
    """Get available LLM providers and models (no auth required)."""
    providers = LLMClient.available_providers()
    return AvailableProvidersResponse(
        providers={
            name: ProviderModelInfo(
                default_model=cfg["default_model"],
                models=cfg["models"],
            )
            for name, cfg in providers.items()
        }
    )
