from pathlib import Path

from app import diagram_utils


def test_render_diagrams_to_images(monkeypatch):
    md = (
        "Intro\n\n"  # simple markdown with diagrams code block
        "```python\nfrom diagrams import Diagram\nwith Diagram('Test'):\n    pass\n```\n"
    )

    def fake_run(cmd, input, text, cwd, check, env):
        # Simulate diagram generation by creating a dummy file
        Path(cwd, "dummy.png").write_bytes(b"fake")
        return None

    monkeypatch.setattr(diagram_utils.subprocess, "run", fake_run)

    captured = {}

    def fake_save(article_id, diagram_type, image_bytes):
        captured["article_id"] = article_id
        captured["diagram_type"] = diagram_type
        captured["image_bytes"] = image_bytes
        return "https://storage.example/img.png"

    monkeypatch.setattr(diagram_utils, "save_article_image", fake_save)

    new_md, urls = diagram_utils.render_diagrams_to_images(md, article_id=1)

    assert new_md.strip().startswith("Intro")
    assert "![Test](https://storage.example/img.png)" in new_md
    assert captured["article_id"] == 1
    assert captured["diagram_type"] == "Test"
    assert captured["image_bytes"] == b"fake"
    assert urls == ["https://storage.example/img.png"]
