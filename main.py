"""
AI Research Publisher
Main entry point for the application
"""

import sys
import click
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from sources.arxiv import ArxivFetcher
from sources.blogs import BlogFetcher
from sources.hackernews import HackerNewsFetcher
from sources.github import GitHubFetcher
from filters.relevance import RelevanceFilter
from filters.dedup import Deduplicator
from filters.ranker import ContentRanker
from llm.analyzer import ContentAnalyzer
from formatters.blog import BlogFormatter
from formatters.linkedin import LinkedInFormatter
from publishers.github_pages import GitHubPagesPublisher
from publishers.linkedin_api import LinkedInPublisher
from utils.cache import Cache
import yaml

logger = setup_logger(__name__)


def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


@click.group()
def cli():
    """AI Research Publisher - Automated content generation from AI/ML sources"""
    pass


@cli.command()
@click.option('--source', type=click.Choice(['arxiv', 'blogs', 'hackernews', 'github', 'all']), 
              default='all', help='Source to fetch from')
@click.option('--cache/--no-cache', default=True, help='Use cached results')
def fetch(source, cache):
    """Fetch content from configured sources"""
    logger.info(f"Fetching content from: {source}")
    
    config = load_config()
    cache_manager = Cache() if cache else None
    
    fetchers = {
        'arxiv': ArxivFetcher(config['sources']['arxiv']),
        'blogs': BlogFetcher(config['sources']['blogs']),
        'hackernews': HackerNewsFetcher(config['sources']['hackernews']),
        'github': GitHubFetcher(config['sources']['github'])
    }
    
    all_content = []
    
    if source == 'all':
        for name, fetcher in fetchers.items():
            if config['sources'][name].get('enabled', True):
                logger.info(f"Fetching from {name}...")
                content = fetcher.fetch()
                all_content.extend(content)
                logger.info(f"Fetched {len(content)} items from {name}")
    else:
        fetcher = fetchers[source]
        all_content = fetcher.fetch()
        logger.info(f"Fetched {len(all_content)} items from {source}")
    
    # Apply filters
    logger.info("Applying relevance filters...")
    relevance_filter = RelevanceFilter(config['filters'])
    filtered_content = relevance_filter.filter(all_content)
    logger.info(f"Filtered to {len(filtered_content)} relevant items")
    
    # Deduplicate
    logger.info("Deduplicating content...")
    dedup = Deduplicator(config['filters']['deduplication'])
    unique_content = dedup.deduplicate(filtered_content)
    logger.info(f"Deduplicated to {len(unique_content)} unique items")
    
    # Rank
    logger.info("Ranking content...")
    ranker = ContentRanker(config['filters']['ranking'])
    ranked_content = ranker.rank(unique_content)
    
    # Save results
    output_path = Path('data/fetched/latest.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(output_path, 'w') as f:
        json.dump(ranked_content, f, indent=2, default=str)
    
    logger.info(f"Saved {len(ranked_content)} items to {output_path}")
    
    # Display top 10
    click.echo("\n📊 Top 10 Items:")
    for i, item in enumerate(ranked_content[:10], 1):
        click.echo(f"{i}. [{item['source']}] {item['title']}")
        click.echo(f"   Score: {item.get('score', 0):.2f} | {item['url']}\n")


@cli.command()
@click.option('--count', default=5, help='Number of items to generate content for')
@click.option('--format', type=click.Choice(['blog', 'linkedin', 'both']), 
              default='both', help='Output format')
def generate(count, format):
    """Generate blog articles and LinkedIn posts using Perplexity LLM"""
    logger.info(f"Generating content for top {count} items...")
    
    config = load_config()
    
    # Load fetched content
    import json
    with open('data/fetched/latest.json', 'r') as f:
        items = json.load(f)[:count]
    
    if not items:
        click.echo("❌ No items found. Run 'fetch' command first.")
        return
    
    # Initialize LLM analyzer
    analyzer = ContentAnalyzer(config['llm'])
    
    # Initialize formatters
    blog_formatter = BlogFormatter(config['formatting']['blog'])
    linkedin_formatter = LinkedInFormatter(config['formatting']['linkedin'])
    
    generated_count = 0
    
    for i, item in enumerate(items, 1):
        click.echo(f"\n🔄 Processing {i}/{count}: {item['title']}")
        
        try:
            # Analyze content using 7-stage prompt pipeline
            analysis = analyzer.analyze(item)
            
            # Generate blog article
            if format in ['blog', 'both']:
                blog_article = blog_formatter.format(item, analysis)
                
                # Save draft
                blog_path = Path(f"data/drafts/blog/{item['id']}.md")
                blog_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(blog_path, 'w') as f:
                    f.write(blog_article)
                
                click.echo(f"  ✅ Blog article: {blog_path}")
            
            # Generate LinkedIn post
            if format in ['linkedin', 'both']:
                linkedin_post = linkedin_formatter.format(item, analysis)
                
                # Save draft
                linkedin_path = Path(f"data/drafts/linkedin/{item['id']}.txt")
                linkedin_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(linkedin_path, 'w') as f:
                    f.write(linkedin_post)
                
                click.echo(f"  ✅ LinkedIn post: {linkedin_path}")
            
            generated_count += 1
            
        except Exception as e:
            logger.error(f"Failed to generate content for {item['title']}: {e}")
            click.echo(f"  ❌ Error: {e}")
    
    click.echo(f"\n✨ Generated content for {generated_count}/{count} items")
    click.echo(f"📁 Drafts saved in: data/drafts/")


@cli.command()
def review():
    """Review generated drafts"""
    logger.info("Reviewing drafts...")
    
    blog_drafts = list(Path('data/drafts/blog').glob('*.md'))
    linkedin_drafts = list(Path('data/drafts/linkedin').glob('*.txt'))
    
    click.echo(f"\n📝 Blog Drafts ({len(blog_drafts)}):")
    for draft in blog_drafts:
        click.echo(f"  - {draft.name}")
    
    click.echo(f"\n💼 LinkedIn Drafts ({len(linkedin_drafts)}):")
    for draft in linkedin_drafts:
        click.echo(f"  - {draft.name}")
    
    click.echo(f"\nTo view a draft: cat data/drafts/blog/<filename>")


@cli.command()
@click.option('--platform', type=click.Choice(['blog', 'linkedin', 'both']), 
              default='both', help='Publishing platform')
@click.option('--approve', is_flag=True, help='Skip approval prompts')
def publish(platform, approve):
    """Publish approved content"""
    logger.info(f"Publishing to: {platform}")
    
    config = load_config()
    
    # Initialize publishers
    github_publisher = GitHubPagesPublisher(config['publishing']['blog'])
    linkedin_publisher = LinkedInPublisher(config['publishing']['linkedin'])
    
    published_count = 0
    
    # Publish blog articles
    if platform in ['blog', 'both']:
        blog_drafts = list(Path('data/drafts/blog').glob('*.md'))
        
        for draft in blog_drafts:
            if not approve:
                click.echo(f"\n📄 Review: {draft.name}")
                with open(draft, 'r') as f:
                    preview = f.read()[:500]
                    click.echo(preview + "...\n")
                
                if not click.confirm("Publish this article?"):
                    continue
            
            try:
                github_publisher.publish(draft)
                click.echo(f"  ✅ Published: {draft.name}")
                
                # Move to published
                published_path = Path(f"data/published/blog/{draft.name}")
                published_path.parent.mkdir(parents=True, exist_ok=True)
                draft.rename(published_path)
                
                published_count += 1
                
            except Exception as e:
                logger.error(f"Failed to publish {draft.name}: {e}")
                click.echo(f"  ❌ Error: {e}")
    
    # Publish LinkedIn posts
    if platform in ['linkedin', 'both']:
        linkedin_drafts = list(Path('data/drafts/linkedin').glob('*.txt'))
        
        for draft in linkedin_drafts:
            if not approve:
                click.echo(f"\n💼 Review: {draft.name}")
                with open(draft, 'r') as f:
                    content = f.read()
                    click.echo(content + "\n")
                
                if not click.confirm("Publish this post?"):
                    continue
            
            try:
                linkedin_publisher.publish(draft)
                click.echo(f"  ✅ Published: {draft.name}")
                
                # Move to published
                published_path = Path(f"data/published/linkedin/{draft.name}")
                published_path.parent.mkdir(parents=True, exist_ok=True)
                draft.rename(published_path)
                
                published_count += 1
                
            except Exception as e:
                logger.error(f"Failed to publish {draft.name}: {e}")
                click.echo(f"  ❌ Error: {e}")
    
    click.echo(f"\n✨ Published {published_count} items")


@cli.command()
@click.option('--days', default=7, help='Number of days to show metrics for')
def metrics(days):
    """Show publishing metrics"""
    logger.info(f"Showing metrics for last {days} days")
    
    import json
    from datetime import datetime, timedelta
    
    metrics_file = Path('data/metrics.json')
    
    if not metrics_file.exists():
        click.echo("No metrics available yet.")
        return
    
    with open(metrics_file, 'r') as f:
        data = json.load(f)
    
    # Filter by date range
    cutoff = datetime.now() - timedelta(days=days)
    
    recent_metrics = [
        m for m in data 
        if datetime.fromisoformat(m['timestamp']) >= cutoff
    ]
    
    # Calculate stats
    total_fetched = sum(m.get('fetched', 0) for m in recent_metrics)
    total_generated = sum(m.get('generated', 0) for m in recent_metrics)
    total_published = sum(m.get('published', 0) for m in recent_metrics)
    
    click.echo(f"\n📊 Metrics (Last {days} days):")
    click.echo(f"  Items Fetched: {total_fetched}")
    click.echo(f"  Content Generated: {total_generated}")
    click.echo(f"  Content Published: {total_published}")
    
    if total_fetched > 0:
        click.echo(f"  Conversion Rate: {(total_published/total_fetched)*100:.1f}%")


@cli.command()
def init():
    """Initialize the project (create directories, setup)"""
    logger.info("Initializing project...")
    
    directories = [
        'data/cache',
        'data/fetched',
        'data/drafts/blog',
        'data/drafts/linkedin',
        'data/published/blog',
        'data/published/linkedin',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        click.echo(f"  ✅ Created: {directory}/")
    
    # Create initial metrics file
    metrics_file = Path('data/metrics.json')
    if not metrics_file.exists():
        with open(metrics_file, 'w') as f:
            json.dump([], f)
        click.echo(f"  ✅ Created: {metrics_file}")
    
    # Check for .env file
    if not Path('.env').exists():
        click.echo(f"\n⚠️  Create .env file from .env.example and add your API keys")
        click.echo(f"   cp .env.example .env")
    
    click.echo("\n✨ Initialization complete!")


if __name__ == '__main__':
    cli()
