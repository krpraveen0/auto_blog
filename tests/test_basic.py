"""
Basic tests for the AI Research Publisher
Run with: pytest tests/
"""

import pytest
from pathlib import Path
import yaml


def test_config_exists():
    """Test that config.yaml exists and is valid"""
    assert Path('config.yaml').exists()
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    assert 'sources' in config
    assert 'filters' in config
    assert 'llm' in config
    assert 'publishing' in config


def test_required_modules():
    """Test that all required modules can be imported"""
    # Sources
    from sources import arxiv, blogs, hackernews, github
    
    # Filters
    from filters import relevance, dedup, ranker
    
    # LLM
    from llm import client, prompts, analyzer
    
    # Formatters
    from formatters import blog, linkedin
    
    # Publishers
    from publishers import github_pages, linkedin_api
    
    # Utils
    from utils import logger, cache


def test_data_directories():
    """Test that data directories exist"""
    dirs = [
        'data/cache',
        'data/fetched',
        'data/drafts/blog',
        'data/drafts/linkedin'
    ]
    
    for dir_path in dirs:
        assert Path(dir_path).exists(), f"Directory {dir_path} does not exist"


def test_prompts_available():
    """Test that all prompt stages are defined"""
    from llm.prompts import get_prompt, get_system_prompt
    
    # Check system prompt
    system = get_system_prompt()
    assert len(system) > 0
    assert 'factual' in system.lower()
    
    # Check all stages
    stages = [
        'fact_extraction',
        'engineer_summary',
        'impact_analysis',
        'application_mapping',
        'blog_synthesis',
        'linkedin_formatting',
        'credibility_check'
    ]
    
    for stage in stages:
        prompt = get_prompt(stage, content='test', title='test', url='test', analyzed_content='test', generated_output='test')
        assert len(prompt) > 0


def test_arxiv_fetcher_init():
    """Test arXiv fetcher initialization"""
    from sources.arxiv import ArxivFetcher
    
    config = {
        'categories': ['cs.AI'],
        'max_results': 5
    }
    
    fetcher = ArxivFetcher(config)
    assert fetcher.categories == ['cs.AI']
    assert fetcher.max_results == 5


def test_relevance_filter_init():
    """Test relevance filter initialization"""
    from filters.relevance import RelevanceFilter
    
    config = {
        'max_age_days': 7,
        'keywords': {
            'high_priority': ['LLM', 'transformer'],
            'medium_priority': ['AI']
        },
        'exclude_keywords': ['crypto']
    }
    
    filter = RelevanceFilter(config)
    assert filter.max_age_days == 7
    assert 'llm' in filter.high_priority_keywords


def test_deduplicator():
    """Test deduplication logic"""
    from filters.dedup import Deduplicator
    
    config = {
        'title_similarity_threshold': 0.85,
        'url_hash': True
    }
    
    dedup = Deduplicator(config)
    
    items = [
        {'title': 'New LLM Model', 'url': 'https://example.com/1'},
        {'title': 'New LLM Model', 'url': 'https://example.com/1'},  # Duplicate
        {'title': 'Different Paper', 'url': 'https://example.com/2'}
    ]
    
    unique = dedup.deduplicate(items)
    assert len(unique) == 2


def test_ranker():
    """Test content ranking"""
    from filters.ranker import ContentRanker
    
    config = {
        'weights': {
            'recency': 0.3,
            'source_priority': 0.3,
            'keyword_match': 0.2,
            'engagement': 0.2
        }
    }
    
    ranker = ContentRanker(config)
    
    items = [
        {
            'title': 'Item 1',
            'source_priority': 'high',
            'keyword_score': 5,
            'points': 100
        },
        {
            'title': 'Item 2',
            'source_priority': 'low',
            'keyword_score': 1,
            'points': 10
        }
    ]
    
    ranked = ranker.rank(items)
    assert ranked[0]['title'] == 'Item 1'  # Higher score should be first


def test_cache():
    """Test caching functionality"""
    from utils.cache import Cache
    
    cache = Cache(cache_dir='data/cache', ttl_hours=24)
    
    # Set and get
    cache.set('test_key', {'data': 'test_value'})
    value = cache.get('test_key')
    
    assert value == {'data': 'test_value'}
    
    # Non-existent key
    assert cache.get('nonexistent') is None


def test_logger():
    """Test logger setup"""
    from utils.logger import setup_logger
    
    logger = setup_logger('test_logger')
    assert logger.name == 'test_logger'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
