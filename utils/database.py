"""
SQLite database management for content storage
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from utils.logger import setup_logger
import json

logger = setup_logger(__name__)


class Database:
    """Manage SQLite database for content storage"""
    
    def __init__(self, db_path: str = "data/research.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create papers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                pdf_url TEXT,
                summary TEXT,
                authors TEXT,
                published TEXT,
                updated TEXT,
                category TEXT,
                categories TEXT,
                primary_category TEXT,
                source TEXT NOT NULL,
                source_priority TEXT,
                score REAL DEFAULT 0.0,
                fetched_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create content table for generated content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content TEXT NOT NULL,
                analysis TEXT,
                file_path TEXT,
                status TEXT DEFAULT 'drafted',
                published_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                published_at TEXT,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            )
        ''')
        
        # Check for missing columns in papers table and add them (auto-migration)
        cursor.execute('PRAGMA table_info(papers)')
        existing_papers_columns = [col[1] for col in cursor.fetchall()]
        
        papers_migrations = []
        
        # Add GitHub-specific statistics columns
        github_columns = {
            'stars': 'INTEGER DEFAULT 0',
            'forks': 'INTEGER DEFAULT 0',
            'watchers': 'INTEGER DEFAULT 0',
            'open_issues': 'INTEGER DEFAULT 0',
            'language': 'TEXT',
            'topics': 'TEXT',  # JSON array
            'license': 'TEXT',
            'languages': 'TEXT',  # JSON object
            'contributors_count': 'INTEGER DEFAULT 0',
            'owner_type': 'TEXT',
            'stars_per_day': 'REAL DEFAULT 0.0',
            'forks_per_day': 'REAL DEFAULT 0.0',
            'activity_score': 'REAL DEFAULT 0.0',
            'days_since_creation': 'INTEGER DEFAULT 0',
            'days_since_update': 'INTEGER DEFAULT 0',
            'is_recently_active': 'INTEGER DEFAULT 0',  # Boolean as INTEGER
            'has_wiki': 'INTEGER DEFAULT 0',
            'has_pages': 'INTEGER DEFAULT 0',
            'has_discussions': 'INTEGER DEFAULT 0',
        }
        
        for col_name, col_type in github_columns.items():
            if col_name not in existing_papers_columns:
                cursor.execute(f'ALTER TABLE papers ADD COLUMN {col_name} {col_type}')
                papers_migrations.append(col_name)
                logger.info(f"✓ Added {col_name} column to papers table")
        
        # Check for missing columns in generated_content table
        cursor.execute('PRAGMA table_info(generated_content)')
        existing_content_columns = [col[1] for col in cursor.fetchall()]
        
        content_migrations = []
        if 'file_path' not in existing_content_columns:
            cursor.execute('ALTER TABLE generated_content ADD COLUMN file_path TEXT')
            content_migrations.append('file_path')
            logger.info("✓ Added file_path column to generated_content table")
        
        if 'published_url' not in existing_content_columns:
            cursor.execute('ALTER TABLE generated_content ADD COLUMN published_url TEXT')
            content_migrations.append('published_url')
            logger.info("✓ Added published_url column to generated_content table")
        
        all_migrations = papers_migrations + content_migrations
        if all_migrations:
            logger.info(f"Database migration completed: {len(all_migrations)} columns added")
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_source ON papers(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_published ON papers(published)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_status ON generated_content(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_stars ON papers(stars)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_activity ON papers(activity_score)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_papers(self, papers: List[Dict]) -> int:
        """Save fetched papers to database with all GitHub statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for paper in papers:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO papers 
                    (id, title, url, pdf_url, summary, authors, published, updated,
                     category, categories, primary_category, source, source_priority,
                     score, fetched_at, stars, forks, watchers, open_issues, language,
                     topics, license, languages, contributors_count, owner_type,
                     stars_per_day, forks_per_day, activity_score, days_since_creation,
                     days_since_update, is_recently_active, has_wiki, has_pages, has_discussions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    paper.get('id'),
                    paper.get('title'),
                    paper.get('url'),
                    paper.get('pdf_url'),
                    paper.get('summary'),
                    json.dumps(paper.get('authors', [])),
                    paper.get('published'),
                    paper.get('updated'),
                    paper.get('category'),
                    json.dumps(paper.get('categories', [])),
                    paper.get('primary_category'),
                    paper.get('source'),
                    paper.get('source_priority'),
                    paper.get('score', 0.0),
                    paper.get('fetched_at'),
                    # GitHub statistics
                    paper.get('stars', 0),
                    paper.get('forks', 0),
                    paper.get('watchers', 0),
                    paper.get('open_issues', 0),
                    paper.get('language', ''),
                    json.dumps(paper.get('topics', [])),
                    paper.get('license', ''),
                    json.dumps(paper.get('languages', {})),
                    paper.get('contributors_count', 0),
                    paper.get('owner_type', ''),
                    paper.get('stars_per_day', 0.0),
                    paper.get('forks_per_day', 0.0),
                    paper.get('activity_score', 0.0),
                    paper.get('days_since_creation', 0),
                    paper.get('days_since_update', 0),
                    1 if paper.get('is_recently_active') else 0,
                    1 if paper.get('has_wiki') else 0,
                    1 if paper.get('has_pages') else 0,
                    1 if paper.get('has_discussions') else 0,
                ))
                saved_count += 1
            except Exception as e:
                logger.error(f"Failed to save paper {paper.get('id')}: {e}")
                logger.error(f"Paper data: {paper.get('title', 'Unknown')}")
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {saved_count} papers to database")
        return saved_count
    
    def get_papers(self, limit: int = 10, status: Optional[str] = None) -> List[Dict]:
        """Retrieve papers from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT p.*, 
                   gc.status as content_status,
                   gc.content_type
            FROM papers p
            LEFT JOIN generated_content gc ON p.id = gc.paper_id
            ORDER BY p.published DESC
            LIMIT ?
        '''
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        papers = []
        for row in rows:
            paper = dict(row)
            # Parse JSON fields
            if paper.get('authors'):
                paper['authors'] = json.loads(paper['authors'])
            if paper.get('categories'):
                paper['categories'] = json.loads(paper['categories'])
            papers.append(paper)
        
        conn.close()
        return papers
    
    def save_generated_content(self, paper_id: str, content_type: str, 
                               content: str, analysis: Optional[Dict] = None,
                               file_path: Optional[str] = None) -> int:
        """Save generated content to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO generated_content 
            (paper_id, content_type, content, analysis, file_path, status)
            VALUES (?, ?, ?, ?, ?, 'drafted')
        ''', (
            paper_id,
            content_type,
            content,
            json.dumps(analysis) if analysis else None,
            file_path
        ))
        
        content_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Saved {content_type} content for paper {paper_id}")
        return content_id
    
    def update_content_status(self, content_id: int, status: str, published_url: Optional[str] = None):
        """Update content status (drafted, published, etc.)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE generated_content 
            SET status = ?, published_at = ?, published_url = ?
            WHERE id = ?
        ''', (status, datetime.now().isoformat() if status == 'published' else None, published_url, content_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated content {content_id} status to {status}")
    
    def get_drafted_content(self, content_type: Optional[str] = None) -> List[Dict]:
        """Get all drafted content"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if content_type:
            cursor.execute('''
                SELECT gc.*, p.title, p.url
                FROM generated_content gc
                JOIN papers p ON gc.paper_id = p.id
                WHERE gc.status = 'drafted' AND gc.content_type = ?
                ORDER BY gc.created_at DESC
            ''', (content_type,))
        else:
            cursor.execute('''
                SELECT gc.*, p.title, p.url
                FROM generated_content gc
                JOIN papers p ON gc.paper_id = p.id
                WHERE gc.status = 'drafted'
                ORDER BY gc.created_at DESC
            ''')
        
        rows = cursor.fetchall()
        content = [dict(row) for row in rows]
        
        conn.close()
        return content
    
    def get_content_by_file_path(self, file_path: str) -> Optional[Dict]:
        """Get content record by file path"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gc.*, p.title, p.url
            FROM generated_content gc
            JOIN papers p ON gc.paper_id = p.id
            WHERE gc.file_path = ?
        ''', (file_path,))
        
        row = cursor.fetchone()
        result = dict(row) if row else None
        
        conn.close()
        return result
    
    def export_blogs_for_pages(self, status: str = 'published', limit: Optional[int] = None) -> List[Dict]:
        """
        Export published blog content with paper metadata for GitHub Pages display
        
        Args:
            status: Content status to filter by (default: 'published')
            limit: Maximum number of blogs to export (optional)
            
        Returns:
            List of blog dictionaries with metadata
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                gc.id as content_id,
                gc.content,
                gc.content_type,
                gc.status,
                gc.published_url,
                gc.published_at,
                gc.created_at,
                p.id as paper_id,
                p.title,
                p.url,
                p.summary,
                p.published,
                p.updated,
                p.source,
                p.stars,
                p.forks,
                p.watchers,
                p.open_issues,
                p.language,
                p.topics,
                p.license,
                p.languages,
                p.contributors_count,
                p.stars_per_day,
                p.activity_score,
                p.is_recently_active
            FROM generated_content gc
            JOIN papers p ON gc.paper_id = p.id
            WHERE gc.content_type = 'blog' AND gc.status = ?
            ORDER BY gc.published_at DESC, gc.created_at DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (status,))
        rows = cursor.fetchall()
        
        blogs = []
        for row in rows:
            blog = dict(row)
            # Parse JSON fields
            if blog.get('topics'):
                try:
                    blog['topics'] = json.loads(blog['topics'])
                except:
                    blog['topics'] = []
            if blog.get('languages'):
                try:
                    blog['languages'] = json.loads(blog['languages'])
                except:
                    blog['languages'] = {}
            blogs.append(blog)
        
        conn.close()
        logger.info(f"Exported {len(blogs)} blogs for GitHub Pages")
        return blogs
    
    def get_blog_statistics(self) -> Dict:
        """Get statistics about blogs in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total papers
        cursor.execute('SELECT COUNT(*) FROM papers')
        stats['total_papers'] = cursor.fetchone()[0]
        
        # Total content by type
        cursor.execute('SELECT content_type, COUNT(*) FROM generated_content GROUP BY content_type')
        stats['content_by_type'] = dict(cursor.fetchall())
        
        # Content by status
        cursor.execute('SELECT status, COUNT(*) FROM generated_content GROUP BY status')
        stats['content_by_status'] = dict(cursor.fetchall())
        
        # GitHub repos stats
        cursor.execute('SELECT COUNT(*) FROM papers WHERE source = "github"')
        stats['github_repos'] = cursor.fetchone()[0]
        
        # Top languages
        cursor.execute('''
            SELECT language, COUNT(*) as count 
            FROM papers 
            WHERE language IS NOT NULL AND language != ""
            GROUP BY language 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        stats['top_languages'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
