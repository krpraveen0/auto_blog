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
        Enhanced with better error recovery for autonomous operation
        
        Args:
            item: Content item dictionary
            
        Returns:
            Analysis results dictionary
        """
        logger.info(f"🔬 Starting analysis: {item.get('title', 'Unknown')}")
        
        # Prepare content for analysis
        content = self._prepare_content(item)
        
        analysis = {
            'item_id': item.get('id'),
            'title': item.get('title'),
            'url': item.get('url'),
            'source': item.get('source'),
            'success': True,  # Track overall success
            'completed_stages': [],
            'failed_stages': []
        }
        
        # Run each stage sequentially with enhanced error handling
        for i, stage in enumerate(self.stages, 1):
            try:
                logger.info(f"  📍 Stage {i}/{len(self.stages)}: {stage}")
                result = self._run_stage(stage, content, analysis)
                analysis[stage] = result
                analysis['completed_stages'].append(stage)
                logger.info(f"  ✅ Stage {stage} completed successfully")
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(f"  ❌ Stage {stage} failed: {e}")
                analysis[stage] = error_msg
                analysis['failed_stages'].append(stage)
                
                # Autonomous decision: continue with remaining stages even if one fails
                # This improves resilience and allows partial results
                logger.info(f"  ⚡ Continuing with remaining stages despite failure")
        
        # Update success status
        if analysis['failed_stages']:
            analysis['success'] = False
            logger.warning(f"⚠️  Analysis completed with {len(analysis['failed_stages'])} failed stages")
        else:
            logger.info(f"✨ Analysis complete: All {len(self.stages)} stages successful")
        
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
        """
        Run a single analysis stage with enhanced logging
        
        Args:
            stage: Stage name to run
            content: Raw content to analyze
            previous_analysis: Results from previous stages
            
        Returns:
            Stage result as string
        """
        
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
        
        logger.debug(f"    🤖 Generating response for stage: {stage}")
        
        # Generate response with error handling
        try:
            response = self.client.generate(
                system_prompt=self.system_prompt,
                user_prompt=prompt
            )
            
            result = response.strip()
            logger.debug(f"    📝 Generated {len(result)} characters for {stage}")
            
            return result
            
        except Exception as e:
            logger.error(f"    ❌ LLM generation failed for {stage}: {e}")
            raise  # Re-raise to be caught by caller
    
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
    
    def generate_linkedin(self, analysis: Dict, use_engaging_format: bool = True) -> str:
        """
        Generate LinkedIn post from analysis
        
        Args:
            analysis: Content analysis dictionary
            use_engaging_format: If True, use enhanced engagement-focused format
            
        Returns:
            LinkedIn post content
        """
        logger.info(f"Generating LinkedIn post (engaging={use_engaging_format})")
        
        analyzed_content = self._format_analysis(analysis)
        
        # Use enhanced engaging format if enabled
        if use_engaging_format:
            prompt = get_prompt(
                'linkedin_engaging',
                title=analysis.get('title', ''),
                url=analysis.get('url', ''),
                analyzed_content=analyzed_content
            )
        else:
            # Fall back to standard format
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
    
    def validate_linkedin_safety(self, content: str) -> Dict:
        """
        Comprehensive safety and quality validation for LinkedIn content
        
        Args:
            content: LinkedIn post content to validate
            
        Returns:
            Validation result dictionary with is_valid, score, issues, etc.
        """
        logger.info("Running comprehensive LinkedIn safety validation")
        
        try:
            # Get LLM validation
            prompt = get_prompt('linkedin_validation', content=content)
            
            response = self.client.generate(
                system_prompt="""You are a content safety expert specializing in 
                professional social media. Your role is to ensure content meets 
                platform guidelines, professional standards, and protects user reputation.""",
                user_prompt=prompt,
                temperature=0.2,  # Low temp for consistent validation
                max_tokens=1000
            )
            
            # Parse JSON response
            import json
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                validation_result = json.loads(json_str)
                
                logger.info(f"Safety validation: {'APPROVED' if validation_result.get('approved', False) else 'REJECTED'}")
                logger.info(f"Validation score: {validation_result.get('validation_score', 0)}/100")
                
                return validation_result
            else:
                logger.error("Could not parse validation response")
                # Fallback to basic validation
                return self._basic_validation(content)
                
        except Exception as e:
            logger.error(f"Safety validation failed: {e}")
            # Fallback to basic validation
            return self._basic_validation(content)
    
    def _basic_validation(self, content: str) -> Dict:
        """Fallback basic validation if LLM validation fails"""
        import re
        
        issues = []
        score = 100
        
        # Get profanity list from config or use minimal defaults
        profanity_patterns = self.config.get('profanity_list', [
            'damn', 'hell', 'crap'  # Minimal list - extend in config
        ])
        
        # Basic safety checks
        for word in profanity_patterns:
            if re.search(rf'\b{word}\b', content, re.IGNORECASE):
                issues.append({
                    'category': 'safety',
                    'severity': 'critical',
                    'issue': f'Contains profanity: {word}',
                    'suggestion': 'Remove profane language'
                })
                score -= 30
                break  # One profanity is enough to flag
        
        # Length check
        word_count = len(content.split())
        if word_count > 300:
            issues.append({
                'category': 'quality',
                'severity': 'medium',
                'issue': f'Too long: {word_count} words',
                'suggestion': 'Shorten to under 300 words'
            })
            score -= 10
        
        # Quality checks - reuse formatter's clean_content logic
        if re.search(r'\[\d+\]', content):
            issues.append({
                'category': 'quality',
                'severity': 'low',
                'issue': 'Contains citation markers',
                'suggestion': 'Remove [1], [2] style citations'
            })
            score -= 5
        
        is_valid = score >= 70
        
        return {
            'is_valid': is_valid,
            'validation_score': max(0, score),
            'issues': issues,
            'approved': is_valid,
            'summary': f"Basic validation: {len(issues)} issues found"
        }
    
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
    
    def analyze_github_eli5(self, item: Dict) -> Dict:
        """
        Run ELI5 (Explain Like I'm 5) analysis pipeline for GitHub repositories
        
        Args:
            item: GitHub repository item dictionary
            
        Returns:
            Analysis dictionary with ELI5 explanations
        """
        from llm.prompts import get_github_eli5_system_prompt, get_prompt
        
        logger.info(f"Running ELI5 GitHub analysis for: {item.get('title', 'Unknown')}")
        
        # Use ELI5 system prompt for GitHub
        eli5_system_prompt = get_github_eli5_system_prompt()
        
        # Prepare repository metadata
        repo_info = {
            'title': item.get('title', ''),
            'summary': item.get('summary', 'No description available'),
            'url': item.get('url', ''),
            'language': item.get('language', 'Unknown'),
            'topics': ', '.join(item.get('topics', [])) if item.get('topics') else 'Not specified',
            'stars': item.get('stars', 0),
            'forks': item.get('forks', 0),
            'contributors': item.get('contributors_count', 0),
            'license': item.get('license', 'Not specified'),
            'stars_per_day': item.get('stars_per_day', 0),
            'is_active': 'Yes' if item.get('is_recently_active') else 'No'
        }
        
        analysis = {
            'item_id': item.get('id'),
            'title': item.get('title'),
            'url': item.get('url'),
            'source': 'github'
        }
        
        # Stage 1: What does it do?
        try:
            logger.info("ELI5 Stage 1: What does it do?")
            what_prompt = get_prompt('github_eli5_what', **repo_info)
            analysis['eli5_what'] = self.client.generate(
                system_prompt=eli5_system_prompt,
                user_prompt=what_prompt,
                max_tokens=500
            ).strip()
        except Exception as e:
            logger.error(f"Failed ELI5 'what' stage: {e}")
            analysis['eli5_what'] = "Failed to generate explanation"
        
        # Stage 2: How does it work?
        try:
            logger.info("ELI5 Stage 2: How does it work?")
            how_prompt = get_prompt('github_eli5_how', **repo_info)
            analysis['eli5_how'] = self.client.generate(
                system_prompt=eli5_system_prompt,
                user_prompt=how_prompt,
                max_tokens=600
            ).strip()
        except Exception as e:
            logger.error(f"Failed ELI5 'how' stage: {e}")
            analysis['eli5_how'] = "Failed to generate explanation"
        
        # Stage 3: Why does it matter?
        try:
            logger.info("ELI5 Stage 3: Why does it matter?")
            why_prompt = get_prompt('github_eli5_why', **repo_info)
            analysis['eli5_why'] = self.client.generate(
                system_prompt=eli5_system_prompt,
                user_prompt=why_prompt,
                max_tokens=500
            ).strip()
        except Exception as e:
            logger.error(f"Failed ELI5 'why' stage: {e}")
            analysis['eli5_why'] = "Failed to generate explanation"
        
        # Stage 4: Getting started
        try:
            logger.info("ELI5 Stage 4: Getting started")
            started_prompt = get_prompt('github_eli5_getting_started', **repo_info)
            analysis['eli5_getting_started'] = self.client.generate(
                system_prompt=eli5_system_prompt,
                user_prompt=started_prompt,
                max_tokens=500
            ).strip()
        except Exception as e:
            logger.error(f"Failed ELI5 'getting started' stage: {e}")
            analysis['eli5_getting_started'] = "Failed to generate explanation"
        
        logger.info(f"ELI5 GitHub analysis complete for: {item.get('title')}")
        return analysis
    
    def generate_github_eli5_blog(self, item: Dict, analysis: Dict) -> str:
        """
        Generate an ELI5 blog article for GitHub repository
        
        Args:
            item: GitHub repository item
            analysis: ELI5 analysis results
            
        Returns:
            Blog article content
        """
        from llm.prompts import get_github_eli5_system_prompt, get_prompt
        
        logger.info("Generating ELI5 GitHub blog article")
        
        eli5_system_prompt = get_github_eli5_system_prompt()
        
        # Mapping of analysis keys to section titles
        section_titles = {
            'eli5_what': 'What Does It Do',
            'eli5_how': 'How Does It Work',
            'eli5_why': 'Why Does It Matter',
            'eli5_getting_started': 'Getting Started'
        }
        
        # Format analysis for blog generation
        analyzed_content = []
        for key, title in section_titles.items():
            if key in analysis and analysis[key]:
                analyzed_content.append(f"## {title}")
                analyzed_content.append(analysis[key])
                analyzed_content.append("")
        
        repo_info = {
            'title': item.get('title', ''),
            'summary': item.get('summary', ''),
            'url': item.get('url', ''),
            'language': item.get('language', 'Unknown'),
            'topics': ', '.join(item.get('topics', [])) if item.get('topics') else 'Not specified',
            'stars': item.get('stars', 0),
            'forks': item.get('forks', 0),
            'contributors': item.get('contributors_count', 0),
            'license': item.get('license', 'Not specified'),
            'stars_per_day': item.get('stars_per_day', 0),
            'is_active': 'Yes' if item.get('is_recently_active') else 'No',
            'analyzed_content': '\n'.join(analyzed_content)
        }
        
        blog_prompt = get_prompt('github_eli5_blog', **repo_info)
        
        blog_content = self.client.generate(
            system_prompt=eli5_system_prompt,
            user_prompt=blog_prompt,
            max_tokens=3000
        )
        
        return blog_content.strip()
