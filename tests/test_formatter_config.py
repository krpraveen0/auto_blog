"""
Test formatter configuration fixes
"""

from formatters.blog import BlogFormatter
from formatters.linkedin import LinkedInFormatter
from formatters.medium import MediumFormatter


def test_blog_formatter_with_llm_config():
    """Test that BlogFormatter accepts llm_config parameter"""
    formatter_config = {
        'target_words': 900,
        'tone': 'analytical',
        'include_references': True
    }
    
    llm_config = {
        'provider': 'perplexity',
        'model': 'sonar-pro',
        'profanity_list': ['test']
    }
    
    # Should not raise an error
    formatter = BlogFormatter(formatter_config, llm_config=llm_config)
    
    assert formatter.config == formatter_config
    assert formatter.llm_config == llm_config
    assert formatter.target_words == 900


def test_blog_formatter_without_llm_config():
    """Test that BlogFormatter works without llm_config (backward compatibility)"""
    formatter_config = {
        'target_words': 800,
        'tone': 'technical'
    }
    
    # Should not raise an error
    formatter = BlogFormatter(formatter_config)
    
    assert formatter.config == formatter_config
    assert formatter.llm_config is None
    assert formatter.target_words == 800


def test_linkedin_formatter_with_llm_config():
    """Test that LinkedInFormatter accepts llm_config parameter"""
    formatter_config = {
        'max_words': 120,
        'bullet_points': 3,
        'hashtag_count': 4
    }
    
    llm_config = {
        'provider': 'perplexity',
        'model': 'sonar-pro'
    }
    
    # Should not raise an error
    formatter = LinkedInFormatter(formatter_config, llm_config=llm_config)
    
    assert formatter.config == formatter_config
    assert formatter.llm_config == llm_config
    assert formatter.max_words == 120


def test_linkedin_formatter_without_llm_config():
    """Test that LinkedInFormatter works without llm_config"""
    formatter_config = {
        'max_words': 150,
        'emojis': True
    }
    
    # Should not raise an error
    formatter = LinkedInFormatter(formatter_config)
    
    assert formatter.config == formatter_config
    assert formatter.llm_config is None


def test_medium_formatter_with_llm_config():
    """Test that MediumFormatter accepts llm_config parameter"""
    formatter_config = {
        'target_words': 2000,
        'include_diagrams': True
    }
    
    llm_config = {
        'provider': 'perplexity',
        'model': 'sonar-pro'
    }
    
    # Should not raise an error
    formatter = MediumFormatter(formatter_config, llm_config=llm_config)
    
    assert formatter.config == formatter_config
    assert formatter.llm_config == llm_config
    assert formatter.target_words == 2000


def test_medium_formatter_without_llm_config():
    """Test that MediumFormatter works without llm_config"""
    formatter_config = {
        'target_words': 1500
    }
    
    # Should not raise an error
    formatter = MediumFormatter(formatter_config)
    
    assert formatter.config == formatter_config
    assert formatter.llm_config is None
