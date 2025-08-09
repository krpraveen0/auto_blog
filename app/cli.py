"""
Command line interface for planning, listing and generating Medium articles.

The CLI provides three subcommands:

``plan``
    Insert an article topic (and optional series information) into the database
    as a planned article.
``list``
    Display planned articles stored in the database.
``generate``
    Fetch a planned article by id, generate full Markdown content using the
    :class:`~medium_auto_article.perplexity_generator.PerplexityGenerator` and
    optionally publish it via
    :class:`~medium_auto_article.medium_publisher.MediumPublisher`.

Run ``python -m app.cli --help`` for full usage information.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .perplexity_generator import PerplexityGenerator
from .medium_publisher import MediumPublisher
from .db import (
    get_engine,
    init_db,
    plan_article,
    list_planned_articles,
    fetch_article,
    update_article,
)


def parse_frontmatter(md: str) -> dict:
    """Extract a minimal YAML frontmatter from a Markdown document.

    Supports simple ``key: value`` pairs separated by newlines. This helper
    returns a dictionary of keys and values if a fenced frontmatter block is
    found at the top of the file. It gracefully handles malformed input by
    returning an empty dict.
    """
    if not md.startswith("---"):
        return {}
    try:
        fence_end = md.index("\n---", 3)
        raw = md[3:fence_end].strip()
        meta = {}
        for line in raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
        return meta
    except ValueError:
        return {}


def cmd_plan(args: argparse.Namespace) -> None:
    engine = get_engine(args.db_url)
    init_db(engine)
    scheduled = (
        datetime.fromisoformat(args.schedule_date)
        if args.schedule_date
        else None
    )
    article_id = plan_article(
        engine,
        topic=args.topic,
        series_name=args.series,
        scheduled_at=scheduled,
    )
    print(f"[OK] Planned article {article_id} for topic '{args.topic}'")


def cmd_list(args: argparse.Namespace) -> None:
    engine = get_engine(args.db_url)
    init_db(engine)
    rows = list_planned_articles(engine)
    for row in rows:
        sched = row.get("scheduled_at")
        sched_str = sched.isoformat() if sched else "-"
        print(f"{row['id']}: {row['topic']} (scheduled {sched_str})")


def cmd_generate(args: argparse.Namespace) -> None:
    engine = get_engine(args.db_url)
    init_db(engine)
    plan = fetch_article(engine, args.id)
    if not plan:
        raise SystemExit(f"No article with id {args.id}")
    topic = plan["topic"]

    generator = PerplexityGenerator(api_key=args.pplx_key)
    article_md = generator.generate_article(
        topic=topic,
        audience_level=args.audience,
        tone=args.tone,
        model=args.model,
        include_code=not args.no_code,
        outline_depth=args.outline_depth,
        target_minutes=args.minutes,
        call_to_action=args.cta,
    )

    if args.save_md:
        outfile = Path(args.save_md)
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_text(article_md, encoding="utf-8")
        print(f"[OK] Saved generated article to {outfile}")

    update_article(
        engine,
        args.id,
        markdown=article_md,
        status=args.status,
    )
    print(f"[OK] Stored article {args.id} in database")

    if args.publish:
        meta = parse_frontmatter(article_md)
        title = meta.get("title") or f"{topic} — with Indian Mini Projects by Praveen"
        suggested_tags_raw = meta.get("suggested_tags")
        meta_tags = [t.strip() for t in suggested_tags_raw.split(",")] if suggested_tags_raw else []
        tags = (meta_tags or args.tags)[:5]

        publisher = MediumPublisher(token=args.medium_token)
        resp = publisher.publish_article(
            title=title,
            content_markdown=article_md,
            tags=tags,
            publish_status=args.status,
            canonical_url=args.canonical_url,
            notify_followers=(args.status == "public"),
        )
        print("[OK] Medium response:")
        print(json.dumps(resp, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan, list and generate Perplexity‑powered Medium articles with Indian "
            "mini projects and Praveen branding."
        )
    )
    parser.add_argument("--db-url", default=None, help="Database URL")
    sub = parser.add_subparsers(dest="command", required=True)

    plan_p = sub.add_parser("plan", help="Insert a planned article into the DB")
    plan_p.add_argument("--topic", required=True, help="Topic to write about")
    plan_p.add_argument("--series", help="Series name for grouping articles")
    plan_p.add_argument(
        "--schedule-date", help="ISO timestamp for scheduled publication"
    )
    plan_p.set_defaults(func=cmd_plan)

    list_p = sub.add_parser("list", help="List planned articles")
    list_p.set_defaults(func=cmd_list)

    gen_p = sub.add_parser("generate", help="Generate an article from a plan id")
    gen_p.add_argument("id", type=int, help="Planned article id")
    gen_p.add_argument(
        "--audience",
        default="beginner",
        choices=["beginner", "intermediate", "advanced"],
        help="Audience level for the article.",
    )
    gen_p.add_argument(
        "--tone",
        default="practical",
        choices=["friendly", "professional", "practical", "conversational"],
        help="Tone of the article.",
    )
    gen_p.add_argument(
        "--model",
        default="sonar",
        choices=["sonar", "sonar-reasoning", "sonar-pro", "sonar-deep-research"],
        help="Perplexity model to use.",
    )
    gen_p.add_argument(
        "--minutes",
        type=int,
        default=10,
        help="Target reading time in minutes.",
    )
    gen_p.add_argument(
        "--outline-depth",
        type=int,
        default=3,
        help="Outline depth (number of heading levels).",
    )
    gen_p.add_argument(
        "--no-code",
        action="store_true",
        help="Reduce code blocks if set (focus on instructions instead).",
    )
    gen_p.add_argument(
        "--cta",
        default="Follow Praveen for more real‑world build guides.",
        help="Call to action appended to the article.",
    )
    gen_p.add_argument(
        "--save-md",
        help="Path to save the generated Markdown (optional)",
    )
    gen_p.add_argument(
        "--publish",
        action="store_true",
        help="Publish the article to Medium after generation.",
    )
    gen_p.add_argument(
        "--tags",
        nargs="*",
        default=[],
        help="Medium tags (max 5 used).",
    )
    gen_p.add_argument(
        "--status",
        default="draft",
        choices=["draft", "public", "unlisted"],
        help="Publish status on Medium.",
    )
    gen_p.add_argument(
        "--canonical-url",
        default=None,
        help="Canonical URL if cross‑posting.",
    )
    gen_p.add_argument(
        "--pplx-key",
        default=None,
        help="Override Perplexity API key (otherwise load from .env).",
    )
    gen_p.add_argument(
        "--medium-token",
        default=None,
        help="Override Medium integration token (otherwise load from .env).",
    )
    gen_p.set_defaults(func=cmd_generate)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
