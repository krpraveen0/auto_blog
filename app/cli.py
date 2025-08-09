"""
Command line interface for generating and optionally publishing Medium articles.

This CLI exposes a single entry point that accepts a topic, audience level,
tone, model and other options. It uses the :class:`~medium_auto_article.perplexity_generator.PerplexityGenerator`
to create a full Markdown article via Perplexity's API and saves it to a file.
Optionally, you can request that the article be published immediately via
Medium using :class:`~medium_auto_article.medium_publisher.MediumPublisher`.

Usage example::

    python -m medium_auto_article.cli \
        --topic "Building a UPI‑like payment flow demo with Java + Spring" \
        --audience beginner --tone practical --model sonar \
        --minutes 12 --publish --status draft --tags payments upi spring java india

To see all options, run with ``--help``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional

from .perplexity_generator import PerplexityGenerator
from .medium_publisher import MediumPublisher


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


def main(argv: Optional[List[str]] = None) -> None:
    """
    Entry point for the command line interface.

    Parses command line arguments, invokes the article generator, saves the
    generated Markdown, and optionally publishes it via Medium. All outputs
    are printed to stdout, including Medium responses when publishing.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Generate a Perplexity‑powered Medium article with Indian mini projects "
            "and Praveen branding, optionally publishing it via Medium."
        )
    )
    parser.add_argument("--topic", required=True, help="Topic to write about.")
    parser.add_argument(
        "--audience",
        default="beginner",
        choices=["beginner", "intermediate", "advanced"],
        help="Audience level for the article.",
    )
    parser.add_argument(
        "--tone",
        default="practical",
        choices=["friendly", "professional", "practical", "conversational"],
        help="Tone of the article.",
    )
    parser.add_argument(
        "--model",
        default="sonar",
        choices=["sonar", "sonar-reasoning", "sonar-pro", "sonar-deep-research"],
        help="Perplexity model to use.",
    )
    parser.add_argument(
        "--minutes",
        type=int,
        default=10,
        help="Target reading time in minutes.",
    )
    parser.add_argument(
        "--outline-depth",
        type=int,
        default=3,
        help="Outline depth (number of heading levels).",
    )
    parser.add_argument(
        "--no-code",
        action="store_true",
        help="Reduce code blocks if set (focus on instructions instead).",
    )
    parser.add_argument(
        "--cta",
        default="Follow Praveen for more real‑world build guides.",
        help="Call to action appended to the article.",
    )
    parser.add_argument(
        "--save-md",
        default=str(Path("output") / "article.md"),
        help="Path to save the generated Markdown.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish the article to Medium after generation.",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=[],
        help="Medium tags (max 5 used).",
    )
    parser.add_argument(
        "--status",
        default="draft",
        choices=["draft", "public", "unlisted"],
        help="Publish status on Medium.",
    )
    parser.add_argument(
        "--canonical-url",
        default=None,
        help="Canonical URL if cross‑posting.",
    )
    parser.add_argument(
        "--pplx-key",
        default=None,
        help="Override Perplexity API key (otherwise load from .env).",
    )
    parser.add_argument(
        "--medium-token",
        default=None,
        help="Override Medium integration token (otherwise load from .env).",
    )

    args = parser.parse_args(argv)

    # 1) Generate article
    generator = PerplexityGenerator(api_key=args.pplx_key)
    article_md = generator.generate_article(
        topic=args.topic,
        audience_level=args.audience,
        tone=args.tone,
        model=args.model,
        include_code=not args.no_code,
        outline_depth=args.outline_depth,
        target_minutes=args.minutes,
        call_to_action=args.cta,
    )

    # Save locally
    outfile = Path(args.save_md)
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(article_md, encoding="utf-8")
    print(f"[OK] Saved generated article to {outfile}")

    # 2) Optionally publish to Medium
    if args.publish:
        meta = parse_frontmatter(article_md)
        title = meta.get("title") or f"{args.topic} — with Indian Mini Projects by Praveen"
        suggested_tags_raw = meta.get("suggested_tags")
        # crude split if comma-separated
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


if __name__ == "__main__":  # pragma: no cover
    main()
