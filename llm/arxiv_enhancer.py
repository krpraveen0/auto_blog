"""
ArXiv Paper Enhancer - Enhanced summarization and relevancy checking for arXiv papers
"""

from typing import Dict, Tuple
from llm.client import PerplexityClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ArxivEnhancer:
    """
    Enhance arXiv papers with engaging summaries, verdicts, and relevancy checks
    """
    
    def __init__(self, config: Dict):
        """
        Initialize ArxivEnhancer
        
        Args:
            config: LLM configuration dictionary
        """
        self.config = config
        self.client = PerplexityClient(config)
        
        # Relevancy threshold (0-10 scale)
        self.relevancy_threshold = config.get('arxiv_relevancy_threshold', 6.0)
        
        logger.info(f"Initialized ArxivEnhancer with relevancy threshold: {self.relevancy_threshold}")
    
    def enhance_arxiv_paper(self, paper: Dict) -> Tuple[bool, Dict]:
        """
        Enhance arXiv paper with summary, verdict, and relevancy check
        
        Args:
            paper: arXiv paper dictionary with title, summary, authors, etc.
            
        Returns:
            Tuple of (is_relevant, enhancement_data)
            - is_relevant: Boolean indicating if paper passes relevancy check
            - enhancement_data: Dict with 'summary', 'verdict', 'relevancy_score', 'reason'
        """
        logger.info(f"🔬 Enhancing arXiv paper: {paper.get('title', 'Unknown')}")
        
        try:
            # Step 1: Generate engaging summary
            summary = self._generate_engaging_summary(paper)
            
            # Step 2: Generate verdict on usefulness
            verdict = self._generate_verdict(paper, summary)
            
            # Step 3: Check relevancy
            relevancy_score, relevancy_reason = self._check_relevancy(paper, summary, verdict)
            
            is_relevant = relevancy_score >= self.relevancy_threshold
            
            enhancement_data = {
                'enhanced_summary': summary,
                'verdict': verdict,
                'relevancy_score': relevancy_score,
                'relevancy_reason': relevancy_reason,
                'is_relevant': is_relevant
            }
            
            if is_relevant:
                logger.info(f"✅ Paper is relevant (score: {relevancy_score:.1f}/10)")
            else:
                logger.warning(f"❌ Paper not relevant (score: {relevancy_score:.1f}/10): {relevancy_reason}")
            
            return is_relevant, enhancement_data
            
        except Exception as e:
            logger.error(f"Failed to enhance paper: {e}")
            # Return minimal data on failure with fallback score of 5.0
            return False, {
                'enhanced_summary': paper.get('summary', '')[:500],
                'verdict': 'Could not determine usefulness due to analysis error',
                'relevancy_score': 5.0,  # Neutral fallback score
                'relevancy_reason': f'Enhancement failed: {str(e)}',
                'is_relevant': False
            }
    
    def _generate_engaging_summary(self, paper: Dict) -> str:
        """Generate an engaging, accessible summary of the paper"""
        
        prompt = f"""You are an expert AI/ML researcher who explains complex research papers in an engaging way.

Paper Title: {paper.get('title', 'Unknown')}
Authors: {', '.join(paper.get('authors', [])[:5])}
Abstract: {paper.get('summary', '')}

Create an engaging 2-3 sentence summary that:
1. Explains what the researchers did in simple terms
2. Highlights the key innovation or contribution
3. Makes it interesting and accessible to ML practitioners

Be conversational and avoid academic jargon. Focus on practical insights.
Do NOT use phrases like "This paper", "The authors", or "In this work".
Write in present tense as if describing current developments.

Summary:"""

        try:
            response = self.client.generate(prompt, temperature=0.4)
            summary = response.strip()
            
            # Clean up any remaining academic patterns
            summary = self._clean_academic_language(summary)
            
            logger.info("✅ Generated engaging summary")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            # Fallback to truncated abstract
            return paper.get('summary', '')[:500]
    
    def _generate_verdict(self, paper: Dict, summary: str) -> str:
        """Generate a verdict on how the paper is useful"""
        
        prompt = f"""You are an expert ML engineer evaluating research papers for practical impact.

Paper Title: {paper.get('title', 'Unknown')}
Summary: {summary}

Provide a ONE sentence verdict on how this paper is useful to ML practitioners. Consider:
- Practical applications
- Novel techniques that can be adopted
- Solutions to common problems
- Advancement of the field

Format: "Useful for [specific use case/audience] because [concrete reason]"

Keep it concise and actionable. No marketing language.

Verdict:"""

        try:
            response = self.client.generate(prompt, temperature=0.3)
            verdict = response.strip()
            
            # Ensure it starts properly
            if not verdict.startswith('Useful for'):
                verdict = f"Useful for {verdict}"
            
            logger.info("✅ Generated verdict")
            return verdict
            
        except Exception as e:
            logger.error(f"Failed to generate verdict: {e}")
            return "Potential value for AI/ML practitioners exploring cutting-edge research."
    
    def _check_relevancy(self, paper: Dict, summary: str, verdict: str) -> Tuple[float, str]:
        """
        Check relevancy of paper to AI/ML practitioners
        
        Returns:
            Tuple of (relevancy_score, reason)
            - relevancy_score: Float from 0-10
            - reason: String explanation of the score
        """
        
        prompt = f"""You are an expert at evaluating research papers for relevancy to AI/ML practitioners and engineers.

Paper Title: {paper.get('title', 'Unknown')}
Category: {paper.get('category', 'Unknown')}
Summary: {summary}
Verdict: {verdict}

Evaluate this paper's relevancy on a scale of 0-10, where:
- 10: Highly relevant - breakthrough/practical technique everyone should know
- 7-9: Very relevant - novel approach with clear applications
- 5-6: Moderately relevant - interesting but niche or early-stage
- 3-4: Low relevance - too theoretical or narrow focus
- 0-2: Not relevant - not applicable to practitioners

Consider:
1. Practical applicability to real-world ML problems
2. Novelty and potential impact
3. Relevance to current AI/ML trends (LLMs, RAG, agents, etc.)
4. Clarity and accessibility of the work

Provide your response in this EXACT format:
Score: [number from 0-10]
Reason: [one sentence explanation]

Your evaluation:"""

        try:
            response = self.client.generate(prompt, temperature=0.2)
            
            # Parse score and reason
            lines = response.strip().split('\n')
            score = 5.0  # default
            reason = "Could not determine relevancy"
            
            for line in lines:
                if line.startswith('Score:'):
                    try:
                        score = float(line.split(':')[1].strip())
                        score = max(0.0, min(10.0, score))  # Clamp to 0-10
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('Reason:'):
                    reason = line.split(':', 1)[1].strip()
            
            logger.info(f"✅ Relevancy check: {score:.1f}/10")
            return score, reason
            
        except Exception as e:
            logger.error(f"Failed to check relevancy: {e}")
            return 5.0, f"Relevancy check failed: {str(e)}"
    
    def _clean_academic_language(self, text: str) -> str:
        """Clean up academic/formal language from text"""
        import re
        
        # Remove common academic patterns
        patterns = [
            r'^This paper ',
            r'^The authors ',
            r'^In this work,? ',
            r'^The paper ',
            r'^We present ',
            r'^We propose ',
            r'^This study ',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Capitalize first letter if needed
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
