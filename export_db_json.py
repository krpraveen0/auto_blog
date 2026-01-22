#!/usr/bin/env python3
"""
Export SQLite database to JSON for admin panel consumption
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from utils.logger import setup_logger

logger = setup_logger(__name__)


def export_database_to_json(db_path: str = "data/research.db", output_dir: str = "docs/admin"):
    """
    Export all database tables to JSON files for client-side querying
    
    Args:
        db_path: Path to SQLite database
        output_dir: Directory to store JSON exports
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Export papers table
    cursor.execute('''
        SELECT 
            id, title, url, pdf_url, summary, authors, published, updated,
            category, categories, primary_category, source, source_priority,
            score, fetched_at, created_at, stars, forks, watchers, open_issues,
            language, topics, license, languages, contributors_count, owner_type,
            stars_per_day, forks_per_day, activity_score, days_since_creation,
            days_since_update, is_recently_active, has_wiki, has_pages, has_discussions
        FROM papers
        ORDER BY created_at DESC
    ''')
    
    papers = []
    for row in cursor.fetchall():
        paper = dict(row)
        # Parse JSON fields safely
        for field in ['authors', 'categories', 'topics', 'languages']:
            if paper.get(field):
                try:
                    paper[field] = json.loads(paper[field])
                except (json.JSONDecodeError, TypeError):
                    paper[field] = [] if field != 'languages' else {}
        papers.append(paper)
    
    # Export generated_content table
    cursor.execute('''
        SELECT 
            gc.id, gc.paper_id, gc.content_type, gc.content, gc.analysis,
            gc.file_path, gc.status, gc.published_url, gc.created_at, gc.published_at,
            p.title as paper_title, p.url as paper_url, p.source as paper_source
        FROM generated_content gc
        LEFT JOIN papers p ON gc.paper_id = p.id
        ORDER BY gc.created_at DESC
    ''')
    
    content = []
    for row in cursor.fetchall():
        item = dict(row)
        # Parse analysis if present
        if item.get('analysis'):
            try:
                item['analysis'] = json.loads(item['analysis'])
            except (json.JSONDecodeError, TypeError):
                item['analysis'] = None
        content.append(item)
    
    # Get database statistics
    cursor.execute('SELECT COUNT(*) FROM papers')
    total_papers = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM generated_content')
    total_content = cursor.fetchone()[0]
    
    cursor.execute('SELECT content_type, COUNT(*) FROM generated_content GROUP BY content_type')
    content_by_type = dict(cursor.fetchall())
    
    cursor.execute('SELECT status, COUNT(*) FROM generated_content GROUP BY status')
    content_by_status = dict(cursor.fetchall())
    
    cursor.execute('SELECT source, COUNT(*) FROM papers GROUP BY source')
    papers_by_source = dict(cursor.fetchall())
    
    cursor.execute('''
        SELECT language, COUNT(*) as count 
        FROM papers 
        WHERE language IS NOT NULL AND language != ""
        GROUP BY language 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    top_languages = dict(cursor.fetchall())
    
    stats = {
        'total_papers': total_papers,
        'total_content': total_content,
        'content_by_type': content_by_type,
        'content_by_status': content_by_status,
        'papers_by_source': papers_by_source,
        'top_languages': top_languages,
        'last_updated': datetime.now(timezone.utc).isoformat()
    }
    
    conn.close()
    
    # Write JSON files
    with open(output_path / 'papers.json', 'w') as f:
        json.dump(papers, f, indent=2)
    logger.info(f"Exported {len(papers)} papers to {output_path / 'papers.json'}")
    
    with open(output_path / 'content.json', 'w') as f:
        json.dump(content, f, indent=2)
    logger.info(f"Exported {len(content)} content items to {output_path / 'content.json'}")
    
    with open(output_path / 'stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Exported statistics to {output_path / 'stats.json'}")
    
    # Create a combined export with metadata
    export_data = {
        'version': '1.0',
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'stats': stats,
        'papers': papers,
        'content': content
    }
    
    with open(output_path / 'database.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    logger.info(f"Created combined database export at {output_path / 'database.json'}")
    
    return {
        'papers_count': len(papers),
        'content_count': len(content),
        'stats': stats
    }


if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/research.db"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "docs/admin"
    
    result = export_database_to_json(db_path, output_dir)
    print(f"\n✓ Database export completed!")
    print(f"  Papers: {result['papers_count']}")
    print(f"  Content: {result['content_count']}")
    print(f"  Output directory: {output_dir}")
