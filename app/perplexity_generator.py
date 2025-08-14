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

    def suggest_trending_topics(
        self,
        count: int = 5,
        model: PerpModel = "sonar",
    ) -> list[str]:
        """Return a list of currently trending blog topics.

        The function queries Perplexity for fresh, technical subjects that are
        popular around the current date. The response is expected to be a JSON
        array of short title strings. A :class:`PerplexityError` is raised if the
        response cannot be parsed.
        """
        from datetime import date

        today = date.today().isoformat()
        system_message = (
            "You are a research assistant for software bloggers. Return only "
            "concise topic titles.")
        user_prompt = f"""
Date: {today}

List {count} trending software or data topics that would make engaging blog posts.
Respond ONLY with a JSON array of strings.
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
            content = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise PerplexityError(
                f"Unexpected response shape from Perplexity: {data}"
            ) from exc

        fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
        if fenced:
            content = fenced.group(1).strip()

        try:
            topics = json.loads(content)
        except ValueError as exc:
            raise PerplexityError(
                f"Perplexity did not return valid JSON: {content}"
            ) from exc

        if not isinstance(topics, list):
            raise PerplexityError("Expected a JSON array of strings.")

        return [str(t) for t in topics]

    def generate_article(
        self,
        topic: str,
        audience_level: Literal["beginner", "intermediate", "advanced"] = "beginner",
        tone: Literal[
            "casual",
            "tutorial",
            "storytelling",
            "formal",
            "friendly",
            "professional",
            "practical",
            "conversational",
        ] = "tutorial",
        model: PerpModel = "sonar",
        include_code: bool = True,
        outline_depth: int = 3,
        target_minutes: int = 10,
        call_to_action: str = "Follow Praveen for more fullstack AI & cloud build guides.",
        expertise: str = "fullstack AI cloud developer",
        content_format: Literal["single article", "series"] = "single article",
        goal: str = "",
        stack_focus: str = "",
        timebox: str = "~15-minute read",
        diagram_language: str = "python",
    ) -> str:
        """
        Generate an article in Markdown format around a given topic.

        The function produces flexible outlines that always provide frontmatter,
        a TL;DR, a short social-media teaser and a closing call to action.
        Beyond those basics, section structure and examples are driven by the
        supplied topic and current trends so repeated runs do not feel canned.
        The generator still showcases Praveen's expertise as a {expertise} but
        leaves room for bespoke mini projects or case studies based on user
        prompts or trend analysis.

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
        expertise:
            A short phrase describing Praveen's background. This will be woven
            into the article to emphasise authority.
        content_format:
            Either ``"single article"`` or ``"series"`` to control the output
            style.
        goal:
            Learning outcome or objective for the reader.
        stack_focus:
            Comma separated technologies or domains to emphasise.
        timebox:
            Optional duration such as ``"30-day bootcamp"`` or ``"~15-minute read"``.
        diagram_language:
            Language to use for diagram code blocks (e.g. ``"python"`` or ``"mermaid"``).

        Returns
        -------
        str
            A full Markdown article ready for publication.
        """
        system_message = (
            "You are a senior technical writer, educator and growth hacker. "
            "Produce publish‑ready Markdown articles with runnable code, "
            "practical projects and viral, shareable hooks."
        )
        user_prompt = f"""
Role & Goal
Act as a passionate senior developer, tech mentor, and content curator across DSA, ML, AI, Go (Golang), Java, React, AWS, and System Design. Use Python only when generating `diagrams` library code; otherwise choose languages that best suit each topic. Create either a single deep‑dive article or a multi‑part bootcamp series for Medium and similar platforms. Make it hands‑on, industry‑relevant, beginner‑friendly (explain like I’m 5), and fully attributed.

Dynamic Controls
topic: {topic}
format: {content_format}
audience_level: {audience_level}
goal: {goal}
tone: {tone}
stack_focus: {stack_focus}
timebox: {timebox}

Trending Topic Pull (Step 0)
Find currently trending and in‑demand topics aligned with {stack_focus} from reputable sources. Briefly justify why this topic is hot now (hiring signals, ecosystem releases, library updates, cloud announcements).

Output Mode (Step 1)
If {content_format} == "single article": produce one comprehensive tutorial.
If {content_format} == "series": produce a series outline (titles, learning objectives, prerequisites, capstone) and deliver Part 1 in full. Include a short preview for Parts 2–N.

Must‑Have Structure (Step 2)
Title & Hook (why it matters now)
Prerequisites (tools, skills, repo templates)
Concepts in Simple Language (ELI5 + precise terms)
Architecture/System Design ({diagram_language} diagrams library by default)
Hands‑On Build (copy‑runnable, well‑commented code; minimal setup; include validation checks and expected outputs)
Testing & Validation (CLI commands, unit tests, curl/Postman examples, sample inputs/outputs)
Performance, Cost, and Reliability (gotchas, trade‑offs, scaling tips)
Common Pitfalls & Fixes
Industry Use Cases & Hiring Signals
Next Steps / Extensions
References & Credits
Used Resources to Curate

Diagram Requirements (Step 3)
Provide {diagram_language} `diagrams` library code blocks and describe how to render them. Use multiple small diagrams where helpful.

Hands‑On & Real‑World (Step 4)
Include 2–3 production‑style examples mapping to {stack_focus}. Show working code in appropriate languages and include infra/deploy notes where relevant. Add metrics/observability hints.

Quality Bar (Step 5)
Use clear numbered steps, short paragraphs, and simple words. Validate every command or code block. Credit third‑party sources. Avoid defaulting to Python for examples unless the topic demands it. End with a "Used Resources to Curate" section listing all sources.

Final Delivery Format
Write the article or series in {tone} tone for {audience_level} learners, timebox: {timebox}. Use section headers, checklists, tables where helpful. Include {diagram_language} `diagrams` code blocks and notes for rendering them. Conclude with a call to action: {call_to_action}. End with "References & Credits" and "Used Resources to Curate" lists.
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

    def refine_article(
        self, markdown: str, model: PerpModel = "sonar"
    ) -> str:
        """Refine a Markdown draft by proofreading and tightening prose."""
        system_message = (
            "You are a meticulous technical editor. Improve clarity, grammar and "
            "flow while preserving code blocks, links and overall meaning. "
            "Return polished Markdown only."
        )
        user_prompt = f"Refine the following article:\n\n```markdown\n{markdown}\n```"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
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
        """Generate a trend-aware plan for a standalone mini-project series."""
        system_message = (
            "You are an expert educational content planner. "
            "Return structured ideas for independent tutorial posts."
        )
        user_prompt = f"""
Topic: {topic}

Produce {posts} self-contained blog post ideas based on current trends
or user interests around the topic. Ensure each idea explores a distinct
angle. Each idea must describe a complete mini-project that does not
depend on the other posts. Respond ONLY with valid JSON representing an
array of objects, each having the fields 'title' and 'summary'.
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

    def generate_job_postings(
        self,
        role: str,
        count: int = 5,
        model: PerpModel = "sonar",
    ) -> str:
        """Generate markdown-formatted job postings for a role.

        Each posting is separated by a blank line and contains a heading with
        bullet points for location, experience and skills. This ensures clear
        spacing and a consistent, attractive layout.
        """
        system_message = (
            "You are an assistant that drafts clean, well-structured job posts"
        )
        user_prompt = f"""
Write {count} realistic job postings for the role "{role}".

Format each posting in Markdown using:

### {{Job Title}} at {{Company}}

- **Location:** City or Remote
- **Experience:** Years or level
- **Key Skills:** comma separated list
- **Description:** one short paragraph

Separate each posting with a blank line and keep all formatting in Markdown.
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
    topic: str,
    posts: int = 5,
    model: PerpModel = "sonar",
    api_key: Optional[str] = None,
    base_url: str = "https://api.perplexity.ai",
) -> list[dict]:
    """Convenience wrapper around :class:`PerplexityGenerator`."""
    generator = PerplexityGenerator(api_key=api_key, base_url=base_url)
    return generator.generate_series_plan(topic, posts, model=model)


def suggest_trending_topics(
    count: int = 5,
    model: PerpModel = "sonar",
    api_key: Optional[str] = None,
    base_url: str = "https://api.perplexity.ai",
) -> list[str]:
    """Convenience wrapper that returns trending blog topics."""
    generator = PerplexityGenerator(api_key=api_key, base_url=base_url)
    return generator.suggest_trending_topics(count=count, model=model)
