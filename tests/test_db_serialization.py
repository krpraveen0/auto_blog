import os
import sys
from datetime import datetime
from types import SimpleNamespace

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db import save_article


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
