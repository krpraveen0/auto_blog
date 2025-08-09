"""
Top‑level package for the Medium auto‑article generator.

This package exposes two main classes:

``PerplexityGenerator``
    Provides a high‑level interface to Perplexity's OpenAI‑compatible API for
    generating full Markdown articles with Indian examples and personal
    branding. See :mod:`.perplexity_generator` for details.

``MediumPublisher``
    Wraps Medium's official API for posting articles. Use this class to
    authenticate with your Medium integration token and create posts. See
    :mod:`.medium_publisher` for details.
"""

from .perplexity_generator import (
    PerplexityGenerator,
    PerplexityError,
    PerpModel,
    generate_series_plan,
)
from .medium_publisher import MediumPublisher, MediumError, PublishStatus

__all__ = [
    "PerplexityGenerator",
    "PerplexityError",
    "PerpModel",
    "generate_series_plan",
    "MediumPublisher",
    "MediumError",
    "PublishStatus",
]
