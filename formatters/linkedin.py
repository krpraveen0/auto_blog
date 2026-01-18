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
    
    def _clean_content(self, content: str) -> str:
        """Clean LinkedIn content by removing problematic elements"""
        import re
        
        # Remove citation markers like [1], [2], [3], etc.
        content = re.sub(r'\[\d+\]', '', content)
        
        # Remove invalid hashtags like "hashtag#Word" - convert to plain text
        content = re.sub(r'hashtag(#\w+)', r'\1', content)
        
        # Remove markdown formatting
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # **bold** -> bold
        content = re.sub(r'\*(.+?)\*', r'\1', content)      # *italic* -> italic
        content = re.sub(r'__(.+?)__', r'\1', content)       # __bold__ -> bold
        content = re.sub(r'_(.+?)_', r'\1', content)         # _italic_ -> italic
        
        # Remove lines that are only hashtags
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # If line is just hashtags, remove it
            stripped = line.strip()
            if stripped and all(word.startswith('#') for word in stripped.split()):
                continue
            cleaned_lines.append(line)
        content = '\n'.join(cleaned_lines)
        
        # Remove trailing filler words
        trailing_words = ['like', 'interesting', 'exciting', 'amazing', 'fantastic', 'great']
        for word in trailing_words:
            pattern = rf'\b{word}\s*\.?\s*$'
            content = re.sub(pattern, '.', content, flags=re.IGNORECASE)
        
        # Clean up extra whitespace while preserving line breaks
        lines = content.split('\n')
        cleaned = [' '.join(line.split()) for line in lines]
        content = '\n'.join(cleaned).strip()
        
        return content
    
    def _build_post(self, item: Dict, content: str) -> str:
        """Build complete LinkedIn post"""
        
        # Clean content first
        content = self._clean_content(content)
        
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
