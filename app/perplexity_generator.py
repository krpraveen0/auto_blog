"""
Module providing a wrapper around the Perplexity chat completions API.

This module defines a ``PerplexityGenerator`` class that uses the
OpenAI‑compatible ``/chat/completions`` endpoint exposed by Perplexity to
generate rich, Markdown articles. The generator is designed to be reused as a
library by CLI tools or other code. Users can customise the tone, audience,
outline depth and other options on a per‑call basis.

If you do not wish to rely on environment variables you can pass your API key
directly when instantiating the class; otherwise the ``PERPLEXITY_API_KEY``
variable will be read from a ``.env`` file in the working directory.
"""

from __future__ import annotations

import os
import json
import re
from typing import Literal, Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter, Retry
try:
    # python‑dotenv is optional; if unavailable we gracefully ignore the
    # missing import and rely on environment variables being set already.
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    def load_dotenv(*args: Any, **kwargs: Any) -> None:
        """Fallback no‑op when python‑dotenv is not installed."""
        return None  # type: ignore


class PerplexityError(RuntimeError):
    """Raised when the Perplexity API returns an error or unexpected output."""
    pass


PerpModel = Literal[
    "sonar",
    "sonar-reasoning",
    "sonar-pro",
    "sonar-deep-research",
]


class PerplexityGenerator:
    """
    Generate full articles via Perplexity's OpenAI‑compatible API.

    Parameters
    ----------
    api_key:
        The Perplexity API key. If omitted, the ``PERPLEXITY_API_KEY`` will be
        loaded from the local environment using ``dotenv``.
    base_url:
        The base URL for the API. You typically won't need to change this.

    Notes
    -----
    The generator uses a ``requests.Session`` configured with basic retry
    behaviour for network resilience. Errors are raised as ``PerplexityError``.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.perplexity.ai") -> None:
        # Load environment variables from .env if present.
        load_dotenv()
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise PerplexityError(
                "PERPLEXITY_API_KEY is missing. Set it in a .env file or pass it "
                "explicitly when creating PerplexityGenerator."
            )

        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        # Configure simple retries on transient failures.
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to POST to the Perplexity API and return parsed JSON."""
        url = f"{self.base_url}{path}"
        response = self.session.post(url, json=json, timeout=60)
        try:
            data = response.json()
        except ValueError:
            # If no JSON, raise HTTP error if possible.
            response.raise_for_status()
            raise PerplexityError("Non‑JSON response received from Perplexity.")
        if not response.ok:
            raise PerplexityError(f"Perplexity API error {response.status_code}: {data}")
        return data

    def generate_article(
        self,
        topic: str,
        audience_level: Literal["beginner", "intermediate", "advanced"] = "beginner",
        tone: Literal["friendly", "professional", "practical", "conversational"] = "practical",
        model: PerpModel = "sonar",
        include_code: bool = True,
        outline_depth: int = 3,
        target_minutes: int = 10,
        call_to_action: str = "Follow Praveen for more real‑world build guides.",
    ) -> str:
        """
        Generate an article in Markdown format around a given topic.

        The resulting text includes frontmatter, a TL;DR, multiple sections with
        mini projects using Indian data sets, personal tips attributed to
        'Praveen', and a concluding call to action. The generator encapsulates
        prompt engineering for typical Perplexity models.

        Parameters
        ----------
        topic:
            The primary subject of the article.
        audience_level:
            Indicates the technical familiarity of readers.
        tone:
            The desired tone of the article.
        model:
            One of the supported Perplexity models.
        include_code:
            Whether to include runnable code snippets. If ``False``, the article
            will emphasise step‑by‑step instructions over code.
        outline_depth:
            Controls the depth of the generated outline (number of heading levels).
        target_minutes:
            Approximate reading time for the article.
        call_to_action:
            A closing call to action for readers.

        Returns
        -------
        str
            A full Markdown article ready for publication.
        """
        system_message = (
            "You are a senior technical writer and educator. Produce publish‑ready "
            "Markdown articles with runnable code and practical projects."
        )
        user_prompt = f"""
Topic: {topic}

Write a Medium‑ready article that strictly follows these rules:

Audience: {audience_level}
Tone: {tone}
Reading time target: ~{target_minutes} minutes
Outline depth (levels): {outline_depth}

MANDATORY CONTENT:
1) Frontmatter (YAML fenced) with: title, seo_description (<=150 chars),
   suggested_tags (<=5), canonical_url (empty), author: Praveen
2) A catchy H1 title
3) A brief TL;DR bullet list
4) Context with Indian examples (payments via UPI, IRCTC bookings, cricket
   stats, Aadhaar eKYC flows, Indian retail prices, Rupay cards, Indian cities, etc.)
5) Mini Projects (2–3):
   - Clearly named, each with GOAL, PREREQS, STEP‑BY‑STEP, CODE (Python/Java/JS as relevant),
     SAMPLE INPUT/OUTPUT, and a "What could go wrong?" section.
   - Use realistic Indian data or scenarios (e.g., Mumbai weather data, NPCI/UPI mock flows,
     local CSVs).
   - Personalize with 'Praveen' (e.g., "Praveen's Tip", "Praveen's Checklist").
6) At least one "Deep Dive" explanation section.
7) A troubleshooting/FAQ section.
8) A concluding CTA that includes: {call_to_action}

STYLE:
- Use Markdown, headings, lists, tables when helpful.
- Prefer code that can run as‑is; keep secrets/config in env vars.
- Keep any external links minimal and optional.
- Avoid fluff. Be specific and instructive.

If code is irrelevant to the topic, replace with commands or configs.
If {include_code} is False, minimise code and focus on step‑by‑step actions.
        """.strip()

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "top_p": 0.9,
        }

        data = self._post("/chat/completions", payload)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise PerplexityError(
                f"Unexpected response shape from Perplexity: {data}"
            ) from exc

    def generate_series_plan(
        self,
        topic: str,
        posts: int = 5,
        model: PerpModel = "sonar",
    ) -> list[dict]:
        """Generate a plan for a standalone mini‑project article series."""
        system_message = (
            "You are an expert educational content planner. "
            "Return structured ideas for independent tutorial posts."
        )
        user_prompt = f"""
Topic: {topic}

Produce {posts} self-contained blog post ideas about the above topic.
Each idea must describe a complete mini-project that does not depend on
the other posts. Respond ONLY with valid JSON representing an array of
objects, each having the fields 'title' and 'summary'.
        """.strip()

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "top_p": 0.9,
        }

        data = self._post("/chat/completions", payload)
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise PerplexityError(
                f"Unexpected response shape from Perplexity: {data}"
            ) from exc

        content = content.strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
        if fenced:
            content = fenced.group(1).strip()

        try:
            plan = json.loads(content)
        except ValueError as exc:
            raise PerplexityError(
                f"Perplexity did not return valid JSON: {content}"
            ) from exc

        if not isinstance(plan, list):
            raise PerplexityError("Expected a JSON array of objects.")

        results: list[dict] = []
        for item in plan:
            if (
                not isinstance(item, dict)
                or "title" not in item
                or "summary" not in item
            ):
                raise PerplexityError(f"Malformed entry in plan: {item}")
            results.append(
                {"title": str(item["title"]), "summary": str(item["summary"])}
            )

        return results


def generate_series_plan(
    topic: str,
    posts: int = 5,
    model: PerpModel = "sonar",
    api_key: Optional[str] = None,
    base_url: str = "https://api.perplexity.ai",
) -> list[dict]:
    """Convenience wrapper around :class:`PerplexityGenerator`."""
    generator = PerplexityGenerator(api_key=api_key, base_url=base_url)
    return generator.generate_series_plan(topic, posts, model=model)
