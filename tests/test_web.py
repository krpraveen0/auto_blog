import app.web as web

def test_create_article(monkeypatch):
    class Gen:
        def generate_article(self, topic, audience_level, tone, goal):
            return "generated content"

    monkeypatch.setattr(web, "get_generator", lambda: Gen())
    monkeypatch.setattr(web, "get_db_client", lambda: object())
    saved = {}

    def fake_save_article(client, **kwargs):
        saved.update(kwargs)
        return 1

    monkeypatch.setattr(web, "save_article", fake_save_article)

    client = web.app.test_client()
    resp = client.post(
        "/create",
        data={"topic": "Foo", "audience_level": "beginner", "tone": "casual", "goal": ""},
    )
    assert resp.status_code == 200
    assert b"generated content" in resp.data
    assert saved["topic"] == "Foo"


def test_list_articles(monkeypatch):
    monkeypatch.setattr(web, "get_db_client", lambda: object())

    def fake_list(client):
        return [{"id": 1, "topic": "Foo"}]

    monkeypatch.setattr(web, "list_articles", fake_list)

    client = web.app.test_client()
    resp = client.get("/articles")
    assert resp.status_code == 200
    assert b"Foo" in resp.data
