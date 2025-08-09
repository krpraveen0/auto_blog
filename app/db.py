from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    select,
    insert,
    func,
)
from sqlalchemy.engine import Engine

DATABASE_URL_ENV = "DATABASE_URL"

metadata = MetaData()

series = Table(
    "series",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("topic", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)

articles = Table(
    "articles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("topic", String, nullable=False),
    Column("status", String, nullable=False),
    Column("markdown", Text),
    Column("series_id", Integer, ForeignKey("series.id")),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("scheduled_at", DateTime),
)

def get_engine(db_url: Optional[str] = None, *, echo: bool = False) -> Engine:
    """Return a SQLAlchemy engine using DATABASE_URL env var or provided string."""
    url = db_url or os.getenv(DATABASE_URL_ENV)
    if not url:
        raise ValueError("A database URL must be provided via argument or DATABASE_URL")
    return create_engine(url, echo=echo, future=True)


def init_db(engine: Engine) -> None:
    """Create tables if they do not exist."""
    metadata.create_all(engine)


def save_article(
    engine: Engine,
    *,
    topic: str,
    status: str,
    markdown: str,
    series_id: Optional[int] = None,
    scheduled_at: Optional[datetime] = None,
) -> int:
    """Insert an article and return its new id."""
    with engine.begin() as conn:
        result = conn.execute(
            insert(articles)
            .values(
                topic=topic,
                status=status,
                markdown=markdown,
                series_id=series_id,
                scheduled_at=scheduled_at,
            )
            .returning(articles.c.id)
        )
        return result.scalar_one()


def fetch_article(engine: Engine, article_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single article by id."""
    with engine.connect() as conn:
        result = conn.execute(select(articles).where(articles.c.id == article_id))
        row = result.mappings().first()
        return dict(row) if row else None


def list_planned_articles(engine: Engine) -> List[Dict[str, Any]]:
    """Return articles with status 'planned', ordered by scheduled_at."""
    with engine.connect() as conn:
        result = conn.execute(
            select(articles)
            .where(articles.c.status == "planned")
            .order_by(articles.c.scheduled_at.asc())
        )
        return [dict(row) for row in result.mappings().all()]


__all__ = [
    "get_engine",
    "init_db",
    "save_article",
    "fetch_article",
    "list_planned_articles",
    "metadata",
    "series",
    "articles",
]
