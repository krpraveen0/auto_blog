"""
Module providing a wrapper around Medium's official API for posting articles.

This module defines a ``MediumPublisher`` class to authenticate using a
personal token, retrieve the current user's ID, and create posts. It includes
simple retry behaviour and returns parsed JSON responses on success. Errors
raised by the API or network are encapsulated in ``MediumError``.

See Also
--------
https://github.com/Medium/medium-api-docs for full API details.
"""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any, Literal

import requests
from requests.adapters import HTTPAdapter, Retry
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    def load_dotenv(*args: Any, **kwargs: Any) -> None:
        """Fallback no‑op when python‑dotenv is not installed."""
        return None  # type: ignore


class MediumError(RuntimeError):
    """Raised when the Medium API returns an error or unexpected output."""
    pass


PublishStatus = Literal["draft", "public", "unlisted"]


class MediumPublisher:
    """
    Publish articles to Medium using their official API.

    Parameters
    ----------
    token:
        A Medium integration token. If omitted, the ``MEDIUM_TOKEN``
        environment variable will be loaded via ``dotenv``.
    base_url:
        The base endpoint for the API. Defaults to ``https://api.medium.com/v1``.

    Notes
    -----
    This class uses a ``requests.Session`` configured with retry logic for
    resilience. All responses are parsed as JSON. Non‑2xx responses raise
    ``MediumError``.
    """

    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.medium.com/v1") -> None:
        load_dotenv()
        self.token = token or os.getenv("MEDIUM_TOKEN")
        if not self.token:
            raise MediumError(
                "MEDIUM_TOKEN is missing. Set it in a .env file or pass it "
                "explicitly when creating MediumPublisher."
            )
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Internal helper to perform an HTTP request and parse JSON."""
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, timeout=30, **kwargs)
        try:
            payload = response.json()
        except ValueError:
            response.raise_for_status()
            raise MediumError("Non‑JSON response received from Medium.")
        if not response.ok:
            raise MediumError(f"Medium API error {response.status_code}: {payload}")
        return payload

    def get_user_id(self) -> str:
        """
        Retrieve the user ID associated with the current token.

        Returns
        -------
        str
            The authenticated user's Medium ID.
        """
        data = self._request("GET", "/me")
        try:
            return data["data"]["id"]
        except KeyError as exc:
            raise MediumError(f"Unexpected response for /me: {data}") from exc

    def upload_image(self, image_path: str, content_type: str = "image/png") -> str:
        """Upload an image to Medium and return its hosted URL.

        Parameters
        ----------
        image_path:
            Path to the image file to upload.
        content_type:
            MIME type of the image. Defaults to ``image/png``.

        Returns
        -------
        str
            The URL of the hosted image returned by Medium.
        """
        url = f"{self.base_url}/images"
        headers = self.session.headers.copy()
        # ``requests`` sets the correct multipart headers when ``files`` is used
        headers.pop("Content-Type", None)
        with open(image_path, "rb") as fh:
            files = {"image": (os.path.basename(image_path), fh, content_type)}
            response = self.session.post(url, files=files, headers=headers, timeout=30)
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise MediumError("Non-JSON response received from Medium.")
        if not response.ok:
            raise MediumError(f"Medium API error {response.status_code}: {data}")
        try:
            return data["data"]["url"]
        except KeyError as exc:
            raise MediumError(f"Unexpected response for /images: {data}") from exc

    def publish_article(
        self,
        title: str,
        content_markdown: str,
        tags: Optional[List[str]] = None,
        publish_status: PublishStatus = "draft",
        canonical_url: Optional[str] = None,
        notify_followers: bool = False,
        license: str = "all-rights-reserved",
        content_format: Literal["markdown", "html"] = "markdown",
    ) -> Dict[str, Any]:
        """
        Publish a new article on Medium.

        Parameters
        ----------
        title:
            The title of the article. This may override the title found in
            frontmatter if provided.
        content_markdown:
            The full article in Markdown or HTML.
        tags:
            A list of tags. Medium allows up to 5. Excess tags will be ignored.
        publish_status:
            One of ``draft``, ``public``, or ``unlisted``.
        canonical_url:
            The original source if cross‑posting. Optional.
        notify_followers:
            Whether followers should receive a notification when the article is
            published. Only relevant when the status is ``public``.
        license:
            The license under which the article is published.
        content_format:
            The format of ``content_markdown``; either ``markdown`` or ``html``.

        Returns
        -------
        dict
            Parsed JSON response from Medium's API describing the created post.
        """
        user_id = self.get_user_id()
        body: Dict[str, Any] = {
            "title": title,
            "contentFormat": content_format,
            "content": content_markdown,
            "publishStatus": publish_status,
            "notifyFollowers": notify_followers,
            "license": license,
        }
        if tags:
            body["tags"] = tags[:5]
        if canonical_url:
            body["canonicalUrl"] = canonical_url
        return self._request("POST", f"/users/{user_id}/posts", json=body)
