import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.cli import parse_frontmatter


def test_basic_frontmatter_parsing():
    md = """---\ntitle: "Hello"\nseo_description: 'desc'\n---\nbody"""
    meta = parse_frontmatter(md)
    assert meta == {"title": "Hello", "seo_description": "desc"}


def test_ignores_comment_lines():
    md = """---\n# just a comment\ntitle: Example\n# another: comment\n---\n"""
    meta = parse_frontmatter(md)
    assert meta == {"title": "Example"}


def test_parses_lists_and_nested_values():
    md = """---\nname: Example\ntags:\n  - a\n  - b\nextra:\n  nested:\n    value: 1\n---\n"""
    meta = parse_frontmatter(md)
    assert meta == {
        "name": "Example",
        "tags": ["a", "b"],
        "extra": {"nested": {"value": 1}},
    }
