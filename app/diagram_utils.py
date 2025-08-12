from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

# Regular expression to capture Python fenced code blocks
CODE_BLOCK_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _execute_diagram(code: str, out_dir: Path, index: int) -> Path:
    """Execute a diagrams code block and return path to generated image.

    The code is executed in an isolated temporary directory. Any image file
    produced by the ``diagrams`` library is moved into ``out_dir`` with a
    deterministic name such as ``diagram_1.png``. The function returns the full
    path to the saved image.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        before = set(tmp_path.iterdir())
        env = os.environ.copy()
        # Ensure diagrams does not attempt to open the image viewer
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
        # Take the first generated file
        src = new_files[0]
        suffix = src.suffix.lower()
        dest = out_dir / f"diagram_{index}{suffix}"
        shutil.move(str(src), dest)
        return dest


def render_diagrams_to_images(md: str, image_dir: str | Path = "diagrams") -> Tuple[str, List[str]]:
    """Replace diagrams code blocks in Markdown with generated images.

    Parameters
    ----------
    md: str
        Markdown content possibly containing Python ``diagrams`` code blocks.
    image_dir: str or Path, optional
        Directory where generated images will be stored. Created if missing.

    Returns
    -------
    tuple[str, list[str]]
        A tuple containing the transformed Markdown and a list of image paths
        written during processing.
    """
    images_path = Path(image_dir)
    images_path.mkdir(parents=True, exist_ok=True)

    out_md_parts: List[str] = []
    image_paths: List[str] = []
    last_end = 0

    for idx, match in enumerate(CODE_BLOCK_RE.finditer(md), start=1):
        out_md_parts.append(md[last_end:match.start()])
        code = match.group(1).strip()
        if "from diagrams" in code or "Diagram(" in code:
            try:
                img_path = _execute_diagram(code, images_path, idx)
                rel_path = img_path.as_posix()
                image_paths.append(rel_path)
                out_md_parts.append(f"![Diagram {idx}]({rel_path})")
            except Exception:
                # If rendering fails, retain original code block
                out_md_parts.append(match.group(0))
        else:
            out_md_parts.append(match.group(0))
        last_end = match.end()

    out_md_parts.append(md[last_end:])
    new_md = "".join(out_md_parts)
    return new_md, image_paths
