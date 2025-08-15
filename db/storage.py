from __future__ import annotations

"""Helper functions for interacting with Supabase storage."""

from app.db import get_client

try:  # pragma: no cover - supabase not installed in tests
    from supabase.client import Client  # type: ignore
except Exception:  # pragma: no cover - supabase not installed in tests
    Client = object  # type: ignore

BUCKET_NAME = "auto_blog"


def upload_image(image_bytes: bytes, file_name: str) -> str:
    """Upload image bytes to Supabase storage and return a public URL.

    Parameters
    ----------
    image_bytes:
        Raw image data to upload.
    file_name:
        Destination path within the storage bucket.
    """
    client: Client = get_client()
    bucket = client.storage.from_(BUCKET_NAME)
    bucket.upload(file_name, image_bytes)
    return bucket.get_public_url(file_name)
