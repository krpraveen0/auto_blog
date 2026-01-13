"""
Integration tests requiring API keys
These tests will be skipped if API keys are not available
"""

import pytest
import os
from pathlib import Path


@pytest.mark.skipif(
    not os.getenv('PERPLEXITY_API_KEY'),
    reason="PERPLEXITY_API_KEY not set"
)
def test_perplexity_client():
    """Test Perplexity API client"""
    from llm.client import PerplexityClient
    import yaml
    
    config = yaml.safe_load(open('config.yaml'))
    client = PerplexityClient(config['llm'])
    
    # Simple test generation
    response = client.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say 'test successful' in one sentence."
    )
    
    assert len(response) > 0
    assert isinstance(response, str)


@pytest.mark.skipif(
    not os.getenv('PERPLEXITY_API_KEY'),
    reason="PERPLEXITY_API_KEY not set"
)
def test_content_analyzer():
    """Test full content analysis pipeline"""
    from llm.analyzer import ContentAnalyzer
    import yaml
    
    config = yaml.safe_load(open('config.yaml'))
    analyzer = ContentAnalyzer(config['llm'])
    
    # Test item
    item = {
        'id': 'test_1',
        'title': 'Test Paper on Transformers',
        'url': 'https://example.com',
        'summary': 'A novel approach to transformer architectures that improves efficiency.',
        'source': 'arxiv',
        'authors': ['Test Author']
    }
    
    # Run analysis (only first 2 stages to save API calls)
    config['llm']['prompt_stages'] = ['fact_extraction', 'engineer_summary']
    analyzer = ContentAnalyzer(config['llm'])
    
    analysis = analyzer.analyze(item)
    
    assert 'fact_extraction' in analysis
    assert 'engineer_summary' in analysis
    assert len(analysis['fact_extraction']) > 0


@pytest.mark.skipif(
    not os.getenv('GITHUB_TOKEN'),
    reason="GITHUB_TOKEN not set"
)
def test_github_publisher_init():
    """Test GitHub Pages publisher initialization"""
    from publishers.github_pages import GitHubPagesPublisher
    import yaml
    
    config = yaml.safe_load(open('config.yaml'))
    publisher = GitHubPagesPublisher(config['publishing']['blog'])
    
    assert publisher.enabled == True
    assert publisher.github is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
