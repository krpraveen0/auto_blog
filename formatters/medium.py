"""
Medium formatter - Generates comprehensive blog posts with diagrams
Specifically designed for detailed ArXiv paper explanations
"""

from pathlib import Path
from typing import Dict
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MediumFormatter:
    """Format content for Medium with comprehensive paper analysis and diagrams"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.target_words = config.get('target_words', 2000)  # Longer for comprehensive analysis
        self.include_diagrams = config.get('include_diagrams', True)
        self.include_references = config.get('include_references', True)
    
    def format(self, item: Dict, analysis: Dict) -> str:
        """
        Format item and analysis into comprehensive Medium article with diagrams
        
        Args:
            item: Source item data
            analysis: LLM analysis results from 7-stage pipeline + diagram generation
            
        Returns:
            Formatted markdown article
        """
        # Extract components
        title = item.get('title', 'Untitled')
        source = item.get('source', 'unknown')
        url = item.get('url', '')
        
        # Get analysis stages
        summary = analysis.get('engineer_summary', '')
        impact = analysis.get('impact_analysis', '')
        applications = analysis.get('application_mapping', '')
        blog_content = analysis.get('medium_synthesis', analysis.get('blog_synthesis', ''))
        
        # Get diagram content if available
        diagrams = analysis.get('diagrams', {})
        architecture_diagram = diagrams.get('architecture', '')
        flow_diagram = diagrams.get('flow', '')
        comparison_diagram = diagrams.get('comparison', '')
        
        # Get comprehensive sections
        methodology = analysis.get('methodology', '')
        results = analysis.get('results', '')
        implications = analysis.get('detailed_implications', '')
        
        # Build article
        article = self._build_article(
            title=title,
            summary=summary,
            blog_content=blog_content,
            methodology=methodology,
            results=results,
            impact=impact,
            implications=implications,
            applications=applications,
            architecture_diagram=architecture_diagram,
            flow_diagram=flow_diagram,
            comparison_diagram=comparison_diagram,
            source=source,
            url=url,
            item=item
        )
        
        return article
    
    def _build_article(
        self,
        title: str,
        summary: str,
        blog_content: str,
        methodology: str,
        results: str,
        impact: str,
        implications: str,
        applications: str,
        architecture_diagram: str,
        flow_diagram: str,
        comparison_diagram: str,
        source: str,
        url: str,
        item: Dict
    ) -> str:
        """Build comprehensive article with all sections"""
        
        # Extract tags from item
        tags = self._extract_tags(item)
        
        # Build YAML frontmatter
        frontmatter = f"""---
title: "{title}"
date: {datetime.now().isoformat()}
tags: {tags}
source: {source}
canonical_url: {url}
---

"""
        
        # Build article body
        body = f"""# {title}

## Executive Summary

{summary}

"""
        
        # Add architecture diagram if available
        if architecture_diagram:
            body += f"""## System Architecture

The following diagram illustrates the key components and their relationships:

```mermaid
{architecture_diagram}
```

"""
        
        # Add main content
        if blog_content:
            body += f"""{blog_content}

"""
        
        # Add methodology section if available
        if methodology:
            body += f"""## Methodology Deep Dive

{methodology}

"""
        
        # Add flow diagram if available
        if flow_diagram:
            body += f"""## Process Flow

```mermaid
{flow_diagram}
```

"""
        
        # Add results section if available
        if results:
            body += f"""## Results & Findings

{results}

"""
        
        # Add comparison diagram if available
        if comparison_diagram:
            body += f"""## Comparative Analysis

```mermaid
{comparison_diagram}
```

"""
        
        # Add impact analysis
        if impact:
            body += f"""## Impact Analysis

{impact}

"""
        
        # Add detailed implications
        if implications:
            body += f"""## Detailed Implications

{implications}

"""
        
        # Add applications
        if applications:
            body += f"""## Real-World Applications

{applications}

"""
        
        # Add references section
        if self.include_references:
            body += self._build_references(item, url)
        
        # Add footer
        body += self._build_footer()
        
        return frontmatter + body
    
    def _extract_tags(self, item: Dict) -> list:
        """Extract relevant tags from item"""
        tags = []
        
        # Add source-based tags
        source = item.get('source', '')
        if source == 'arxiv':
            tags.append('Research Paper')
            tags.append('ArXiv')
        
        # Add category-based tags
        categories = item.get('categories', [])
        if categories:
            if 'cs.AI' in categories:
                tags.append('Artificial Intelligence')
            if 'cs.LG' in categories:
                tags.append('Machine Learning')
            if 'cs.CL' in categories:
                tags.append('NLP')
            if 'cs.CV' in categories:
                tags.append('Computer Vision')
        
        # Add general tags
        tags.extend(['AI Research', 'Deep Learning'])
        
        # Return first 5 tags (Medium limit)
        return tags[:5]
    
    def _build_references(self, item: Dict, url: str) -> str:
        """Build references section"""
        refs = f"""## References & Further Reading

**Original Paper:** [{item.get('title', 'Source')}]({url})

"""
        
        # Add authors if available
        authors = item.get('authors', [])
        if authors:
            author_list = ', '.join(authors[:5])  # Limit to first 5 authors
            if len(authors) > 5:
                author_list += f' et al. ({len(authors)} authors)'
            refs += f"**Authors:** {author_list}\n\n"
        
        # Add published date if available
        published = item.get('published', '')
        if published:
            refs += f"**Published:** {published}\n\n"
        
        # Add PDF link if available
        pdf_url = item.get('pdf_url', '')
        if pdf_url:
            refs += f"**PDF:** [Download]({pdf_url})\n\n"
        
        return refs
    
    def _build_footer(self) -> str:
        """Build article footer"""
        return """---

*This article was generated using AI-assisted analysis to provide comprehensive coverage of recent research. The analysis includes technical details, implications, and practical applications to help engineers and researchers understand the significance of this work.*

*Follow for more in-depth analyses of AI/ML research papers.*
"""
