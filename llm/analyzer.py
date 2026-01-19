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
    
    def validate_linkedin_content(self, content: str) -> tuple:
        """
        Validate LinkedIn content before publishing
        
        Args:
            content: Generated LinkedIn post content
            
        Returns:
            (is_valid, error_message) - tuple of boolean and error string
        """
        issues = []
        
        # Check for citation markers
        import re
        if re.search(r'\[\d+\]', content):
            issues.append("Contains citation markers like [1], [2]")
        
        # Check for invalid hashtag markers
        if 'hashtag#' in content:
            issues.append("Contains 'hashtag#' instead of proper hashtags")
        
        # Check for filler words at the end
        filler_words = ['like', 'interesting', 'exciting', 'amazing', 'fantastic']
        for word in filler_words:
            if re.search(rf'\b{word}\s*\.?\s*$', content, re.IGNORECASE):
                issues.append(f"Ends with filler word: '{word}'")
                break
        
        # Check for markdown formatting
        if '**' in content or '__' in content or ('*' in content and not content.count('*') % 2):
            issues.append("Contains markdown formatting")
        
        # Check word count (should be ~120 words)
        word_count = len(content.split())
        if word_count > 300:
            issues.append(f"Too long: {word_count} words (max 300)")
        
        is_valid = len(issues) == 0
        error_msg = "; ".join(issues) if issues else ""
        
        logger.info(f"LinkedIn content validation: {'PASS' if is_valid else 'FAIL'}")
        if not is_valid:
            logger.warning(f"Validation issues: {error_msg}")
        
        return is_valid, error_msg
    
    def analyze_for_medium(self, item: Dict) -> Dict:
        """
        Run comprehensive analysis pipeline for Medium articles with diagrams
        
        Args:
            item: Content item dictionary
            
        Returns:
            Comprehensive analysis dictionary with all sections and diagrams
        """
        logger.info(f"Running comprehensive Medium analysis for: {item.get('title', 'Unknown')}")
        
        # Start with standard analysis
        analysis = self.analyze(item)
        
        # Add comprehensive sections for Medium
        content = self._prepare_content(item)
        
        try:
            # Generate methodology section
            logger.info("Generating methodology section")
            methodology_prompt = get_prompt('methodology', content=content)
            analysis['methodology'] = self.client.generate(
                system_prompt=self.system_prompt,
                user_prompt=methodology_prompt,
                max_tokens=1000
            ).strip()
            
            # Generate results section
            logger.info("Generating results section")
            results_prompt = get_prompt('results', content=content)
            analysis['results'] = self.client.generate(
                system_prompt=self.system_prompt,
                user_prompt=results_prompt,
                max_tokens=1000
            ).strip()
            
            # Generate comprehensive Medium article
            logger.info("Generating comprehensive Medium article")
            analyzed_content = self._format_analysis(analysis)
            medium_prompt = get_prompt(
                'medium_synthesis',
                title=item.get('title', ''),
                url=item.get('url', ''),
                analyzed_content=analyzed_content
            )
            analysis['medium_synthesis'] = self.client.generate(
                system_prompt=self.system_prompt,
                user_prompt=medium_prompt,
                max_tokens=3500
            ).strip()
            
            # Generate Mermaid diagrams
            logger.info("Generating Mermaid diagrams")
            diagrams = self._generate_diagrams(content, analysis)
            analysis['diagrams'] = diagrams
            
        except Exception as e:
            logger.error(f"Error in comprehensive Medium analysis: {e}")
            # Don't fail entirely, return what we have
        
        logger.info(f"Comprehensive Medium analysis complete")
        return analysis
    
    def _generate_diagrams(self, content: str, analysis: Dict) -> Dict:
        """
        Generate Mermaid diagrams for visualization
        
        Args:
            content: Raw content
            analysis: Analysis results so far
            
        Returns:
            Dictionary with different diagram types
        """
        diagrams = {}
        
        # Combine content and analysis for diagram generation
        full_context = f"{content}\n\n{self._format_analysis(analysis)}"
        
        try:
            # Architecture diagram
            logger.info("Generating architecture diagram")
            arch_prompt = get_prompt('diagram_architecture', content=full_context)
            diagrams['architecture'] = self.client.generate(
                system_prompt=self.system_prompt,
                user_prompt=arch_prompt,
                max_tokens=800
            ).strip()
        except Exception as e:
            logger.warning(f"Failed to generate architecture diagram: {e}")
            diagrams['architecture'] = ""
        
        try:
            # Flow diagram
            logger.info("Generating flow diagram")
            flow_prompt = get_prompt('diagram_flow', content=full_context)
            diagrams['flow'] = self.client.generate(
                system_prompt=self.system_prompt,
                user_prompt=flow_prompt,
                max_tokens=800
            ).strip()
        except Exception as e:
            logger.warning(f"Failed to generate flow diagram: {e}")
            diagrams['flow'] = ""
        
        try:
            # Comparison diagram
            logger.info("Generating comparison diagram")
            comp_prompt = get_prompt('diagram_comparison', content=full_context)
            diagrams['comparison'] = self.client.generate(
                system_prompt=self.system_prompt,
                user_prompt=comp_prompt,
                max_tokens=800
            ).strip()
        except Exception as e:
            logger.warning(f"Failed to generate comparison diagram: {e}")
            diagrams['comparison'] = ""
        
        return diagrams
