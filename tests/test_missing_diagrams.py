import argparse
import logging

from app import cli


def test_cmd_generate_warns_on_missing_diagram(monkeypatch, caplog):
    sample_md = (
        "# Title\n\n"
        "## Overview\n"
        "Text\n"
        "```mermaid\n"
        "graph TD;\nA-->B\n"
        "```\n\n"
        "## Data Flow\n"
        "More text\n"
    )

    class DummyGenerator:
        def __init__(self, api_key):
            pass

        def generate_article(self, **kwargs):
            return sample_md

        def refine_article(self, markdown, model="sonar"):
            return markdown

    monkeypatch.setattr(cli, "PerplexityGenerator", DummyGenerator)
    monkeypatch.setattr(cli, "render_diagrams_to_images", lambda md, article_id: (md, []))
    monkeypatch.setattr(cli, "update_article", lambda client, article_id, **values: None)
    monkeypatch.setattr(cli, "get_client", lambda key: object())
    monkeypatch.setattr(cli, "init_db", lambda client: None)
    monkeypatch.setattr(cli, "fetch_article", lambda client, id: {"id": id, "topic": "Topic", "summary": ""})

    args = argparse.Namespace(
        id=1,
        db_key=None,
        pplx_key="k",
        audience="beginner",
        tone="tutorial",
        model="sonar",
        no_code=False,
        outline_depth=3,
        minutes=10,
        cta="CTA",
        format="single article",
        goal="",
        stack_focus="",
        timebox=None,
        diagram_language="mermaid",
        diagram_sections=["Overview", "Data Flow"],
        save_md=None,
        publish=False,
        refine=False,
        tags=[],
        status="draft",
        canonical_url=None,
        medium_token=None,
    )

    with caplog.at_level(logging.WARNING):
        cli.cmd_generate(args)

    assert "Section 'Data Flow' is missing mermaid diagram" in caplog.text
