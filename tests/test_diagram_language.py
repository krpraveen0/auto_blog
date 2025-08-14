import pytest

from app.perplexity_generator import PerplexityGenerator


def test_mermaid_diagram_language_propagates(monkeypatch):
    captured = {}

    def fake_post(self, path, json):
        captured['payload'] = json
        # Return minimal structure expected by generate_article
        return {'choices': [{'message': {'content': 'dummy'}}]}

    monkeypatch.setattr(PerplexityGenerator, '_post', fake_post)

    gen = PerplexityGenerator(api_key='test')
    gen.generate_article('Sample', diagram_language='mermaid')

    user_prompt = captured['payload']['messages'][1]['content']
    assert 'Architecture/System Design (mermaid diagrams library by default)' in user_prompt
    assert 'Provide mermaid `diagrams` library code blocks' in user_prompt
    assert 'Include mermaid `diagrams` code blocks' in user_prompt
    assert 'Use Python only when generating `diagrams` library code' in user_prompt
