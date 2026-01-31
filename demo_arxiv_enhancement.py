#!/usr/bin/env python
"""
Demo script to showcase ArXiv enhancement functionality
Run with: python demo_arxiv_enhancement.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from unittest.mock import patch, Mock
import json


def demo_arxiv_enhancement():
    """Demonstrate the ArXiv enhancement feature"""
    
    print("=" * 80)
    print("ArXiv Paper Enhancement Demo")
    print("=" * 80)
    print()
    
    # Sample arXiv papers - one relevant, one not
    papers = [
        {
            'id': 'arXiv:2410.08003',
            'title': 'Attention Is All You Need',
            'url': 'https://arxiv.org/abs/2410.08003',
            'summary': 'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable.',
            'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
            'category': 'cs.LG',
            'source': 'arxiv'
        },
        {
            'id': 'arXiv:2410.99999',
            'title': 'Advanced Theoretical Constructs in Abstract Algebra',
            'url': 'https://arxiv.org/abs/2410.99999',
            'summary': 'We present new theoretical results in algebraic topology with applications to differential geometry. The proofs rely on advanced category theory.',
            'authors': ['Pure Mathematician'],
            'category': 'math.AG',
            'source': 'arxiv'
        }
    ]
    
    # Mock the Perplexity API client
    with patch('llm.client.PerplexityClient') as mock_client_class:
        mock_client = Mock()
        
        # Setup mock responses
        responses = [
            # Paper 1 - Relevant
            "Transformers revolutionize sequence modeling by using only attention mechanisms, eliminating recurrence entirely.",
            "ML engineers building NLP systems because it provides better parallelization and performance than RNNs.",
            "Score: 9.5\nReason: Foundational architecture that transformed NLP and is widely adopted in production systems.",
            # Standard analysis
            "Key innovation: Self-attention replaces recurrent layers...",
            "Technical summary: Architecture uses stacked attention layers...",
            "Industry impact: Enables modern LLMs like GPT and BERT...",
            "Applications: Machine translation, text generation, language understanding...",
            # Paper 2 - Not Relevant
            "Abstract mathematical proofs with limited computational applications.",
            "Pure mathematics researchers studying theoretical foundations.",
            "Score: 2.0\nReason: Too theoretical with no direct ML applications.",
        ]
        
        mock_client.generate.side_effect = responses
        mock_client_class.return_value = mock_client
        
        # Import after mocking
        from llm.analyzer import ContentAnalyzer
        
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
        
        # Process each paper
        for i, paper in enumerate(papers, 1):
            print(f"\n📄 Paper {i}: {paper['title']}")
            print(f"📎 URL: {paper['url']}")
            print(f"📂 Category: {paper['category']}")
            print("-" * 80)
            
            # Analyze with enhancement
            analysis = analyzer.analyze_arxiv(paper)
            
            if analysis is None:
                print("❌ SKIPPED - Paper not relevant for ML practitioners")
                print()
                continue
            
            # Paper was relevant - show enhancement details
            enhancement = analysis['arxiv_enhancement']
            
            print("✅ APPROVED - Paper passes relevancy check")
            print()
            print(f"📊 Relevancy Score: {enhancement['relevancy_score']:.1f}/10")
            print(f"💭 Reason: {enhancement['relevancy_reason']}")
            print()
            print(f"📝 Enhanced Summary:")
            print(f"   {enhancement['enhanced_summary']}")
            print()
            print(f"💡 Verdict:")
            print(f"   {enhancement['verdict']}")
            print()
            
            # Show what the LinkedIn post would look like
            print("📱 LinkedIn Post Preview:")
            print("-" * 80)
            post_content = f"""📄 New Research: {paper['title']}

{enhancement['enhanced_summary']}

💡 {enhancement['verdict']}

📎 Read more: {paper['url']}

#AI #MachineLearning #Research #DeepLearning"""
            print(post_content)
            print("-" * 80)
            print()
    
    print("=" * 80)
    print("Demo Complete!")
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Engaging summaries that explain papers simply")
    print("  ✓ Verdicts on practical usefulness")
    print("  ✓ Relevancy scoring to filter out non-relevant papers")
    print("  ✓ Enhanced LinkedIn posts instead of just links")
    print("=" * 80)


if __name__ == '__main__':
    demo_arxiv_enhancement()
