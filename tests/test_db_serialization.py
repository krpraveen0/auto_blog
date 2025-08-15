import os
import sys
from datetime import datetime
from types import SimpleNamespace

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db import save_article, update_article, fetch_article


def test_save_article_serializes_datetime():
    table_payload = {}

    class DummyInsert:
        def __init__(self, payload):
            table_payload.update(payload)
        def execute(self):
            return SimpleNamespace(data=[{"id": 1}])

    class DummyTable:
        def insert(self, payload):
            return DummyInsert(payload)

    class DummyClient:
        def __init__(self):
            self._table = DummyTable()
        def table(self, name):
            assert name == "articles"
            return self._table

    client = DummyClient()
    dt = datetime(2024, 1, 1, 2, 3, 4)
    save_article(
        client,
        topic="topic",
        status="planned",
        markdown="",
        scheduled_at=dt,
    )
    assert table_payload["scheduled_at"] == dt.isoformat()


def test_save_article_serializes_markdown_raw():
    table_payload = {}

    class DummyInsert:
        def __init__(self, payload):
            table_payload.update(payload)

        def execute(self):
            return SimpleNamespace(data=[{"id": 1}])

    class DummyTable:
        def insert(self, payload):
            return DummyInsert(payload)

    class DummyClient:
        def __init__(self):
            self._table = DummyTable()

        def table(self, name):
            assert name == "articles"
            return self._table

    client = DummyClient()
    save_article(
        client,
        topic="topic",
        status="planned",
        markdown="",
        markdown_raw="# raw",
    )
    assert table_payload["markdown_raw"] == "# raw"


def test_update_article_serializes_markdown_raw():
    table_payload = {}

    class DummyUpdate:
        def __init__(self, payload):
            table_payload.update(payload)

        def eq(self, field, value):
            assert field == "id"
            assert value == 1
            return self

        def execute(self):
            return None

    class DummyTable:
        def update(self, payload):
            return DummyUpdate(payload)

    class DummyClient:
        def __init__(self):
            self._table = DummyTable()

        def table(self, name):
            assert name == "articles"
            return self._table

    client = DummyClient()
    update_article(client, 1, markdown_raw="raw")
    assert table_payload["markdown_raw"] == "raw"


def test_fetch_article_returns_markdown_raw():
    class DummySelect:
        def __init__(self, data):
            self._data = data

        def eq(self, field, value):
            assert field == "id"
            assert value == 1
            return self

        def execute(self):
            return SimpleNamespace(data=self._data)

    class DummyTable:
        def select(self, columns):
            assert columns == "*"
            return DummySelect([
                {"id": 1, "markdown": "html", "markdown_raw": "# raw"}
            ])

    class DummyClient:
        def __init__(self):
            self._table = DummyTable()

        def table(self, name):
            assert name == "articles"
            return self._table

    client = DummyClient()
    article = fetch_article(client, 1)
    assert article["markdown_raw"] == "# raw"
