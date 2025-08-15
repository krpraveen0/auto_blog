import pytest

from app.perplexity_generator import PerplexityGenerator


def test_diagram_sections_in_prompt(monkeypatch):
    captured = {}

    def fake_post(self, path, json):
        captured['payload'] = json
        return {'choices': [{'message': {'content': 'dummy'}}]}

    monkeypatch.setattr(PerplexityGenerator, '_post', fake_post)

    gen = PerplexityGenerator(api_key='test')
    gen.generate_article('Sample', diagram_language='mermaid', diagram_sections=['Overview', 'Data Flow'])

    user_prompt = captured['payload']['messages'][1]['content']
    assert 'For section "Overview", include a separate mermaid `diagrams` code block.' in user_prompt
    assert 'For section "Data Flow", include a separate mermaid `diagrams` code block.' in user_prompt
