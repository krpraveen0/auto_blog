from __future__ import annotations

import uuid
from app.db import get_client

try:
    from supabase.client import Client  # type: ignore
except Exception:  # pragma: no cover - supabase not installed in tests
    Client = object  # type: ignore


BUCKET_NAME = "article-images"


def save_article_image(article_id: int, diagram_type: str, image_bytes: bytes) -> str:
    """Upload an article diagram image to Supabase storage and record metadata.

    Parameters
    ----------
    article_id:
        Identifier of the article the diagram belongs to.
    diagram_type:
        Name or type of diagram being stored.
    image_bytes:
        Binary image data to store.

    Returns
    -------
    str
        Public URL of the uploaded image.
    """
    client: Client = get_client()
    file_name = f"{article_id}_{uuid.uuid4().hex}.png"
    storage_path = f"{article_id}/{file_name}"
    bucket = client.storage.from_(BUCKET_NAME)
    bucket.upload(storage_path, image_bytes)
    public_url = bucket.get_public_url(storage_path)
    client.table("article_images").insert(
        {
            "article_id": article_id,
            "diagram_type": diagram_type,
            "image_url": public_url,
        }
    ).execute()
    return public_url
