"""
Blog article formatter - converts analysis to markdown blog posts
"""

from datetime import datetime
from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BlogFormatter:
    """Format content analysis as blog articles"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.target_words = config.get('target_words', 900)
        self.tone = config.get('tone', 'analytical')
        self.include_references = config.get('include_references', True)
    
    def format(self, item: Dict, analysis: Dict) -> str:
        """
        Format item and analysis as a blog article
        
        Args:
            item: Original content item
            analysis: Analysis results from ContentAnalyzer
            
        Returns:
            Formatted markdown blog post
        """
        logger.info(f"Formatting blog article: {item.get('title')}")
        
        # Generate blog content from analysis
        from llm.analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer(self.config)
        blog_content = analyzer.generate_blog(analysis)
        
        # Build markdown post with frontmatter
        post = self._build_post(item, analysis, blog_content)
        
        return post
    
    def _build_post(self, item: Dict, analysis: Dict, content: str) -> str:
        """Build complete markdown post with frontmatter"""
        
        # YAML frontmatter for Jekyll/Hugo
        frontmatter = self._generate_frontmatter(item, analysis)
        
        # Add source attribution
        source_section = self._generate_source_section(item)
        
        # Combine all parts
        parts = [
            frontmatter,
            "",  # Blank line after frontmatter
            content,
            "",
            "---",
            "",
            source_section
        ]
        
        return '\n'.join(parts)
    
    def _generate_frontmatter(self, item: Dict, analysis: Dict) -> str:
        """Generate YAML frontmatter"""
        title = item.get('title', 'Untitled')
        date = datetime.now().strftime('%Y-%m-%d')
        
        # Extract tags from source and analysis
        tags = self._extract_tags(item, analysis)
        tags_yaml = '\n  - '.join(tags)
        
        frontmatter = f"""---
layout: post
title: "{title}"
date: {date}
categories: [AI, Research]
tags:
  - {tags_yaml}
author: AI Research Publisher
source: {item.get('source', 'unknown')}
source_url: {item.get('url', '')}
---"""
        
        return frontmatter
    
    def _extract_tags(self, item: Dict, analysis: Dict) -> list:
        """Extract relevant tags"""
        tags = set()
        
        # From source
        if item.get('category'):
            tags.add(item['category'].replace('cs.', '').upper())
        
        if item.get('topics'):
            topics = item['topics'] if isinstance(item['topics'], list) else [item['topics']]
            tags.update(topics[:3])  # Max 3 topic tags
        
        # From source type
        source = item.get('source', '')
        if 'arxiv' in source:
            tags.add('Research')
        elif 'github' in source:
            tags.add('Open Source')
        elif 'blog' in source:
            tags.add('Industry')
        
        # Default tags
        tags.add('Machine Learning')
        
        return sorted(list(tags))[:6]  # Max 6 tags
    
    def _generate_source_section(self, item: Dict) -> str:
        """Generate source attribution section"""
        
        source_name = item.get('source_name', item.get('source', 'Unknown'))
        url = item.get('url', '')
        
        section = f"""## Source

**Original Publication:** [{source_name}]({url})"""
        
        if item.get('authors'):
            authors = ', '.join(item['authors']) if isinstance(item['authors'], list) else item['authors']
            section += f"\n**Authors:** {authors}"
        
        if item.get('published'):
            section += f"\n**Published:** {item['published']}"
        
        section += "\n\n*This article was automatically generated using AI analysis. Please refer to the original source for complete details.*"
        
        return section
