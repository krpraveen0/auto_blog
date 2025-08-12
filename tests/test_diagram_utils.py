from pathlib import Path

from app import diagram_utils


def test_render_diagrams_to_images(tmp_path, monkeypatch):
    md = (
        "Intro\n\n"  # simple markdown with diagrams code block
        "```python\nfrom diagrams import Diagram\nwith Diagram('Test'):\n    pass\n```\n"
    )

    def fake_run(cmd, input, text, cwd, check, env):
        # Simulate diagram generation by creating a dummy file
        Path(cwd, "dummy.png").write_bytes(b"fake")
        return None

    monkeypatch.setattr(diagram_utils.subprocess, "run", fake_run)

    new_md, paths = diagram_utils.render_diagrams_to_images(md, image_dir=tmp_path)

    assert "![Diagram 1]" in new_md
    assert len(paths) == 1
    assert Path(paths[0]).exists()
