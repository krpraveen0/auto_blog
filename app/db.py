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
from postgrest.exceptions import APIError

SUPABASE_URL_ENV = "SUPABASE_URL"
SUPABASE_KEY_ENV = "SUPABASE_KEY"


def get_client(db_key: Optional[str] = None) -> Client:
    """Return a Supabase client using env vars or provided strings."""
    load_dotenv()
    url = os.getenv(SUPABASE_URL_ENV)
    key = db_key or os.getenv(SUPABASE_KEY_ENV)
    if not url or not key:
        raise ValueError(
            "Supabase URL and key must be provided via environment or arguments"
        )
    return create_client(url, key)


def init_db(client: Client) -> None:
    """Ensure required tables exist before executing queries.

    Supabase projects manage schema separately from the application code. When a
    table is missing, the REST API raises an :class:`postgrest.exceptions.APIError`
    with code ``42P01`` (undefined_table).  Rather than bubbling up a cryptic
    stack trace, detect this situation and raise a more helpful error message so
    callers know that database migrations need to run.
    """

    try:
        # A lightweight existence check; we only care that the query succeeds.
        client.table("articles").select("id").limit(1).execute()
    except APIError as exc:
        if getattr(exc, "code", None) == "42P01":
            raise RuntimeError(
                "Supabase schema is not initialised; run migrations to create the 'articles' table"
            ) from exc
        raise

    return None


def get_or_create_series(client: Client, topic: str) -> int:
    """Return the id for a series with the given topic, creating it if needed."""
    existing = client.table("series").select("id").eq("topic", topic).execute()
    if existing.data:
        return existing.data[0]["id"]
    # Supabase's Python client changed behaviour between versions: older
    # releases allowed ``.select("id")`` after an ``insert`` to limit the
    # returned columns, while newer versions return the inserted row directly
    # and expose no ``select`` method on the builder.  Attempt to use the more
    # efficient ``select`` when available but fall back to a plain insert for
    # compatibility with newer clients.
    insert_builder = client.table("series").insert({"topic": topic})
    if hasattr(insert_builder, "select"):  # Supabase <1.0
        insert_builder = insert_builder.select("id")
    inserted = insert_builder.execute()
    return inserted.data[0]["id"]


def plan_article(
    client: Client,
    *,
    topic: str,
    summary: Optional[str] = None,
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
        summary=summary,
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
    markdown_raw: Optional[str] = None,
    summary: Optional[str] = None,
    series_id: Optional[int] = None,
    scheduled_at: Optional[datetime] = None,
) -> None:
    """Update fields on an existing article."""
    values = {
        k: (v.isoformat() if isinstance(v, datetime) else v)
        for k, v in {
            "topic": topic,
            "status": status,
            "markdown": markdown,
            "markdown_raw": markdown_raw,
            "summary": summary,
            "series_id": series_id,
            "scheduled_at": scheduled_at,
        }.items()
        if v is not None
    }
    if not values:
        return
    try:
        client.table("articles").update(values).eq("id", article_id).execute()
    except APIError as exc:
        if getattr(exc, "code", None) == "PGRST204" and "summary" in values:
            values.pop("summary")
            if values:
                client.table("articles").update(values).eq("id", article_id).execute()
        else:
            raise


def save_article(
    client: Client,
    *,
    topic: str,
    status: str,
    markdown: str,
    markdown_raw: Optional[str] = None,
    summary: Optional[str] = None,
    series_id: Optional[int] = None,
    scheduled_at: Optional[datetime] = None,
) -> int:
    """Insert an article and return its new id."""
    payload = {
        "topic": topic,
        "status": status,
        "markdown": markdown,
        "markdown_raw": markdown_raw,
        "summary": summary,
        "series_id": series_id,
        "scheduled_at": scheduled_at.isoformat() if scheduled_at else None,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    insert_builder = client.table("articles").insert(payload)

    # Older versions of the Supabase client exposed ``select`` on the insert
    # builder to limit returned columns.  Newer releases removed this helper and
    # instead return the inserted row directly.  Attempt to use ``select`` when
    # available but gracefully fall back when it's missing.
    if hasattr(insert_builder, "select"):  # Supabase <1.0
        insert_builder = insert_builder.select("id")

    try:
        inserted = insert_builder.execute()
    except APIError as exc:
        # Some deployments may not have run migrations adding the ``summary``
        # column yet.  ``postgrest`` reports this with code ``PGRST204``.  For
        # compatibility with older schemas, retry the insert without the summary
        # field when we hit this specific error.
        if getattr(exc, "code", None) == "PGRST204" and "summary" in payload:
            payload.pop("summary")
            inserted = client.table("articles").insert(payload).execute()
        else:
            raise

    return inserted.data[0]["id"]


def fetch_article(client: Client, article_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single article by id."""
    result = client.table("articles").select("*").eq("id", article_id).execute()
    data = result.data
    return data[0] if data else None


def list_articles(client: Client) -> List[Dict[str, Any]]:
    """Return all articles ordered by id."""
    result = client.table("articles").select("*").order("id", desc=False).execute()
    return result.data or []


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


def fetch_next_planned_article(client: Client) -> Optional[Dict[str, Any]]:
    """Return the next planned article or ``None``.

    This helper mirrors :func:`list_planned_articles` but only returns a single
    row.  It keeps the selection logic in one place so callers that want the
    "next" article don't have to re‑implement the Supabase query each time.
    """
    now = datetime.utcnow().isoformat()
    rows = (
        client.table("articles")
        .select("*")
        .eq("status", "planned")
        .lte("scheduled_at", now)
        .order("scheduled_at", desc=False)
        .limit(1)
        .execute()
    ).data
    return rows[0] if rows else None


__all__ = [
    "get_client",
    "init_db",
    "get_or_create_series",
    "plan_article",
    "save_article",
    "fetch_article",
    "list_articles",
    "update_article",
    "list_planned_articles",
    "fetch_next_planned_article",
]
