from __future__ import annotations
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from db.helpers import save_article_image

# Regular expression to capture Python fenced code blocks
CODE_BLOCK_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)
DIAGRAM_TYPE_RE = re.compile(r"Diagram\(['\"]([^'\"]+)['\"]")


def _execute_diagram(code: str) -> Tuple[bytes, str]:
    """Execute a diagrams code block and return image bytes and extension."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        before = set(tmp_path.iterdir())
        env = os.environ.copy()
        env.setdefault("DIAGRAMS_SHOW", "false")
        subprocess.run(
            ["python", "-"],
            input=code,
            text=True,
            cwd=tmp,
            check=True,
            env=env,
        )
        after = set(tmp_path.iterdir())
        new_files = [p for p in after - before if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg"}]
        if not new_files:
            raise RuntimeError("No diagram image generated")
        src = new_files[0]
        data = src.read_bytes()
        return data, src.suffix.lower()


def render_diagrams_to_images(md: str, article_id: int) -> Tuple[str, List[str]]:
    """Replace diagrams code blocks in Markdown with generated images.

    Parameters
    ----------
    md: str
        Markdown content possibly containing Python ``diagrams`` code blocks.
    article_id: int
        Identifier for the article; used when persisting images.

    Returns
    -------
    tuple[str, list[str]]
        A tuple containing the transformed Markdown and a list of hosted image
        URLs written during processing.
    """
    out_md_parts: List[str] = []
    image_urls: List[str] = []
    last_end = 0

    for idx, match in enumerate(CODE_BLOCK_RE.finditer(md), start=1):
        out_md_parts.append(md[last_end:match.start()])
        code = match.group(1).strip()
        if "from diagrams" in code or "Diagram(" in code:
            try:
                image_bytes, _ = _execute_diagram(code)
                name_match = DIAGRAM_TYPE_RE.search(code)
                diagram_type = name_match.group(1) if name_match else f"Diagram {idx}"
                url = save_article_image(article_id, diagram_type, image_bytes)
                image_urls.append(url)
                out_md_parts.append(f"![{diagram_type}]({url})")
            except Exception:
                out_md_parts.append(match.group(0))
        else:
            out_md_parts.append(match.group(0))
        last_end = match.end()

    out_md_parts.append(md[last_end:])
    new_md = "".join(out_md_parts)
    return new_md, image_urls
