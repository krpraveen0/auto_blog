"""
Integration test for ArXiv enhancement
Tests the full flow without requiring API keys
"""

import pytest
from unittest.mock import patch, Mock
from pathlib import Path
import json


def test_arxiv_enhancement_integration():
    """Test full arxiv enhancement integration with mocked API"""
    
    # Sample arXiv paper
    arxiv_paper = {
        'id': 'arXiv:2410.08003',
        'title': 'Attention Is All You Need',
        'url': 'https://arxiv.org/abs/2410.08003',
        'pdf_url': 'https://arxiv.org/pdf/2410.08003.pdf',
        'summary': 'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.',
        'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
        'published': '2023-10-01T00:00:00',
        'category': 'cs.LG',
        'categories': ['cs.LG', 'cs.AI'],
        'primary_category': 'cs.LG',
        'source': 'arxiv'
    }
    
    # Mock Perplexity client at the right level
    with patch('llm.arxiv_enhancer.PerplexityClient') as mock_enhancer_client, \
         patch('llm.analyzer.PerplexityClient') as mock_analyzer_client:
        mock_client = Mock()
        
        # Mock responses for different stages
        mock_client.generate.side_effect = [
            # Enhanced summary
            "Transformers revolutionize NLP by using pure attention mechanisms instead of recurrence.",
            # Verdict
            "ML engineers building sequence models because it eliminates RNN complexity.",
            # Relevancy check
            "Score: 9.5\nReason: Foundational architecture that transformed NLP and ML.",
            # Standard analysis stages
            "Key facts: Novel transformer architecture...",
            "Engineer summary: Self-attention replaces recurrence...",
            "Impact: Major breakthrough in sequence modeling...",
            "Applications: Machine translation, text generation...",
        ]
        mock_enhancer_client.return_value = mock_client
        mock_analyzer_client.return_value = mock_client
        
        # Import after mocking
        from llm.analyzer import ContentAnalyzer
        
        # Create analyzer with test config
        config = {
            'provider': 'perplexity',
            'model': 'sonar-pro',
            'arxiv_relevancy_threshold': 6.0,
            'prompt_stages': [
                'fact_extraction',
                'engineer_summary',
                'impact_analysis',
                'application_mapping'
            ]
        }
        
        analyzer = ContentAnalyzer(config)
        
        # Run arxiv-enhanced analysis
        analysis = analyzer.analyze_arxiv(arxiv_paper)
        
        # Verify analysis was successful
        assert analysis is not None, "Paper should be relevant and return analysis"
        
        # Check arxiv enhancement is present
        assert 'arxiv_enhancement' in analysis
        enhancement = analysis['arxiv_enhancement']
        
        # Verify enhancement structure
        assert 'enhanced_summary' in enhancement
        assert 'verdict' in enhancement
        assert 'relevancy_score' in enhancement
        assert 'relevancy_reason' in enhancement
        assert 'is_relevant' in enhancement
        
        # Verify relevancy check worked
        assert enhancement['is_relevant'] is True
        assert enhancement['relevancy_score'] >= 6.0
        
        # Verify enhanced summary
        assert len(enhancement['enhanced_summary']) > 0
        assert 'Transformers' in enhancement['enhanced_summary']
        
        # Verify verdict format
        assert enhancement['verdict'].startswith('Useful for')
        
        print(f"\n✅ Enhanced Summary: {enhancement['enhanced_summary']}")
        print(f"💡 Verdict: {enhancement['verdict']}")
        print(f"📊 Relevancy: {enhancement['relevancy_score']}/10 - {enhancement['relevancy_reason']}")


def test_arxiv_enhancement_skip_irrelevant():
    """Test that irrelevant papers are skipped"""
    
    # Sample irrelevant arXiv paper
    arxiv_paper = {
        'id': 'arXiv:2410.99999',
        'title': 'Advanced Theoretical Constructs in Pure Mathematics',
        'url': 'https://arxiv.org/abs/2410.99999',
        'summary': 'Highly abstract mathematical proofs with no practical applications.',
        'authors': ['Theoretical Researcher'],
        'published': '2023-10-01T00:00:00',
        'category': 'math.AG',
        'source': 'arxiv'
    }
    
    # Mock Perplexity client at the right level
    with patch('llm.arxiv_enhancer.PerplexityClient') as mock_enhancer_client, \
         patch('llm.analyzer.PerplexityClient') as mock_analyzer_client:
        mock_client = Mock()
        
        # Mock responses indicating low relevancy
        mock_client.generate.side_effect = [
            # Enhanced summary
            "Complex mathematical proofs with limited ML applicability.",
            # Verdict
            "Pure mathematics researchers studying abstract algebra.",
            # Relevancy check - LOW SCORE
            "Score: 2.0\nReason: Too theoretical, not applicable to ML practitioners.",
        ]
        mock_enhancer_client.return_value = mock_client
        mock_analyzer_client.return_value = mock_client
        
        # Import after mocking
        from llm.analyzer import ContentAnalyzer
        
        # Create analyzer
        config = {
            'provider': 'perplexity',
            'model': 'sonar-pro',
            'arxiv_relevancy_threshold': 6.0,
            'prompt_stages': ['fact_extraction']
        }
        
        analyzer = ContentAnalyzer(config)
        
        # Run arxiv-enhanced analysis
        analysis = analyzer.analyze_arxiv(arxiv_paper)
        
        # Verify paper was skipped
        assert analysis is None, "Irrelevant paper should return None"
        
        print("\n⏭️  Paper correctly skipped due to low relevancy")


def test_linkedin_formatting_with_enhancement():
    """Test LinkedIn formatting uses enhanced content"""
    
    # Sample paper with enhancement
    paper = {
        'id': 'arXiv:2410.08003',
        'title': 'Attention Is All You Need',
        'url': 'https://arxiv.org/abs/2410.08003',
        'source': 'arxiv',
        'category': 'cs.LG'
    }
    
    analysis = {
        'title': 'Attention Is All You Need',
        'arxiv_enhancement': {
            'enhanced_summary': 'Transformers revolutionize NLP by using pure attention instead of recurrence.',
            'verdict': 'Useful for ML engineers building sequence models because it eliminates RNN complexity.',
            'relevancy_score': 9.5,
            'is_relevant': True
        }
    }
    
    # Mock everything
    with patch('llm.arxiv_enhancer.PerplexityClient'), \
         patch('llm.analyzer.PerplexityClient'):
        from formatters.linkedin import LinkedInFormatter
        
        config = {
            'max_words': 150,
            'bullet_points': 3,
            'hashtag_count': 4,
            'use_engaging_format': True
        }
        
        formatter = LinkedInFormatter(config, llm_config={'provider': 'perplexity'})
        
        # Format post
        post = formatter.format(paper, analysis)
        
        # Verify post contains enhanced content
        assert 'Transformers' in post
        assert 'Useful for' in post
        assert '#Research' in post
        assert paper['url'] in post
        
        print(f"\n📱 LinkedIn Post Preview:")
        print("=" * 60)
        print(post)
        print("=" * 60)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
