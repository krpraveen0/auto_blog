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
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import logging
import re
import yaml

from .perplexity_generator import PerplexityGenerator, PerplexityError
from .medium_publisher import MediumPublisher
from .diagram_utils import render_diagrams_to_images
from .db import (
    get_client,
    init_db,
    plan_article,
    list_planned_articles,
    fetch_article,
    update_article,
    fetch_next_planned_article,
)

logger = logging.getLogger(__name__)


def parse_frontmatter(md: str) -> dict:
    """Extract YAML frontmatter from a Markdown document.

    The frontmatter is expected to be enclosed in ``---`` fences at the top of
    the document. :func:`yaml.safe_load` is used to parse the contents and the
    resulting dictionary is returned. Any parsing errors or non‑mapping
    frontmatter result in an empty ``dict``.
    """

    if not md.startswith("---"):
        return {}

    try:
        fence_end = md.index("\n---", 3)
        raw = md[3:fence_end]
    except ValueError:
        return {}

    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}

    return data if isinstance(data, dict) else {}


# Map common technology keywords to canonical stack focus labels.
LANG_KEYWORDS = {
    "golang": "Go (Golang)",
    "go": "Go (Golang)",
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "aws": "AWS",
}


def infer_stack_focus_from_topic(topic: str) -> str:
    """Infer a comma-separated stack focus from a topic title.

    Scans the topic for known technology keywords and returns a
    comma-separated list suitable for the ``stack_focus`` parameter used by
    :func:`PerplexityGenerator.generate_article`.
    """
    topic_lower = topic.lower()
    matches: list[str] = []
    for key, label in LANG_KEYWORDS.items():
        if re.search(rf"\b{re.escape(key)}\b", topic_lower) and label not in matches:
            matches.append(label)
    return ", ".join(matches)


def cmd_plan(args: argparse.Namespace) -> None:
    client = get_client(args.db_key)
    init_db(client)
    scheduled = (
        datetime.fromisoformat(args.schedule_date)
        if args.schedule_date
        else None
    )
    article_id = plan_article(
        client,
        topic=args.topic,
        series_name=args.series,
        scheduled_at=scheduled,
    )
    print(f"[OK] Planned article {article_id} for topic '{args.topic}'")


def cmd_plan_series(args: argparse.Namespace) -> None:
    client = get_client(args.db_key)
    init_db(client)

    generator = PerplexityGenerator(api_key=args.pplx_key)
    plan = generator.generate_series_plan(
        topic=args.topic, posts=args.posts, model=args.model
    )
    start = (
        datetime.fromisoformat(args.schedule_date)
        if args.schedule_date
        else datetime.utcnow()
    )
    gap = timedelta(hours=args.gap_hours)
    for idx, item in enumerate(plan):
        scheduled = start + idx * gap
        article_id = plan_article(
            client,
            topic=item["title"],
            summary=item["summary"],
            series_name=args.topic,
            scheduled_at=scheduled,
        )
        print(
            f"[OK] Planned article {article_id} for topic '{item['title']}'"
        )


def cmd_list(args: argparse.Namespace) -> None:
    client = get_client(args.db_key)
    init_db(client)
    rows = list_planned_articles(client)
    for row in rows:
        sched = row.get("scheduled_at")
        sched_dt = None
        if isinstance(sched, str):
            try:
                sched_dt = datetime.fromisoformat(sched)
            except ValueError:
                sched_dt = None
        else:
            sched_dt = sched
        sched_str = sched_dt.isoformat() if sched_dt else (sched if isinstance(sched, str) else "-")
        print(f"{row['id']}: {row['topic']} (scheduled {sched_str})")


def _warn_missing_diagram_sections(md: str, sections: List[str], language: str) -> None:
    """Log warnings for sections missing diagram code blocks."""
    for section in sections:
        pattern = rf"^#+\s*{re.escape(section)}\s*$\n(?P<body>.*?)(?=^#+\s|\Z)"
        match = re.search(pattern, md, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if not match or f"```{language}" not in match.group("body"):
            logger.warning("Section '%s' is missing %s diagram", section, language)


def cmd_generate(args: argparse.Namespace) -> None:
    client = get_client(args.db_key)
    init_db(client)
    plan = fetch_article(client, args.id)
    if not plan:
        raise SystemExit(f"No article with id {args.id}")
    topic = plan["topic"]
    summary = plan.get("summary", "")

    generator = PerplexityGenerator(api_key=args.pplx_key)
    stack_focus = args.stack_focus or infer_stack_focus_from_topic(topic)
    article_md_raw = generator.generate_article(
        topic=topic,
        audience_level=args.audience,
        tone=args.tone,
        model=args.model,
        include_code=not args.no_code,
        outline_depth=args.outline_depth,
        target_minutes=args.minutes,
        call_to_action=args.cta,
        content_format=args.format,
        goal=args.goal or summary,
        stack_focus=stack_focus,
        timebox=args.timebox,
        diagram_language=args.diagram_language,
        diagram_sections=args.diagram_sections,
    )
    article_md = (
        generator.refine_article(article_md_raw, model=args.model)
        if args.refine
        else article_md_raw
    )

    if args.diagram_sections:
        _warn_missing_diagram_sections(article_md, args.diagram_sections, args.diagram_language)

    article_md, _ = render_diagrams_to_images(article_md, article_id=args.id)

    if args.save_md:
        outfile = Path(args.save_md)
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_text(article_md, encoding="utf-8")
        print(f"[OK] Saved generated article to {outfile}")

    db_status = "published" if args.publish else "generated"
    update_article(
        client,
        args.id,
        markdown=article_md,
        markdown_raw=article_md_raw,
        status=db_status,
    )
    print(f"[OK] Stored article {args.id} in database with status '{db_status}'")

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
        update_article(client, args.id, markdown=article_md, status=db_status)
        print("[OK] Medium response:")
        print(json.dumps(resp, indent=2))


def cmd_publish(args: argparse.Namespace) -> None:
    client = get_client(args.db_key)
    init_db(client)
    row = fetch_article(client, args.id)
    if not row:
        raise SystemExit(f"No article with id {args.id}")
    article_md = row.get("markdown")
    if not article_md:
        raise SystemExit(f"Article {args.id} has no markdown to publish")
    topic = row["topic"]

    article_md, _ = render_diagrams_to_images(article_md, article_id=args.id)

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
    update_article(client, args.id, markdown=article_md, status="published")
    print("[OK] Medium response:")
    print(json.dumps(resp, indent=2))


def cmd_auto(args: argparse.Namespace) -> None:
    client = get_client(args.db_key)
    init_db(client)

    plan = fetch_next_planned_article(client)
    if not plan:
        pending = list_planned_articles(client)
        if pending:
            print("[INFO] Next article is scheduled for later. Skipping generation.")
            return
        generator = PerplexityGenerator(api_key=args.pplx_key)
        topic = args.topic
        if not topic:
            try:
                topic = generator.suggest_trending_topics(count=1, model=args.model)[0]
                print(f"[INFO] Selected trending topic '{topic}'")
            except PerplexityError as exc:
                raise SystemExit(
                    "No planned articles available and failed to fetch a trending topic"
                ) from exc
        series_plan = generator.generate_series_plan(
            topic=topic, posts=args.posts, model=args.model
        )
        scheduled = (
            datetime.fromisoformat(args.schedule_date)
            if args.schedule_date
            else None
        )
        for item in series_plan:
            plan_article(
                client,
                topic=item["title"],
                summary=item["summary"],
                series_name=topic,
                scheduled_at=scheduled,
            )
        plan = fetch_next_planned_article(client)
        if not plan:
            raise SystemExit("Failed to plan a new article")

    args.id = plan["id"]
    cmd_generate(args)


def add_generate_args(p: argparse.ArgumentParser) -> None:
    """Add common generation/publishing arguments to a parser."""
    p.add_argument(
        "--audience",
        default="beginner",
        choices=["beginner", "intermediate", "advanced"],
        help="Audience level for the article.",
    )
    p.add_argument(
        "--tone",
        default="tutorial",
        choices=[
            "casual",
            "tutorial",
            "storytelling",
            "formal",
            "friendly",
            "professional",
            "practical",
            "conversational",
        ],
        help="Tone of the article.",
    )
    p.add_argument(
        "--model",
        default="sonar",
        choices=["sonar", "sonar-reasoning", "sonar-pro", "sonar-deep-research"],
        help="Perplexity model to use.",
    )
    p.add_argument(
        "--minutes",
        type=int,
        default=10,
        help="Target reading time in minutes.",
    )
    p.add_argument(
        "--outline-depth",
        type=int,
        default=3,
        help="Outline depth (number of heading levels).",
    )
    p.add_argument(
        "--no-code",
        action="store_true",
        help="Reduce code blocks if set (focus on instructions instead).",
    )
    p.add_argument(
        "--cta",
        default="Follow Praveen for more real‑world build guides.",
        help="Call to action appended to the article.",
    )
    p.add_argument(
        "--format",
        default="single article",
        choices=["single article", "series"],
        help="Generate a single article or a multi-part series.",
    )
    p.add_argument(
        "--goal",
        default="",
        help="Learning outcome or objective for the reader.",
    )
    p.add_argument(
        "--stack-focus",
        dest="stack_focus",
        default="",
        help="Comma separated technologies or domains to emphasise.",
    )
    p.add_argument(
        "--timebox",
        default="~15-minute read",
        help="Optional duration such as '30-day bootcamp'.",
    )
    p.add_argument(
        "--diagram-language",
        default="python",
        help="Language for diagram code blocks (e.g. 'python', 'mermaid').",
    )
    p.add_argument(
        "--diagram-section",
        action="append",
        dest="diagram_sections",
        default=[],
        help="Section name requiring its own diagram (repeatable).",
    )
    p.add_argument(
        "--refine",
        action="store_true",
        help="Proofread and tighten the article after initial generation.",
    )
    p.add_argument(
        "--save-md",
        help="Path to save the generated Markdown (optional)",
    )
    p.add_argument(
        "--publish",
        action="store_true",
        help="Publish the article to Medium after generation.",
    )
    p.add_argument(
        "--tags",
        nargs="*",
        default=[],
        help="Medium tags (max 5 used).",
    )
    p.add_argument(
        "--status",
        default="draft",
        choices=["draft", "public", "unlisted"],
        help="Publish status on Medium.",
    )
    p.add_argument(
        "--canonical-url",
        default=None,
        help="Canonical URL if cross‑posting.",
    )
    p.add_argument(
        "--pplx-key",
        default=None,
        help="Override Perplexity API key (otherwise load from .env).",
    )
    p.add_argument(
        "--medium-token",
        default=None,
        help="Override Medium integration token (otherwise load from .env).",
    )


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db-key", default=None, help="Supabase API key")

    parser = argparse.ArgumentParser(
        description=(
            "Plan, list and generate Perplexity‑powered Medium articles with Indian "
            "mini projects and Praveen branding."
        ),
        parents=[common],
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan_p = sub.add_parser(
        "plan", parents=[common], help="Insert a planned article into the DB"
    )
    plan_p.add_argument("--topic", required=True, help="Topic to write about")
    plan_p.add_argument("--series", help="Series name for grouping articles")
    plan_p.add_argument(
        "--schedule-date", help="ISO timestamp for scheduled publication"
    )
    plan_p.set_defaults(func=cmd_plan)

    series_p = sub.add_parser(
        "plan-series",
        parents=[common],
        help="Generate and plan a series of articles"
    )
    series_p.add_argument("--topic", required=True, help="Series theme")
    series_p.add_argument(
        "--posts", type=int, default=5, help="Number of entries to plan"
    )
    series_p.add_argument(
        "--schedule-date", help="ISO timestamp for scheduled publication"
    )
    series_p.add_argument(
        "--gap-hours",
        type=int,
        default=24,
        help="Hours between scheduled articles",
    )
    series_p.add_argument(
        "--model",
        default="sonar",
        choices=["sonar", "sonar-reasoning", "sonar-pro", "sonar-deep-research"],
        help="Perplexity model to use.",
    )
    series_p.add_argument(
        "--pplx-key",
        default=None,
        help="Override Perplexity API key (otherwise load from .env).",
    )
    series_p.set_defaults(func=cmd_plan_series)

    list_p = sub.add_parser("list", parents=[common], help="List planned articles")
    list_p.set_defaults(func=cmd_list)

    publish_p = sub.add_parser(
        "publish", parents=[common], help="Publish a generated article to Medium"
    )
    publish_p.add_argument("id", type=int, help="Article id to publish")
    publish_p.add_argument(
        "--tags",
        nargs="*",
        default=[],
        help="Medium tags (max 5 used).",
    )
    publish_p.add_argument(
        "--status",
        default="draft",
        choices=["draft", "public", "unlisted"],
        help="Publish status on Medium.",
    )
    publish_p.add_argument(
        "--canonical-url",
        default=None,
        help="Canonical URL if cross‑posting.",
    )
    publish_p.add_argument(
        "--medium-token",
        default=None,
        help="Override Medium integration token (otherwise load from .env).",
    )
    publish_p.set_defaults(func=cmd_publish)

    gen_p = sub.add_parser(
        "generate", parents=[common], help="Generate an article from a plan id"
    )
    gen_p.add_argument("id", type=int, help="Planned article id")
    add_generate_args(gen_p)
    gen_p.set_defaults(func=cmd_generate)

    auto_p = sub.add_parser(
        "auto",
        parents=[common],
        help="Plan a series if needed and generate the next article",
    )
    auto_p.add_argument(
        "--topic",
        help="Series topic used when planning a new set of articles",
    )
    auto_p.add_argument(
        "--posts",
        type=int,
        default=5,
        help="Number of posts to plan when creating a series",
    )
    auto_p.add_argument(
        "--schedule-date",
        help="ISO timestamp for scheduled publication",
    )
    add_generate_args(auto_p)
    auto_p.set_defaults(func=cmd_auto)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
