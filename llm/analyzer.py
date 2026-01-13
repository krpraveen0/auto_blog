"""
Content analyzer using 7-stage prompt pipeline with Perplexity
"""

from typing import Dict
from llm.client import PerplexityClient
from llm.prompts import get_system_prompt, get_prompt
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentAnalyzer:
    """Analyze content through 7-stage credibility pipeline"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.client = PerplexityClient(config)
        self.system_prompt = get_system_prompt()
        
        # Which stages to run (can be configured)
        self.stages = config.get('prompt_stages', [
            'fact_extraction',
            'engineer_summary',
            'impact_analysis',
            'application_mapping'
        ])
        
        logger.info(f"Initialized ContentAnalyzer with {len(self.stages)} stages")
    
    def analyze(self, item: Dict) -> Dict:
        """
        Run full analysis pipeline on a content item
        
        Args:
            item: Content item dictionary
            
        Returns:
            Analysis results dictionary
        """
        logger.info(f"Analyzing: {item.get('title', 'Unknown')}")
        
        # Prepare content for analysis
        content = self._prepare_content(item)
        
        analysis = {
            'item_id': item.get('id'),
            'title': item.get('title'),
            'url': item.get('url'),
            'source': item.get('source')
        }
        
        # Run each stage sequentially
        for stage in self.stages:
            try:
                logger.info(f"Running stage: {stage}")
                result = self._run_stage(stage, content, analysis)
                analysis[stage] = result
                
            except Exception as e:
                logger.error(f"Failed at stage {stage}: {e}")
                analysis[stage] = f"Error: {str(e)}"
        
        logger.info(f"Analysis complete for: {item.get('title')}")
        return analysis
    
    def _prepare_content(self, item: Dict) -> str:
        """Prepare content text for analysis"""
        parts = []
        
        parts.append(f"Title: {item.get('title', 'N/A')}")
        parts.append(f"Source: {item.get('source', 'N/A')}")
        parts.append(f"URL: {item.get('url', 'N/A')}")
        
        if item.get('authors'):
            authors = ', '.join(item['authors']) if isinstance(item['authors'], list) else item['authors']
            parts.append(f"Authors: {authors}")
        
        if item.get('published'):
            parts.append(f"Published: {item['published']}")
        
        summary = item.get('summary', '')
        if summary:
            parts.append(f"\nContent:\n{summary}")
        
        # Add source-specific metadata
        if item.get('category'):
            parts.append(f"Category: {item['category']}")
        
        if item.get('topics'):
            topics = ', '.join(item['topics']) if isinstance(item['topics'], list) else item['topics']
            parts.append(f"Topics: {topics}")
        
        return '\n'.join(parts)
    
    def _run_stage(self, stage: str, content: str, previous_analysis: Dict) -> str:
        """Run a single analysis stage"""
        
        # Get stage-specific prompt
        if stage in ['blog_synthesis', 'linkedin_formatting']:
            # These stages need the full analysis
            analyzed_content = self._format_analysis(previous_analysis)
            prompt = get_prompt(
                stage,
                title=previous_analysis.get('title', ''),
                url=previous_analysis.get('url', ''),
                analyzed_content=analyzed_content
            )
        else:
            # Early stages work with raw content
            prompt = get_prompt(stage, content=content)
        
        # Generate response
        response = self.client.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt
        )
        
        return response.strip()
    
    def _format_analysis(self, analysis: Dict) -> str:
        """Format analysis results for downstream stages"""
        parts = []
        
        for key in ['fact_extraction', 'engineer_summary', 'impact_analysis', 'application_mapping']:
            if key in analysis and analysis[key]:
                parts.append(f"## {key.replace('_', ' ').title()}")
                parts.append(analysis[key])
                parts.append("")  # Blank line
        
        return '\n'.join(parts)
    
    def generate_blog(self, analysis: Dict) -> str:
        """Generate blog article from analysis"""
        logger.info("Generating blog article")
        
        analyzed_content = self._format_analysis(analysis)
        prompt = get_prompt(
            'blog_synthesis',
            title=analysis.get('title', ''),
            url=analysis.get('url', ''),
            analyzed_content=analyzed_content
        )
        
        blog_content = self.client.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            max_tokens=3000  # Longer for blog
        )
        
        return blog_content.strip()
    
    def generate_linkedin(self, analysis: Dict) -> str:
        """Generate LinkedIn post from analysis"""
        logger.info("Generating LinkedIn post")
        
        analyzed_content = self._format_analysis(analysis)
        prompt = get_prompt(
            'linkedin_formatting',
            title=analysis.get('title', ''),
            url=analysis.get('url', ''),
            analyzed_content=analyzed_content
        )
        
        linkedin_content = self.client.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            max_tokens=500  # Shorter for LinkedIn
        )
        
        return linkedin_content.strip()
    
    def credibility_check(self, generated_content: str) -> str:
        """Run credibility check on generated content"""
        logger.info("Running credibility check")
        
        prompt = get_prompt('credibility_check', generated_output=generated_content)
        
        check_result = self.client.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt
        )
        
        return check_result.strip()
