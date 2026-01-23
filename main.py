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
from sources.trends import TrendDiscovery
from filters.relevance import RelevanceFilter
from filters.dedup import Deduplicator
from filters.ranker import ContentRanker
from llm.analyzer import ContentAnalyzer
from formatters.blog import BlogFormatter
from formatters.linkedin import LinkedInFormatter
from formatters.medium import MediumFormatter
from publishers.github_pages import GitHubPagesPublisher
from publishers.linkedin_api import LinkedInPublisher
from publishers.medium_api import MediumPublisher
from utils.cache import Cache
from utils.database import Database
import yaml

logger = setup_logger(__name__)


def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


def validate_required_env_vars(operation: str = 'general'):
    """
    Validate required environment variables based on operation
    
    Args:
        operation: Type of operation ('general', 'generate', 'publish_linkedin', 'publish_github', 'publish_medium')
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import os
    
    errors = []
    
    # Always required for content generation
    if operation in ['general', 'generate', 'publish_linkedin', 'publish_github', 'publish_medium']:
        if not os.getenv('PERPLEXITY_API_KEY'):
            errors.append("PERPLEXITY_API_KEY is required for content generation")
    
    # LinkedIn-specific
    if operation == 'publish_linkedin':
        if not os.getenv('LINKEDIN_ACCESS_TOKEN'):
            errors.append("LINKEDIN_ACCESS_TOKEN is required for LinkedIn publishing")
        if not os.getenv('LINKEDIN_USER_ID'):
            errors.append("LINKEDIN_USER_ID is required for LinkedIn publishing")
    
    # GitHub Pages-specific
    if operation == 'publish_github':
        if not os.getenv('GH_PAGES_TOKEN'):
            errors.append("GH_PAGES_TOKEN is required for GitHub Pages publishing")
        if not os.getenv('GITHUB_REPO'):
            errors.append("GITHUB_REPO is required for GitHub Pages publishing")
    
    # Medium-specific
    if operation == 'publish_medium':
        if not os.getenv('MEDIUM_INTEGRATION_TOKEN'):
            errors.append("MEDIUM_INTEGRATION_TOKEN is required for Medium publishing")
    
    if errors:
        return False, "\n".join(errors)
    
    return True, None


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
    
    # Save results to JSON
    output_path = Path('data/fetched/latest.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(output_path, 'w') as f:
        json.dump(ranked_content, f, indent=2, default=str)
    
    logger.info(f"Saved {len(ranked_content)} items to {output_path}")
    
    # Save to database
    db = Database()
    db_saved = db.save_papers(ranked_content)
    logger.info(f"Saved {db_saved} items to database")
    
    # Display top 10
    click.echo("\n📊 Top 10 Items:")
    for i, item in enumerate(ranked_content[:10], 1):
        click.echo(f"{i}. [{item['source']}] {item['title']}")
        click.echo(f"   Score: {item.get('score', 0):.2f} | {item['url']}\n")


@cli.command()
@click.option('--count', default=5, help='Number of items to generate content for')
@click.option('--format', type=click.Choice(['blog', 'linkedin', 'medium', 'both', 'all']), 
              default='both', help='Output format (both=blog+linkedin, all=blog+linkedin+medium)')
def generate(count, format):
    """Generate blog articles, LinkedIn posts, and/or Medium articles using Perplexity LLM
    
    Format options:
    - blog: Generate blog articles only
    - linkedin: Generate LinkedIn posts only  
    - medium: Generate comprehensive Medium articles with diagrams
    - both: Generate blog + LinkedIn (default)
    - all: Generate blog + LinkedIn + Medium
    """
    logger.info(f"Generating content for top {count} items...")
    
    # Validate environment variables for content generation
    is_valid, error_msg = validate_required_env_vars('generate')
    if not is_valid:
        click.echo(f"❌ Configuration Error:\n{error_msg}", err=True)
        click.echo("\nPlease add the required environment variables to your .env file")
        return
    
    config = load_config()
    
    # Check if latest.json exists
    json_path = Path('data/fetched/latest.json')
    if not json_path.exists():
        click.echo("❌ No fetched content found. Please run 'fetch' command first:")
        click.echo("   python main.py fetch")
        return
    
    # Load fetched content
    import json
    with open(json_path, 'r') as f:
        items = json.load(f)[:count]
    
    if not items:
        click.echo("❌ No items found. Run 'fetch' command first.")
        return
    
    # Initialize LLM analyzer
    analyzer = ContentAnalyzer(config['llm'])
    
    # Initialize formatters with LLM config
    blog_formatter = BlogFormatter(config['formatting']['blog'], llm_config=config['llm'])
    linkedin_formatter = LinkedInFormatter(config['formatting']['linkedin'], llm_config=config['llm'])
    medium_formatter = MediumFormatter(config['formatting']['medium'], llm_config=config['llm'])
    
    # Initialize database
    db = Database()
    
    generated_count = 0
    
    for i, item in enumerate(items, 1):
        click.echo(f"\n🔄 Processing {i}/{count}: {item['title']}")
        
        try:
            # Determine which analysis to use based on source and format
            if format in ['medium', 'all']:
                # Use comprehensive analysis for Medium
                click.echo(f"  📊 Running comprehensive analysis with diagrams...")
                analysis = analyzer.analyze_for_medium(item)
            elif item.get('source') == 'github':
                # Use ELI5 analysis for GitHub repositories
                click.echo(f"  🎓 Running ELI5 (Explain Like I'm 5) analysis for GitHub repository...")
                analysis = analyzer.analyze_github_eli5(item)
            else:
                # Use standard analysis for other sources
                analysis = analyzer.analyze(item)
            
            # Generate blog article
            if format in ['blog', 'both', 'all']:
                blog_article = blog_formatter.format(item, analysis)
                
                # Save draft to file
                blog_path = Path(f"data/drafts/blog/{item['id']}.md")
                blog_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(blog_path, 'w') as f:
                    f.write(blog_article)
                
                # Save to database with status='drafted'
                content_id = db.save_generated_content(
                    paper_id=item['id'],
                    content_type='blog',
                    content=blog_article,
                    analysis=analysis,
                    file_path=str(blog_path)
                )
                
                click.echo(f"  ✅ Blog article: {blog_path} (DB ID: {content_id})")
            
            # Generate LinkedIn post
            if format in ['linkedin', 'both', 'all']:
                linkedin_post = linkedin_formatter.format(item, analysis)
                
                # Validate content before saving
                is_valid, validation_error = analyzer.validate_linkedin_content(linkedin_post)
                if not is_valid:
                    click.echo(f"  ⚠️  LinkedIn validation failed: {validation_error}")
                    click.echo(f"  Skipping this LinkedIn post")
                else:
                    # Save draft to file
                    linkedin_path = Path(f"data/drafts/linkedin/{item['id']}.txt")
                    linkedin_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(linkedin_path, 'w') as f:
                        f.write(linkedin_post)
                    
                    # Save to database with status='drafted'
                    content_id = db.save_generated_content(
                        paper_id=item['id'],
                        content_type='linkedin',
                        content=linkedin_post,
                        analysis=analysis,
                        file_path=str(linkedin_path)
                    )
                    
                    click.echo(f"  ✅ LinkedIn post: {linkedin_path} (DB ID: {content_id})")
            
            # Generate Medium article (comprehensive with diagrams)
            if format in ['medium', 'all']:
                medium_article = medium_formatter.format(item, analysis)
                
                # Save draft to file
                medium_path = Path(f"data/drafts/medium/{item['id']}.md")
                medium_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(medium_path, 'w', encoding='utf-8') as f:
                    f.write(medium_article)
                
                # Save to database with status='drafted'
                content_id = db.save_generated_content(
                    paper_id=item['id'],
                    content_type='medium',
                    content=medium_article,
                    analysis=analysis,
                    file_path=str(medium_path)
                )
                
                click.echo(f"  ✅ Medium article: {medium_path} (DB ID: {content_id})")
            
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
    medium_drafts = list(Path('data/drafts/medium').glob('*.md'))
    
    click.echo(f"\n📝 Blog Drafts ({len(blog_drafts)}):")
    for draft in blog_drafts:
        click.echo(f"  - {draft.name}")
    
    click.echo(f"\n💼 LinkedIn Drafts ({len(linkedin_drafts)}):")
    for draft in linkedin_drafts:
        click.echo(f"  - {draft.name}")
    
    click.echo(f"\n📰 Medium Drafts ({len(medium_drafts)}):")
    for draft in medium_drafts:
        click.echo(f"  - {draft.name}")
    
    click.echo(f"\nTo view a draft:")
    click.echo(f"  Blog: cat data/drafts/blog/<filename>")
    click.echo(f"  LinkedIn: cat data/drafts/linkedin/<filename>")
    click.echo(f"  Medium: cat data/drafts/medium/<filename>")


@cli.command()
@click.option('--platform', type=click.Choice(['blog', 'linkedin', 'medium', 'both', 'all']), 
              default='both', help='Publishing platform')
@click.option('--approve', is_flag=True, help='Skip approval prompts')
@click.option('--batch-delay', default=300, help='Delay between posts (seconds, default: 5 min)')
@click.option('--limit', default=None, type=int, help='Limit number of posts to publish')
@click.option('--medium-status', type=click.Choice(['public', 'draft', 'unlisted']), 
              default='draft', help='Medium publish status')
def publish(platform, approve, batch_delay, limit, medium_status):
    """Publish approved content with database status tracking"""
    import time
    from datetime import datetime
    
    logger.info(f"Publishing to: {platform}")
    
    config = load_config()
    
    # Initialize publishers only for selected platform
    github_publisher = None
    linkedin_publisher = None
    medium_publisher = None
    
    if platform in ['blog', 'both', 'all']:
        github_publisher = GitHubPagesPublisher(config['publishing']['blog'])
    
    if platform in ['linkedin', 'both', 'all']:
        linkedin_publisher = LinkedInPublisher(config['publishing']['linkedin'])
    
    if platform in ['medium', 'all']:
        medium_publisher = MediumPublisher(config['publishing']['medium'])
    
    # Initialize database
    db = Database()
    
    published_count = 0
    
    # Check LinkedIn credentials before starting
    if platform in ['linkedin', 'both'] and linkedin_publisher:
        if not linkedin_publisher.access_token or not linkedin_publisher.user_id:
            click.echo("\n❌ LinkedIn credentials not configured!")
            click.echo("\n📋 Setup Instructions:")
            click.echo("1. Go to: https://www.linkedin.com/developers/apps")
            click.echo("2. Create a new app or select existing one")
            click.echo("3. Add OAuth 2.0 scopes: w_member_social (for posting)")
            click.echo("4. Generate access token from Auth tab")
            click.echo("5. Get your User ID from: https://www.linkedin.com/in/YOUR-PROFILE (last part of URL)")
            click.echo("\n6. Set environment variables:")
            click.echo("   export LINKEDIN_ACCESS_TOKEN='your_token_here'")
            click.echo("   export LINKEDIN_USER_ID='your_user_id_here'")
            click.echo("\n   Or add to .env file:")
            click.echo("   LINKEDIN_ACCESS_TOKEN=your_token_here")
            click.echo("   LINKEDIN_USER_ID=your_user_id_here")
            click.echo("\n⚠️  Note: Access tokens typically expire after 60 days")
            return
    
    # Publish blog articles
    if platform in ['blog', 'both']:
        blog_drafts = list(Path('data/drafts/blog').glob('*.md'))
        
        if limit:
            blog_drafts = blog_drafts[:limit]
        
        for draft in blog_drafts:
            if not approve:
                click.echo(f"\n📄 Review: {draft.name}")
                with open(draft, 'r') as f:
                    preview = f.read()[:500]
                    click.echo(preview + "...\n")
                
                if not click.confirm("Publish this article?"):
                    continue
            
            try:
                # Publish to GitHub Pages
                success = github_publisher.publish(draft)
                
                if success:
                    click.echo(f"  ✅ Published: {draft.name}")
                    
                    # Update database status
                    try:
                        content_record = db.get_content_by_file_path(str(draft))
                        if content_record:
                            db.update_content_status(
                                content_record['id'], 
                                'published',
                                published_url=github_publisher.get_post_url(draft)
                            )
                            click.echo(f"  📊 Database updated: ID {content_record['id']}")
                        else:
                            click.echo(f"  ⚠️  Draft not in database (created before tracking)")
                    except Exception as db_error:
                        logger.error(f"Database update failed: {db_error}")
                        click.echo(f"  ⚠️  Database update failed: {db_error}")
                        click.echo(f"      Post was published successfully")
                    
                    # Move to published
                    published_path = Path(f"data/published/blog/{draft.name}")
                    published_path.parent.mkdir(parents=True, exist_ok=True)
                    draft.rename(published_path)
                    
                    published_count += 1
                else:
                    click.echo(f"  ❌ Failed to publish: {draft.name}")
                
            except Exception as e:
                logger.error(f"Failed to publish {draft.name}: {e}")
                click.echo(f"  ❌ Error: {e}")
    
    # Publish LinkedIn posts with batch delays
    if platform in ['linkedin', 'both']:
        linkedin_drafts = list(Path('data/drafts/linkedin').glob('*.txt'))
        
        if limit:
            linkedin_drafts = linkedin_drafts[:limit]
        
        total_linkedin = len(linkedin_drafts)
        
        if total_linkedin > 0:
            click.echo(f"\n📅 Best times to post on LinkedIn:")
            click.echo("   • Weekdays: 8-10 AM, 12 PM, 5-6 PM")
            click.echo("   • Avoid: Weekends, late nights")
            current_hour = datetime.now().hour
            if current_hour < 8 or current_hour > 18:
                click.echo(f"   ⚠️  Current time ({datetime.now().strftime('%I:%M %p')}) is outside optimal posting hours")
            
            if total_linkedin > 1:
                total_time = (total_linkedin - 1) * batch_delay
                click.echo(f"\n⏱️  Publishing {total_linkedin} posts with {batch_delay}s delays (~{total_time//60} min total)")
        
        for idx, draft in enumerate(linkedin_drafts, 1):
            if not approve:
                click.echo(f"\n💼 Review [{idx}/{total_linkedin}]: {draft.name}")
                with open(draft, 'r') as f:
                    content = f.read()
                    click.echo(content + "\n")
                
                if not click.confirm("Publish this post?"):
                    continue
            
            try:
                # Publish to LinkedIn
                result = linkedin_publisher.publish(draft)
                
                if result and result.get('success'):
                    post_url = result.get('post_url', '')
                    click.echo(f"  ✅ Published: {draft.name}")
                    if post_url:
                        click.echo(f"  🔗 URL: {post_url}")
                    
                    # Update database status
                    try:
                        content_record = db.get_content_by_file_path(str(draft))
                        if content_record:
                            db.update_content_status(
                                content_record['id'], 
                                'published',
                                published_url=post_url
                            )
                            click.echo(f"  📊 Database updated: ID {content_record['id']} → 'published'")
                        else:
                            click.echo(f"  ⚠️  Draft not in database (created before tracking)")
                    except Exception as db_error:
                        logger.error(f"Database update failed: {db_error}")
                        click.echo(f"  ⚠️  Database update failed: {db_error}")
                        click.echo(f"      Post was published successfully")
                    
                    # Move to published
                    published_path = Path(f"data/published/linkedin/{draft.name}")
                    published_path.parent.mkdir(parents=True, exist_ok=True)
                    draft.rename(published_path)
                    
                    published_count += 1
                    
                    # Add delay between posts (except for last one)
                    if idx < total_linkedin and batch_delay > 0:
                        click.echo(f"  ⏳ Waiting {batch_delay}s before next post...")
                        time.sleep(batch_delay)
                else:
                    click.echo(f"  ❌ Failed to publish: {draft.name}")
                    if result and 'error' in result:
                        click.echo(f"  ℹ️  {result['error']}")
                
            except Exception as e:
                logger.error(f"Failed to publish {draft.name}: {e}")
                click.echo(f"  ❌ Error: {e}")
    
    # Publish Medium articles
    if platform in ['medium', 'all']:
        # Check Medium credentials
        if medium_publisher and not medium_publisher.integration_token:
            click.echo("\n❌ Medium credentials not configured!")
            click.echo("\n📋 Setup Instructions:")
            click.echo("1. Go to: https://medium.com/me/settings")
            click.echo("2. Scroll to 'Integration tokens' section")
            click.echo("3. Enter description (e.g., 'Auto Blog Publisher') and click 'Get integration token'")
            click.echo("4. Copy the token (it will only be shown once)")
            click.echo("\n5. Set environment variable:")
            click.echo("   export MEDIUM_INTEGRATION_TOKEN='your_token_here'")
            click.echo("\n   Or add to .env file:")
            click.echo("   MEDIUM_INTEGRATION_TOKEN=your_token_here")
            click.echo("\n⚠️  Note: Integration tokens don't expire but have rate limits")
            return
        
        medium_drafts = list(Path('data/drafts/medium').glob('*.md'))
        
        if limit:
            medium_drafts = medium_drafts[:limit]
        
        total_medium = len(medium_drafts)
        
        for idx, draft in enumerate(medium_drafts, 1):
            if not approve:
                click.echo(f"\n📰 Review [{idx}/{total_medium}]: {draft.name}")
                with open(draft, 'r', encoding='utf-8') as f:
                    preview = f.read()[:800]
                    click.echo(preview + "...\n")
                
                if not click.confirm("Publish this article to Medium?"):
                    continue
            
            try:
                # Publish to Medium
                result = medium_publisher.publish(draft, publish_status=medium_status)
                
                if result and result.get('success'):
                    post_url = result.get('post_url', '')
                    click.echo(f"  ✅ Published: {draft.name}")
                    if post_url:
                        click.echo(f"  🔗 URL: {post_url}")
                    click.echo(f"  📌 Status: {medium_status}")
                    
                    # Update database status
                    try:
                        content_record = db.get_content_by_file_path(str(draft))
                        if content_record:
                            db.update_content_status(
                                content_record['id'], 
                                'published',
                                published_url=post_url
                            )
                            click.echo(f"  📊 Database updated: ID {content_record['id']}")
                        else:
                            click.echo(f"  ⚠️  Draft not in database (created before tracking)")
                    except Exception as db_error:
                        logger.error(f"Database update failed: {db_error}")
                        click.echo(f"  ⚠️  Database update failed: {db_error}")
                        click.echo(f"      Post was published successfully")
                    
                    # Move to published
                    published_path = Path(f"data/published/medium/{draft.name}")
                    published_path.parent.mkdir(parents=True, exist_ok=True)
                    draft.rename(published_path)
                    
                    published_count += 1
                    
                    # Add delay between posts if needed
                    if idx < total_medium and batch_delay > 0:
                        click.echo(f"  ⏳ Waiting {batch_delay}s before next post...")
                        time.sleep(batch_delay)
                else:
                    click.echo(f"  ❌ Failed to publish: {draft.name}")
                    if result and 'error' in result:
                        click.echo(f"  ℹ️  {result['error']}")
                
            except Exception as e:
                logger.error(f"Failed to publish {draft.name}: {e}")
                click.echo(f"  ❌ Error: {e}")
    
    click.echo(f"\n✨ Published {published_count} items")
    
    # Show database summary
    drafted = db.get_drafted_content()
    click.echo(f"📊 Database Status: {len(drafted)} drafts remaining")


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
        'data/drafts/medium',
        'data/published/blog',
        'data/published/linkedin',
        'data/published/medium',
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


@cli.command()
def generate_index():
    """Generate GitHub Pages index from published blogs in database"""
    logger.info("Generating GitHub Pages index...")
    
    from generate_pages_index import generate_index_json, generate_index_html
    
    try:
        # Generate JSON and HTML
        blog_count = generate_index_json()
        generate_index_html()
        
        click.echo(f"\n✅ Generated GitHub Pages index with {blog_count} blogs")
        click.echo(f"📁 Files created in docs/ directory:")
        click.echo(f"   - index.html (GitHub Pages site)")
        click.echo(f"   - blogs.json (API data)")
        click.echo(f"   - stats.json (Statistics)")
        click.echo(f"\n💡 To enable GitHub Pages:")
        click.echo(f"   1. Go to Settings > Pages in your GitHub repository")
        click.echo(f"   2. Set Source to 'Deploy from a branch'")
        click.echo(f"   3. Select branch and /docs folder")
        click.echo(f"   4. Your site will be available at https://USERNAME.github.io/REPO-NAME/")
        
    except Exception as e:
        logger.error(f"Failed to generate index: {e}")
        click.echo(f"❌ Error: {e}")


@cli.command()
def db_stats():
    """Show database statistics"""
    logger.info("Fetching database statistics...")
    
    db = Database()
    stats = db.get_blog_statistics()
    
    click.echo("\n📊 Database Statistics:")
    click.echo(f"\n📄 Papers:")
    click.echo(f"   Total Papers: {stats.get('total_papers', 0)}")
    click.echo(f"   GitHub Repos: {stats.get('github_repos', 0)}")
    
    click.echo(f"\n📝 Content:")
    content_by_type = stats.get('content_by_type', {})
    for content_type, count in content_by_type.items():
        click.echo(f"   {content_type.title()}: {count}")
    
    click.echo(f"\n📌 Status:")
    content_by_status = stats.get('content_by_status', {})
    for status, count in content_by_status.items():
        click.echo(f"   {status.title()}: {count}")
    
    click.echo(f"\n💻 Top Languages:")
    top_languages = stats.get('top_languages', {})
    for language, count in list(top_languages.items())[:5]:
        click.echo(f"   {language}: {count}")



@cli.command()
@click.option('--max-trends', default=5, help='Maximum number of trends to discover')
@click.option('--generate-content', is_flag=True, help='Generate content for discovered trends')
def discover_trends(max_trends, generate_content):
    """Discover trending AI/ML topics and optionally generate content"""
    logger.info(f"Discovering up to {max_trends} trending topics...")
    
    config = load_config()
    
    # Check if trends source is enabled
    if not config.get('sources', {}).get('trends', {}).get('enabled', False):
        click.echo("❌ Trend discovery is not enabled in config.yaml")
        click.echo("   Set sources.trends.enabled: true to enable")
        return
    
    # Load recent content for analysis
    json_path = Path('data/fetched/latest.json')
    if not json_path.exists():
        click.echo("⚠️  No fetched content found. Running fetch first...")
        # Fetch content
        from sources.arxiv import ArxivFetcher
        from sources.blogs import BlogFetcher
        from sources.hackernews import HackerNewsFetcher
        from sources.github import GitHubFetcher
        
        fetchers = {
            'arxiv': ArxivFetcher(config['sources']['arxiv']),
            'blogs': BlogFetcher(config['sources']['blogs']),
            'hackernews': HackerNewsFetcher(config['sources']['hackernews']),
            'github': GitHubFetcher(config['sources']['github'])
        }
        
        all_content = []
        for name, fetcher in fetchers.items():
            if config['sources'][name].get('enabled', True):
                content = fetcher.fetch()
                all_content.extend(content)
        
        # Save for trend analysis
        import json
        with open(json_path, 'w') as f:
            json.dump(all_content, f, indent=2, default=str)
    else:
        # Load existing content
        import json
        with open(json_path, 'r') as f:
            all_content = json.load(f)
    
    click.echo(f"📊 Analyzing {len(all_content)} recent items for trends...")
    
    # Initialize trend discovery
    trend_engine = TrendDiscovery(config)
    
    # Discover trends
    trends = trend_engine.discover_trends(all_content, max_trends=max_trends)
    
    if not trends:
        click.echo("❌ No trends discovered. Try again later or check LLM configuration.")
        return
    
    # Display discovered trends
    click.echo(f"\n🔥 Discovered {len(trends)} Trending Topics:\n")
    
    for i, trend in enumerate(trends, 1):
        click.echo(f"{i}. {trend.get('topic', 'Unknown')}")
        click.echo(f"   Category: {trend.get('category', 'N/A')}")
        click.echo(f"   Score: {trend.get('composite_score', 0):.1f}/100")
        click.echo(f"   Why now: {trend.get('why_now', 'N/A')[:80]}...")
        click.echo(f"   Engagement: {trend.get('engagement_potential', 0)}/100")
        click.echo()
    
    # Save trends to file
    trends_path = Path('data/trends/latest_trends.json')
    trends_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    from datetime import datetime
    with open(trends_path, 'w') as f:
        json.dump({
            'discovered_at': datetime.now().isoformat(),
            'trends': trends
        }, f, indent=2)
    
    click.echo(f"💾 Saved trends to: {trends_path}")
    
    # Optionally generate content for trends
    if generate_content:
        click.echo(f"\n📝 Generating content for top trend...")
        
        # Convert top trend to content item
        top_trend = trends[0]
        trend_item = trend_engine.generate_trend_content_item(top_trend)
        
        # Generate content
        from llm.analyzer import ContentAnalyzer
        from formatters.linkedin import LinkedInFormatter
        
        analyzer = ContentAnalyzer(config['llm'])
        linkedin_formatter = LinkedInFormatter(config['formatting']['linkedin'], llm_config=config['llm'])
        
        try:
            # Analyze trend
            analysis = analyzer.analyze(trend_item)
            
            # Generate LinkedIn post
            linkedin_post = linkedin_formatter.format(trend_item, analysis)
            
            # Save draft
            linkedin_path = Path(f"data/drafts/linkedin/{trend_item['id']}.txt")
            linkedin_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(linkedin_path, 'w') as f:
                f.write(linkedin_post)
            
            click.echo(f"✅ Generated LinkedIn post: {linkedin_path}")
            click.echo(f"\nPreview:")
            click.echo("─" * 60)
            click.echo(linkedin_post[:500])
            click.echo("─" * 60)
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            click.echo(f"❌ Error: {e}")


@cli.command()
@click.option('--output-dir', default='docs/admin', help='Output directory for JSON exports')
def export_admin(output_dir):
    """Export database to JSON for admin panel"""
    logger.info(f"Exporting database to {output_dir}...")
    
    from export_db_json import export_database_to_json
    
    try:
        result = export_database_to_json(output_dir=output_dir)
        
        click.echo("\n✅ Database export completed!")
        click.echo(f"   Papers exported: {result['papers_count']}")
        click.echo(f"   Content exported: {result['content_count']}")
        click.echo(f"   Output directory: {output_dir}")
        click.echo(f"\n📊 Statistics:")
        stats = result['stats']
        click.echo(f"   Total papers: {stats['total_papers']}")
        click.echo(f"   Total content: {stats['total_content']}")
        click.echo(f"   GitHub repos: {stats.get('github_repos', 0)}")
        
        click.echo(f"\n🌐 Admin panel available at:")
        click.echo(f"   Local: file://{Path(output_dir).absolute()}/index.html")
        click.echo(f"   After deployment: https://YOUR_USERNAME.github.io/YOUR_REPO/admin/")
        
        click.echo(f"\n📚 See {output_dir}/README.md for setup instructions")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        click.echo(f"❌ Export failed: {e}")


if __name__ == '__main__':
    cli()
