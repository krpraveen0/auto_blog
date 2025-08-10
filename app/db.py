from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    def load_dotenv(*args: Any, **kwargs: Any) -> None:
        return None  # type: ignore

from supabase import create_client, Client

SUPABASE_URL_ENV = "SUPABASE_URL"
SUPABASE_KEY_ENV = "SUPABASE_KEY"


def get_client(db_url: Optional[str] = None, db_key: Optional[str] = None) -> Client:
    """Return a Supabase client using env vars or provided strings."""
    load_dotenv()
    url = db_url or os.getenv(SUPABASE_URL_ENV)
    key = db_key or os.getenv(SUPABASE_KEY_ENV)
    if not url or not key:
        raise ValueError(
            "Supabase URL and key must be provided via arguments or environment"
        )
    return create_client(url, key)


def init_db(client: Client) -> None:
    """Supabase manages schema separately; nothing to initialize."""
    return None


def get_or_create_series(client: Client, topic: str) -> int:
    """Return the id for a series with the given topic, creating it if needed."""
    existing = client.table("series").select("id").eq("topic", topic).execute()
    if existing.data:
        return existing.data[0]["id"]
    inserted = (
        client.table("series").insert({"topic": topic}).select("id").execute()
    )
    return inserted.data[0]["id"]


def plan_article(
    client: Client,
    *,
    topic: str,
    series_name: Optional[str] = None,
    scheduled_at: Optional[datetime] = None,
) -> int:
    """Insert a planned article and return its id."""
    series_id = None
    if series_name:
        series_id = get_or_create_series(client, series_name)
    return save_article(
        client,
        topic=topic,
        status="planned",
        markdown="",
        series_id=series_id,
        scheduled_at=scheduled_at,
    )


def update_article(
    client: Client,
    article_id: int,
    *,
    topic: Optional[str] = None,
    status: Optional[str] = None,
    markdown: Optional[str] = None,
    series_id: Optional[int] = None,
    scheduled_at: Optional[datetime] = None,
) -> None:
    """Update fields on an existing article."""
    values = {
        k: v
        for k, v in {
            "topic": topic,
            "status": status,
            "markdown": markdown,
            "series_id": series_id,
            "scheduled_at": scheduled_at,
        }.items()
        if v is not None
    }
    if not values:
        return
    client.table("articles").update(values).eq("id", article_id).execute()


def save_article(
    client: Client,
    *,
    topic: str,
    status: str,
    markdown: str,
    series_id: Optional[int] = None,
    scheduled_at: Optional[datetime] = None,
) -> int:
    """Insert an article and return its new id."""
    payload = {
        "topic": topic,
        "status": status,
        "markdown": markdown,
        "series_id": series_id,
        "scheduled_at": scheduled_at,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    inserted = client.table("articles").insert(payload).select("id").execute()
    return inserted.data[0]["id"]


def fetch_article(client: Client, article_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single article by id."""
    result = client.table("articles").select("*").eq("id", article_id).execute()
    data = result.data
    return data[0] if data else None


def list_planned_articles(client: Client) -> List[Dict[str, Any]]:
    """Return articles with status 'planned', ordered by scheduled_at."""
    result = (
        client.table("articles")
        .select("*")
        .eq("status", "planned")
        .order("scheduled_at", desc=False)
        .execute()
    )
    return result.data or []


__all__ = [
    "get_client",
    "init_db",
    "get_or_create_series",
    "plan_article",
    "save_article",
    "fetch_article",
    "update_article",
    "list_planned_articles",
]
