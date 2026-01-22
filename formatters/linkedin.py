"""
LinkedIn post formatter - converts analysis to short-form posts
"""

from typing import Dict, Optional
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
    
    def format(self, item: Dict, analysis: Dict, analyzer: Optional['ContentAnalyzer'] = None) -> str:
        """
        Format item and analysis as a LinkedIn post
        
        Args:
            item: Original content item
            analysis: Analysis results from ContentAnalyzer
            analyzer: Optional pre-initialized ContentAnalyzer (for performance)
            
        Returns:
            Formatted LinkedIn post text
        """
        logger.info(f"Formatting LinkedIn post: {item.get('title')}")
        
        # Use provided analyzer or create new one
        if analyzer is None:
            from llm.analyzer import ContentAnalyzer
            analyzer = ContentAnalyzer(self.config)
        
        # Use engaging format by default (can be configured)
        use_engaging = self.config.get('use_engaging_format', True)
        linkedin_content = analyzer.generate_linkedin(analysis, use_engaging_format=use_engaging)
        
        # Run safety validation
        validation_result = analyzer.validate_linkedin_safety(linkedin_content)
        
        # If validation fails with critical issues, log warning
        if not validation_result.get('approved', True):
            critical_issues = [
                issue for issue in validation_result.get('issues', [])
                if issue.get('severity') == 'critical'
            ]
            if critical_issues:
                logger.warning(f"LinkedIn post has {len(critical_issues)} critical safety issues")
                for issue in critical_issues:
                    logger.warning(f"  - {issue.get('issue', 'Unknown issue')}")
        
        # Build complete post
        post = self._build_post(item, linkedin_content)
        
        return post
    
    def _clean_content(self, content: str) -> str:
        """Clean LinkedIn content by removing problematic elements"""
        import re
        
        # Remove agent-related phrases and meta-commentary
        agent_patterns = [
            # Agent conversation markers
            r'(?i)\b(as an ai|as a language model|i\'m an ai|i am an ai)\b[^.!?]*[.!?]',
            r'(?i)\b(i cannot|i can\'t|i don\'t have|i do not have)\b[^.!?]*[.!?]',
            r'(?i)\b(let me|i\'ll|i will|i would|i should)\b[^.!?]*[.!?]',
            r'(?i)\b(my (understanding|analysis|interpretation) is)\b[^.!?]*[.!?]',
            r'(?i)\b(based on (my|the) (analysis|understanding|interpretation))\b[^.!?]*[.!?]',
            # Meta-instructions that leak through
            r'(?i)\b(here\'s|here is) (what|how|why|a|an|the)\b',
            r'(?i)\bin (this post|this article|this summary)\b',
            r'(?i)\b(this (post|article|piece|content) (discusses|covers|explores))\b',
            # Conversational hedges
            r'(?i)\bit seems (that|like)',
            r'(?i)\bit appears (that|as if)',
            r'(?i)\bone might (say|think|argue|consider)',
            r'(?i)\bwe (might|could|should) (note|observe|consider)',
            # LLM attribution phrases
            r'(?i)\baccording to (my|the) (analysis|understanding)',
            r'(?i)\b(generated|created|written) by',
            r'(?i)\b(this was|content) (generated|created|produced)',
        ]
        
        for pattern in agent_patterns:
            content = re.sub(pattern, '', content)
        
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
        
        # Remove empty lines and fix multiple consecutive spaces
        lines = content.split('\n')
        cleaned = []
        for line in lines:
            line = ' '.join(line.split())  # Normalize whitespace
            if line.strip():  # Only keep non-empty lines
                cleaned.append(line)
        content = '\n'.join(cleaned).strip()
        
        # Remove any remaining double spaces
        content = re.sub(r'\s{2,}', ' ', content)
        
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
        
        return f"📎 Read more: {url}"
    
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
