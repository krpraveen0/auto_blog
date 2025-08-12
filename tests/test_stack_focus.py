import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.cli import infer_stack_focus_from_topic


def test_infer_golang():
    topic = "Automate the Boring Stuff Using Golang"
    assert infer_stack_focus_from_topic(topic) == "Go (Golang)"


def test_infer_multiple():
    topic = "Build a REST API with Python and AWS"
    assert infer_stack_focus_from_topic(topic) == "Python, AWS"
