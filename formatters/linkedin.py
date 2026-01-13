"""
LinkedIn post formatter - converts analysis to short-form posts
"""

from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LinkedInFormatter:
    """Format content analysis as LinkedIn posts"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_words = config.get('max_words', 120)
        self.bullet_points = config.get('bullet_points', 3)
        self.hashtag_count = config.get('hashtag_count', 4)
        self.use_emojis = config.get('emojis', False)
    
    def format(self, item: Dict, analysis: Dict) -> str:
        """
        Format item and analysis as a LinkedIn post
        
        Args:
            item: Original content item
            analysis: Analysis results from ContentAnalyzer
            
        Returns:
            Formatted LinkedIn post text
        """
        logger.info(f"Formatting LinkedIn post: {item.get('title')}")
        
        # Generate LinkedIn content from analysis
        from llm.analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer(self.config)
        linkedin_content = analyzer.generate_linkedin(analysis)
        
        # Add source link
        post = self._build_post(item, linkedin_content)
        
        return post
    
    def _build_post(self, item: Dict, content: str) -> str:
        """Build complete LinkedIn post"""
        
        parts = [
            content,
            "",
            self._generate_source_link(item),
            "",
            self._generate_hashtags(item)
        ]
        
        return '\n'.join(parts)
    
    def _generate_source_link(self, item: Dict) -> str:
        """Generate source attribution link"""
        url = item.get('url', '')
        source = item.get('source_name', item.get('source', 'Source'))
        
        return f"📎 Read more: {url}\nvia {source}"
    
    def _generate_hashtags(self, item: Dict) -> str:
        """Generate relevant hashtags"""
        hashtags = set()
        
        # Core AI/ML tags
        hashtags.add('#AI')
        hashtags.add('#MachineLearning')
        
        # Source-specific tags
        source = item.get('source', '')
        if 'arxiv' in source:
            hashtags.add('#Research')
            hashtags.add('#DeepLearning')
        elif 'github' in source:
            hashtags.add('#OpenSource')
            hashtags.add('#MLOps')
        elif 'blog' in source:
            if 'openai' in source:
                hashtags.add('#LLM')
                hashtags.add('#GPT')
            elif 'deepmind' in source or 'google' in source:
                hashtags.add('#GoogleAI')
            elif 'meta' in source:
                hashtags.add('#MetaAI')
            elif 'anthropic' in source:
                hashtags.add('#Claude')
            else:
                hashtags.add('#GenAI')
        
        # From item category/topics
        if item.get('category'):
            cat = item['category'].replace('cs.', '').upper()
            if cat == 'CL':
                hashtags.add('#NLP')
            elif cat == 'CV':
                hashtags.add('#ComputerVision')
        
        # Limit to configured count
        hashtag_list = sorted(list(hashtags))[:self.hashtag_count]
        
        return ' '.join(hashtag_list)
