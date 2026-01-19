"""
Generate GitHub Pages index from database
Creates an index page that displays all published blogs
"""

import json
from pathlib import Path
from datetime import datetime
from utils.database import Database
from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_index_json():
    """Generate JSON file with all published blogs for GitHub Pages"""
    db = Database()
    
    # Get all published blogs
    blogs = db.export_blogs_for_pages(status='published', limit=100)
    
    # Get statistics
    stats = db.get_blog_statistics()
    
    # Create output directory
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    # Write blogs JSON
    blogs_file = output_dir / 'blogs.json'
    with open(blogs_file, 'w', encoding='utf-8') as f:
        json.dump(blogs, f, indent=2, default=str)
    
    logger.info(f"Generated {blogs_file} with {len(blogs)} blogs")
    
    # Write stats JSON
    stats_file = output_dir / 'stats.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"Generated {stats_file}")
    
    return len(blogs)


def generate_index_html():
    """Generate simple HTML index page for GitHub Pages"""
    db = Database()
    
    # Get all published blogs
    blogs = db.export_blogs_for_pages(status='published', limit=100)
    stats = db.get_blog_statistics()
    
    # Create HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Research Blog - Auto Generated Content</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            margin-bottom: 30px;
        }}
        
        header h1 {{
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            text-align: center;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card h3 {{
            font-size: 2em;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card p {{
            color: #666;
        }}
        
        .filters {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .filters input {{
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
        }}
        
        .blog-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }}
        
        .blog-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .blog-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}
        
        .blog-card h2 {{
            font-size: 1.4em;
            margin-bottom: 10px;
            color: #333;
        }}
        
        .blog-card h2 a {{
            color: #333;
            text-decoration: none;
        }}
        
        .blog-card h2 a:hover {{
            color: #667eea;
        }}
        
        .blog-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .badge-source {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge-github {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}
        
        .badge-language {{
            background: #fff3e0;
            color: #f57c00;
        }}
        
        .blog-stats {{
            display: flex;
            gap: 15px;
            margin-top: 15px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .blog-summary {{
            color: #666;
            margin: 15px 0;
            line-height: 1.6;
        }}
        
        .blog-date {{
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
            font-size: 1.2em;
        }}
        
        footer {{
            text-align: center;
            padding: 40px 20px;
            color: #999;
            margin-top: 60px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🤖 AI Research Blog</h1>
            <p>Automatically generated content about trending AI/ML projects and research</p>
        </div>
    </header>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>{stats.get('total_papers', 0)}</h3>
                <p>Total Papers</p>
            </div>
            <div class="stat-card">
                <h3>{len(blogs)}</h3>
                <p>Published Blogs</p>
            </div>
            <div class="stat-card">
                <h3>{stats.get('github_repos', 0)}</h3>
                <p>GitHub Repos</p>
            </div>
            <div class="stat-card">
                <h3>{stats.get('content_by_status', {}).get('drafted', 0)}</h3>
                <p>Drafts</p>
            </div>
        </div>
        
        <div class="filters">
            <input type="text" id="searchInput" placeholder="🔍 Search blogs by title, language, or topic..." onkeyup="filterBlogs()">
        </div>
        
        <div class="blog-grid" id="blogGrid">
"""
    
    # Add blog cards
    for blog in blogs:
        title = blog.get('title', 'Untitled')
        url = blog.get('url', '#')
        summary = blog.get('summary', '')[:200] + '...' if blog.get('summary') else 'No description available'
        published_at = blog.get('published_at', blog.get('created_at', ''))
        
        # Format date
        try:
            date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%B %d, %Y')
        except:
            formatted_date = 'Recent'
        
        source = blog.get('source', 'unknown')
        language = blog.get('language', '')
        stars = blog.get('stars', 0)
        forks = blog.get('forks', 0)
        
        topics = blog.get('topics', [])
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except:
                topics = []
        
        topics_html = ' '.join([f'<span class="badge badge-language">#{topic}</span>' for topic in topics[:3]])
        
        html += f"""
            <div class="blog-card" data-title="{title.lower()}" data-language="{language.lower()}" data-topics="{' '.join(topics).lower()}">
                <h2><a href="{url}" target="_blank">{title}</a></h2>
                <div class="blog-meta">
                    <span class="badge badge-source">{source.upper()}</span>
"""
        
        if source == 'github':
            html += f'                    <span class="badge badge-github">GitHub</span>\n'
            if language:
                html += f'                    <span class="badge badge-language">{language}</span>\n'
        
        html += f"""
                </div>
                {topics_html}
                <p class="blog-summary">{summary}</p>
"""
        
        if source == 'github' and (stars > 0 or forks > 0):
            html += f"""
                <div class="blog-stats">
"""
            if stars > 0:
                html += f'                    <span>⭐ {stars:,} stars</span>\n'
            if forks > 0:
                html += f'                    <span>🔱 {forks:,} forks</span>\n'
            html += """
                </div>
"""
        
        html += f"""
                <p class="blog-date">Published: {formatted_date}</p>
            </div>
"""
    
    # Close HTML
    html += """
        </div>
        
        <div class="no-results" id="noResults" style="display: none;">
            No blogs found matching your search.
        </div>
    </div>
    
    <footer>
        <p>Generated by Auto Blog Publisher | Last updated: """ + datetime.now().strftime('%B %d, %Y %H:%M UTC') + """</p>
        <p>All content is AI-generated from trusted sources</p>
    </footer>
    
    <script>
        function filterBlogs() {
            const searchInput = document.getElementById('searchInput');
            const filter = searchInput.value.toLowerCase();
            const blogGrid = document.getElementById('blogGrid');
            const cards = blogGrid.getElementsByClassName('blog-card');
            const noResults = document.getElementById('noResults');
            
            let visibleCount = 0;
            
            for (let i = 0; i < cards.length; i++) {
                const card = cards[i];
                const title = card.getAttribute('data-title');
                const language = card.getAttribute('data-language');
                const topics = card.getAttribute('data-topics');
                
                const searchText = title + ' ' + language + ' ' + topics;
                
                if (searchText.indexOf(filter) > -1) {
                    card.style.display = '';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            }
            
            if (visibleCount === 0) {
                blogGrid.style.display = 'none';
                noResults.style.display = 'block';
            } else {
                blogGrid.style.display = 'grid';
                noResults.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""
    
    # Write HTML file
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)
    
    index_file = output_dir / 'index.html'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Generated {index_file}")
    
    return len(blogs)


if __name__ == '__main__':
    print("Generating GitHub Pages index...")
    
    # Generate both JSON and HTML
    blog_count = generate_index_json()
    generate_index_html()
    
    print(f"✅ Generated index with {blog_count} blogs")
    print(f"📁 Files created in docs/ directory")
    print(f"   - index.html (GitHub Pages site)")
    print(f"   - blogs.json (API data)")
    print(f"   - stats.json (Statistics)")
