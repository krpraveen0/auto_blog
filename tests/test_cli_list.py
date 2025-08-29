import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app import cli


def test_cmd_list_handles_string_schedule(monkeypatch, capsys):
    rows = [{"id": 1, "topic": "t", "scheduled_at": "2024-01-01T00:00:00"}]
    monkeypatch.setattr(cli, "get_client", lambda db_key: None)
    monkeypatch.setattr(cli, "init_db", lambda client: None)
    monkeypatch.setattr(cli, "list_planned_articles", lambda client: rows)
    cli.cmd_list(argparse.Namespace(db_key=None))
    assert "2024-01-01T00:00:00" in capsys.readouterr().out
