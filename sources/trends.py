"""
Trend discovery engine for AI/ML topics
Identifies emerging trends, patterns, and technologies worth covering
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from utils.logger import setup_logger
from llm.client import PerplexityClient
from llm.prompts import get_prompt

logger = setup_logger(__name__)


class TrendDiscovery:
    """
    Discover trending AI/ML topics using LLM-powered analysis
    Focuses on: agentic AI, design patterns, production best practices
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.llm_config = config.get('llm', {})
        self.client = PerplexityClient(self.llm_config)
        self.trend_categories = [
            'agentic-ai',
            'ai-patterns',
            'production-ai',
            'research-breakthroughs',
            'industry-applications'
        ]
        
        logger.info("Initialized TrendDiscovery engine")
    
    def discover_trends(self, recent_content: List[Dict], max_trends: int = 5) -> List[Dict]:
        """
        Analyze recent content to identify emerging trends
        
        Args:
            recent_content: List of recently fetched papers/articles
            max_trends: Maximum number of trends to return
            
        Returns:
            List of trend dictionaries with scores and metadata
        """
        logger.info(f"Discovering trends from {len(recent_content)} recent items")
        
        try:
            # Prepare content summary for LLM
            content_summary = self._prepare_content_summary(recent_content)
            
            # Get trend analysis from LLM
            prompt = get_prompt(
                'trend_discovery',
                current_date=datetime.now().strftime('%Y-%m-%d'),
                recent_content=content_summary
            )
            
            response = self.client.generate(
                prompt=prompt,
                system_prompt="""You are an AI trend analyst specializing in identifying 
                emerging technologies, patterns, and practices in AI/ML. You have deep 
                knowledge of what makes content engaging on professional platforms.""",
                temperature=0.4,  # Balanced creativity
                max_tokens=2000
            )
            
            # Parse LLM response (expecting JSON format)
            trends = self._parse_trends_response(response)
            
            # Score and rank trends
            ranked_trends = self._rank_trends(trends, recent_content)
            
            # Return top trends
            top_trends = ranked_trends[:max_trends]
            
            logger.info(f"Discovered {len(top_trends)} high-value trends")
            return top_trends
            
        except Exception as e:
            logger.error(f"Failed to discover trends: {e}")
            return []
    
    def _prepare_content_summary(self, content: List[Dict]) -> str:
        """Prepare a concise summary of recent content for LLM analysis"""
        summaries = []
        
        for item in content[:20]:  # Limit to prevent context overflow
            summary = {
                'title': item.get('title', ''),
                'source': item.get('source', ''),
                'category': item.get('category', ''),
                'date': item.get('published', item.get('fetched_at', '')),
                'topics': item.get('topics', []),
            }
            
            # Add brief content snippet
            text = item.get('summary', '')[:200]
            if text:
                summary['snippet'] = text + '...'
            
            summaries.append(summary)
        
        return json.dumps(summaries, indent=2)
    
    def _parse_trends_response(self, response: str) -> List[Dict]:
        """Parse LLM response into structured trend data"""
        try:
            # Try to extract JSON from response
            # LLM might wrap it in markdown code blocks
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                if 'trends' in data:
                    return data['trends']
                
            logger.warning("Could not parse JSON from LLM response, using fallback")
            return []
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse trends JSON: {e}")
            return []
    
    def _rank_trends(self, trends: List[Dict], recent_content: List[Dict]) -> List[Dict]:
        """
        Rank trends by relevance, timeliness, and engagement potential
        """
        for trend in trends:
            # Calculate composite score
            novelty = trend.get('novelty', 50)
            impact = trend.get('impact', 50)
            timeliness = trend.get('timeliness', 50)
            engagement = trend.get('engagement_potential', 50)
            
            # Weighted scoring
            composite_score = (
                novelty * 0.25 +
                impact * 0.30 +
                timeliness * 0.25 +
                engagement * 0.20
            )
            
            trend['composite_score'] = composite_score
            
            # Add metadata
            trend['discovered_at'] = datetime.now().isoformat()
            trend['content_ready'] = True
        
        # Sort by composite score
        ranked = sorted(trends, key=lambda x: x.get('composite_score', 0), reverse=True)
        
        return ranked
    
    def generate_trend_content_item(self, trend: Dict) -> Dict:
        """
        Convert a trend into a content item that can be processed by the pipeline
        
        Args:
            trend: Trend dictionary from discover_trends()
            
        Returns:
            Content item dictionary compatible with existing pipeline
        """
        # Sanitize topic for ID - remove special chars, limit length
        import re
        topic_safe = re.sub(r'[^a-zA-Z0-9_]', '_', trend.get('topic', 'unknown'))[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        item = {
            'id': f"trend_{timestamp}_{topic_safe}",
            'title': self._generate_trend_title(trend),
            'url': '#',  # Trends don't have a single URL
            'summary': trend.get('description', ''),
            'source': 'trend_discovery',
            'source_priority': 'high',
            'category': trend.get('category', 'ai-trends'),
            'topics': [trend.get('topic', '')],
            'published': datetime.now().isoformat(),
            'fetched_at': datetime.now().isoformat(),
            'score': trend.get('composite_score', 0),
            
            # Trend-specific metadata
            'is_trend': True,
            'trend_score': trend.get('trend_score', 0),
            'novelty': trend.get('novelty', 0),
            'impact': trend.get('impact', 0),
            'timeliness': trend.get('timeliness', 0),
            'engagement_potential': trend.get('engagement_potential', 0),
            'why_now': trend.get('why_now', ''),
            'content_angle': trend.get('content_angle', ''),
            'trend_sources': trend.get('sources', []),
        }
        
        return item
    
    def _generate_trend_title(self, trend: Dict) -> str:
        """Generate an engaging title for a trend"""
        topic = trend.get('topic', 'Emerging AI Trend')
        category = trend.get('category', '').replace('-', ' ').title()
        
        # Use content_angle if available for more specific title
        angle = trend.get('content_angle', '')
        if angle and len(angle) < 100:
            return f"{topic}: {angle}"
        
        return f"{topic} - {category}"


class TrendScheduler:
    """
    Schedule and manage trend discovery runs
    Ensures fresh trending content is regularly identified
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.discovery_engine = TrendDiscovery(config)
        self.last_run = None
        self.min_interval_hours = config.get('trend_discovery', {}).get('interval_hours', 24)
        
        logger.info(f"Initialized TrendScheduler (interval: {self.min_interval_hours}h)")
    
    def should_run_discovery(self) -> bool:
        """Check if enough time has passed since last discovery"""
        if not self.last_run:
            return True
        
        time_since_last = datetime.now() - self.last_run
        return time_since_last.total_seconds() > (self.min_interval_hours * 3600)
    
    def run_discovery(self, recent_content: List[Dict]) -> List[Dict]:
        """Run trend discovery if interval has passed"""
        if not self.should_run_discovery():
            logger.info("Skipping trend discovery - ran recently")
            return []
        
        trends = self.discovery_engine.discover_trends(recent_content)
        self.last_run = datetime.now()
        
        return trends
