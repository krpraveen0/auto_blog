import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.cli import parse_frontmatter


def test_parses_valid_yaml_frontmatter():
    md = (
        "---\n"
        "title: Sample Post\n"
        "tags: python, testing\n"
        "---\n"
        "Content"
    )
    meta = parse_frontmatter(md)
    assert meta == {"title": "Sample Post", "tags": "python, testing"}


def test_handles_missing_frontmatter():
    md = "No front matter here"
    meta = parse_frontmatter(md)
    assert meta == {}


def test_handles_malformed_frontmatter():
    md = "---\nmissing closing fence"
    meta = parse_frontmatter(md)
    assert meta == {}
