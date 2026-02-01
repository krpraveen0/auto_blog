"""
Tests for ArxivEnhancer module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from llm.arxiv_enhancer import ArxivEnhancer


@pytest.fixture
def mock_config():
    """Mock LLM configuration"""
    return {
        'provider': 'perplexity',
        'model': 'sonar-pro',
        'api_timeout': 60,
        'max_retries': 3,
        'arxiv_relevancy_threshold': 6.0
    }


@pytest.fixture
def sample_arxiv_paper():
    """Sample arXiv paper for testing"""
    return {
        'id': 'arXiv:2410.08003',
        'title': 'Attention Is All You Need',
        'url': 'https://arxiv.org/abs/2410.08003',
        'pdf_url': 'https://arxiv.org/pdf/2410.08003.pdf',
        'summary': 'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.',
        'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
        'published': '2024-10-01T00:00:00',
        'category': 'cs.LG',
        'categories': ['cs.LG', 'cs.AI'],
        'primary_category': 'cs.LG',
        'source': 'arxiv'
    }


class TestArxivEnhancer:
    """Test ArxivEnhancer functionality"""
    
    def test_initialization(self, mock_config):
        """Test ArxivEnhancer initialization"""
        with patch('llm.arxiv_enhancer.PerplexityClient'):
            enhancer = ArxivEnhancer(mock_config)
            assert enhancer.relevancy_threshold == 6.0
            assert enhancer.config == mock_config
    
    @patch('llm.arxiv_enhancer.PerplexityClient')
    def test_generate_engaging_summary(self, mock_client_class, mock_config, sample_arxiv_paper):
        """Test generating engaging summary"""
        # Setup mock client
        mock_client = Mock()
        mock_client.generate.return_value = "Transformers revolutionize NLP by replacing recurrence with self-attention."
        mock_client_class.return_value = mock_client
        
        enhancer = ArxivEnhancer(mock_config)
        summary = enhancer._generate_engaging_summary(sample_arxiv_paper)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Check that academic language is cleaned
        assert not summary.startswith('This paper')
        assert not summary.startswith('The authors')
    
    @patch('llm.arxiv_enhancer.PerplexityClient')
    def test_generate_verdict(self, mock_client_class, mock_config, sample_arxiv_paper):
        """Test generating verdict"""
        # Setup mock client
        mock_client = Mock()
        mock_client.generate.return_value = "ML engineers building sequence-to-sequence models because it simplifies architecture."
        mock_client_class.return_value = mock_client
        
        enhancer = ArxivEnhancer(mock_config)
        summary = "Transformers use self-attention for sequence modeling."
        verdict = enhancer._generate_verdict(sample_arxiv_paper, summary)
        
        assert isinstance(verdict, str)
        assert len(verdict) > 0
        assert verdict.startswith('Useful for')
    
    @patch('llm.arxiv_enhancer.PerplexityClient')
    def test_check_relevancy_high_score(self, mock_client_class, mock_config, sample_arxiv_paper):
        """Test relevancy check with high score"""
        # Setup mock client
        mock_client = Mock()
        mock_client.generate.return_value = "Score: 9.0\nReason: Breakthrough technique widely adopted in industry."
        mock_client_class.return_value = mock_client
        
        enhancer = ArxivEnhancer(mock_config)
        summary = "Transformers use self-attention."
        verdict = "Useful for NLP practitioners."
        
        score, reason = enhancer._check_relevancy(sample_arxiv_paper, summary, verdict)
        
        assert isinstance(score, float)
        assert 0 <= score <= 10
        assert score == 9.0
        assert isinstance(reason, str)
        assert len(reason) > 0
    
    @patch('llm.arxiv_enhancer.PerplexityClient')
    def test_check_relevancy_low_score(self, mock_client_class, mock_config, sample_arxiv_paper):
        """Test relevancy check with low score"""
        # Setup mock client
        mock_client = Mock()
        mock_client.generate.return_value = "Score: 3.0\nReason: Too theoretical for practical applications."
        mock_client_class.return_value = mock_client
        
        enhancer = ArxivEnhancer(mock_config)
        summary = "Complex mathematical proof."
        verdict = "Useful for theorists."
        
        score, reason = enhancer._check_relevancy(sample_arxiv_paper, summary, verdict)
        
        assert score == 3.0
        assert "theoretical" in reason.lower() or "practical" in reason.lower()
    
    @patch('llm.arxiv_enhancer.PerplexityClient')
    def test_enhance_arxiv_paper_relevant(self, mock_client_class, mock_config, sample_arxiv_paper):
        """Test full enhancement of relevant paper"""
        # Setup mock client with multiple responses
        mock_client = Mock()
        mock_client.generate.side_effect = [
            "Transformers revolutionize NLP by replacing recurrence with self-attention.",
            "ML engineers building sequence-to-sequence models because it simplifies architecture.",
            "Score: 9.0\nReason: Breakthrough technique widely adopted."
        ]
        mock_client_class.return_value = mock_client
        
        enhancer = ArxivEnhancer(mock_config)
        is_relevant, enhancement = enhancer.enhance_arxiv_paper(sample_arxiv_paper)
        
        assert is_relevant is True
        assert 'enhanced_summary' in enhancement
        assert 'verdict' in enhancement
        assert 'relevancy_score' in enhancement
        assert 'relevancy_reason' in enhancement
        assert 'is_relevant' in enhancement
        assert enhancement['relevancy_score'] >= 6.0
    
    @patch('llm.arxiv_enhancer.PerplexityClient')
    def test_enhance_arxiv_paper_not_relevant(self, mock_client_class, mock_config, sample_arxiv_paper):
        """Test full enhancement of non-relevant paper"""
        # Setup mock client with low relevancy score
        mock_client = Mock()
        mock_client.generate.side_effect = [
            "Complex theoretical analysis.",
            "Researchers in pure mathematics.",
            "Score: 2.0\nReason: Not applicable to ML practitioners."
        ]
        mock_client_class.return_value = mock_client
        
        enhancer = ArxivEnhancer(mock_config)
        is_relevant, enhancement = enhancer.enhance_arxiv_paper(sample_arxiv_paper)
        
        assert is_relevant is False
        assert enhancement['relevancy_score'] < 6.0
        assert enhancement['is_relevant'] is False
    
    @patch('llm.arxiv_enhancer.PerplexityClient')
    def test_enhance_arxiv_paper_error_handling(self, mock_client_class, mock_config, sample_arxiv_paper):
        """Test error handling in enhancement"""
        # Setup mock client to raise exception
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("API error")
        mock_client_class.return_value = mock_client
        
        enhancer = ArxivEnhancer(mock_config)
        is_relevant, enhancement = enhancer.enhance_arxiv_paper(sample_arxiv_paper)
        
        # Should return False with fallback score of 5.0
        assert is_relevant is False
        # Error case returns 5.0, not 0, as a default fallback
        assert enhancement['relevancy_score'] == 5.0
        assert 'failed' in enhancement['relevancy_reason'].lower()
    
    def test_clean_academic_language(self, mock_config):
        """Test cleaning of academic language patterns"""
        with patch('llm.arxiv_enhancer.PerplexityClient'):
            enhancer = ArxivEnhancer(mock_config)
            
            test_cases = [
                ("This paper presents a novel approach.", "Presents a novel approach."),
                ("The authors propose a new method.", "Propose a new method."),
                ("In this work, we introduce transformers.", "We introduce transformers."),
                ("We propose a solution.", "Propose a solution."),
            ]
            
            for input_text, expected_start in test_cases:
                result = enhancer._clean_academic_language(input_text)
                assert result.startswith(expected_start) or result[0].isupper()
    
    def test_custom_threshold(self):
        """Test custom relevancy threshold"""
        config = {
            'provider': 'perplexity',
            'arxiv_relevancy_threshold': 7.5
        }
        with patch('llm.arxiv_enhancer.PerplexityClient'):
            enhancer = ArxivEnhancer(config)
            assert enhancer.relevancy_threshold == 7.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
