"""
LinkedIn post formatter - converts analysis to short-form posts
"""

from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LinkedInFormatter:
    """Format content analysis as LinkedIn posts"""
    
    def __init__(self, config: Dict, llm_config: Dict = None):
        """
        Initialize LinkedIn formatter
        
        Args:
            config: Formatting configuration
            llm_config: LLM configuration (required for ContentAnalyzer)
        """
        self.config = config
        self.llm_config = llm_config
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
            # Use LLM config if provided, otherwise fallback to formatter config
            analyzer_config = self.llm_config if self.llm_config else self.config
            analyzer = ContentAnalyzer(analyzer_config)
        
        # For arXiv papers with enhancement, use enhanced content directly
        if item.get('source') == 'arxiv' and analysis.get('arxiv_enhancement'):
            enhancement = analysis['arxiv_enhancement']
            # Create content from enhanced summary and verdict
            linkedin_content = self._format_arxiv_enhanced(
                item, 
                enhancement.get('enhanced_summary', ''),
                enhancement.get('verdict', '')
            )
        else:
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
        # Enhanced patterns to catch AI-generated content markers
        agent_patterns = [
            # Agent conversation markers - full sentence patterns
            r'(?i)\b(as an ai|as a language model|i\'m an ai|i am an ai)\b[^.!?]*[.!?]',
            r'(?i)\b(i cannot|i can\'t|i don\'t have|i do not have)\b[^.!?]*[.!?]',
            # Meta-announcements (most common AI pattern)
            r'(?i)^here\'s\s+(what|how|why|a|an)\s+',
            r'(?i)^here is\s+(what|how|why|a|an)\s+',
            r'(?i)^let me (share|tell|show|explain)\s+',
            r'(?i)^i want to (share|tell|show|explain)\s+',
            r'(?i)^i\'m (excited|thrilled|pleased) to (share|announce)\s+',
            r'(?i)^check out\s+',
            r'(?i)^today,?\s+i\'m sharing\s+',
            # Post self-reference
            r'(?i)\bin (this post|this article|this summary|today\'s post),?\s+(we|I)\b[^.!?]*[.!?]',
            r'(?i)\b(this (post|article|piece|content) (discusses|covers|explores|examines))\b[^.!?]*[.!?]',
            # Conversational hedges that sound like AI explanations
            r'(?i)\bit seems (that|like)[^.!?]*[.!?]',
            r'(?i)\bit appears (that|as if)[^.!?]*[.!?]',
            r'(?i)\bone might (say|think|argue|consider) that\b[^.!?]*[.!?]',
            r'(?i)\bwe (might|could|should) (note|observe|consider) that\b[^.!?]*[.!?]',
            # LLM attribution phrases
            r'(?i)\baccording to (my|the) (analysis|understanding)\b[^.!?]*[.!?]',
            r'(?i)\bbased on (my|the) (analysis|understanding|interpretation)\b[^.!?]*[.!?]',
            r'(?i)\b(generated|created|written) by (an ai|ai|a language model)\b',
            r'(?i)\b(this was|content) (generated|created|produced) (by|using)\b',
            # Analysis/interpretation qualifiers
            r'(?i)\bmy (understanding|analysis|interpretation) is\b[^.!?]*[.!?]',
            r'(?i)\bin my (view|opinion|experience|analysis)\b[^.!?]*[.!?]',
            # Hype and buzzwords that sound promotional/AI-generated
            r'(?i)\b(game-changing|revolutionary|groundbreaking|paradigm-shifting)\b',
            r'(?i)\b(exciting|amazing|incredible|fantastic) (news|discovery|breakthrough)\b',
            # Common AI filler patterns
            r'(?i)\binterestingly enough,?\s+',
            r'(?i)\bit\'s worth (noting|mentioning) that\s+',
            r'(?i)\bone of the (most|key) (interesting|important) (things|aspects|points) is\s+',
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
        
        # Remove trailing filler words and phrases
        trailing_patterns = [
            r'\b(like|interesting|exciting|amazing|fantastic|great)\s*\.?\s*$',
            r'\bthoughts\?\s*$',
            r'\bwhat do you think\?\s*$',
            r'\bagree\?\s*$',
        ]
        for pattern in trailing_patterns:
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
        
        # Clean up leading/trailing punctuation artifacts
        content = re.sub(r'\s*[,;]\s*\.', '.', content)  # Fix ", ." -> "."
        content = re.sub(r'^\s*[,;]\s*', '', content, flags=re.MULTILINE)  # Remove leading commas
        
        # Fix sentences that start with lowercase after cleaning
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].islower():
                line = stripped[0].upper() + stripped[1:]
            fixed_lines.append(line)
        content = '\n'.join(fixed_lines)
        
        return content
    
    def _format_arxiv_enhanced(self, item: Dict, summary: str, verdict: str) -> str:
        """
        Format arXiv paper with enhanced summary and verdict
        
        Args:
            item: arXiv paper dictionary
            summary: Enhanced engaging summary
            verdict: Verdict on usefulness
            
        Returns:
            Formatted LinkedIn content
        """
        # Build engaging post from enhanced content
        parts = []
        
        # Add title context
        title = item.get('title', '')
        if title:
            parts.append(f"📄 New Research: {title}")
            parts.append("")
        
        # Add enhanced summary
        if summary:
            parts.append(summary)
            parts.append("")
        
        # Add verdict with emoji
        if verdict:
            parts.append(f"💡 {verdict}")
        
        content = '\n'.join(parts)
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
