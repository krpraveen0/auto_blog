import argparse
from app.perplexity_generator import PerplexityGenerator
from app import cli


def test_refine_article_monkeypatch(monkeypatch):
    gen = PerplexityGenerator(api_key="key")

    def fake_post(path, json):
        return {"choices": [{"message": {"content": "better text"}}]}

    monkeypatch.setattr(gen, "_post", fake_post)
    result = gen.refine_article("raw text")
    assert result == "better text"
    assert result != "raw text"


def test_cmd_generate_with_refine(monkeypatch):
    raw_md = "raw"
    refined_md = "refined"

    class DummyGenerator:
        def __init__(self, api_key):
            pass

        def generate_article(self, **kwargs):
            return raw_md

        def refine_article(self, markdown, model="sonar"):
            assert markdown == raw_md
            return refined_md

    monkeypatch.setattr(cli, "PerplexityGenerator", DummyGenerator)
    monkeypatch.setattr(cli, "render_diagrams_to_images", lambda md: (md, []))

    captured = {}

    def fake_update(client, article_id, **values):
        captured["article_id"] = article_id
        captured.update(values)

    monkeypatch.setattr(cli, "update_article", fake_update)
    monkeypatch.setattr(cli, "get_client", lambda key: object())
    monkeypatch.setattr(cli, "init_db", lambda client: None)
    monkeypatch.setattr(cli, "fetch_article", lambda client, id: {"id": id, "topic": "Topic"})

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
        timebox="~15-minute read",
        diagram_language="python",
        save_md=None,
        publish=False,
        refine=True,
        tags=[],
        status="draft",
        canonical_url=None,
        medium_token=None,
    )

    cli.cmd_generate(args)

    assert captured["markdown_raw"] == raw_md
    assert captured["markdown"] == refined_md
    assert captured["status"] == "generated"
