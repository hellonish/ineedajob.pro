"""
Supabase Storage — uses storage3 directly to avoid httpx version conflicts.

Buckets expected in your Supabase project:
  - avatars      (public)   — profile pictures
  - wand-uploads (private)  — resume / linkedin / portfolio files
"""

import os
from functools import lru_cache
from storage3 import create_client as create_storage_client
from storage3.utils import StorageException

AVATAR_BUCKET = "avatars"
FILES_BUCKET = "wand-uploads"


@lru_cache(maxsize=1)
def _storage():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    headers = {
        "apiKey": key,
        "Authorization": f"Bearer {key}",
    }
    return create_storage_client(f"{url}/storage/v1", headers, is_async=False)


# ── Avatars (public bucket) ──────────────────────────────────────────────────

def upload_avatar(storage_path: str, data: bytes, content_type: str = "image/jpeg") -> str:
    """Upload avatar bytes, return the public URL."""
    _storage().from_(AVATAR_BUCKET).upload(
        storage_path, data, {"content-type": content_type, "upsert": "true"}
    )
    return _storage().from_(AVATAR_BUCKET).get_public_url(storage_path)


def delete_avatar(public_url: str) -> None:
    """Delete avatar given its public URL."""
    marker = f"/object/public/{AVATAR_BUCKET}/"
    if marker not in public_url:
        return
    storage_path = public_url.split(marker, 1)[1]
    try:
        _storage().from_(AVATAR_BUCKET).remove([storage_path])
    except StorageException:
        pass


# ── Profile files (private bucket) ──────────────────────────────────────────

def upload_file(storage_path: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Upload file bytes, return the storage path."""
    _storage().from_(FILES_BUCKET).upload(
        storage_path, data, {"content-type": content_type, "upsert": "true"}
    )
    return storage_path


def get_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    """Return a signed download URL valid for *expires_in* seconds."""
    result = _storage().from_(FILES_BUCKET).create_signed_url(storage_path, expires_in)
    return result["signedURL"]


def delete_file(storage_path: str) -> None:
    """Delete a private file by its storage path."""
    if not storage_path:
        return
    try:
        _storage().from_(FILES_BUCKET).remove([storage_path])
    except StorageException:
        pass
