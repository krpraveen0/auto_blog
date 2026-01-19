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
        
        # Check for missing columns and add them (auto-migration)
        cursor.execute('PRAGMA table_info(generated_content)')
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        migrations_applied = []
        if 'file_path' not in existing_columns:
            cursor.execute('ALTER TABLE generated_content ADD COLUMN file_path TEXT')
            migrations_applied.append('file_path')
            logger.info("✓ Added file_path column to generated_content table")
        
        if 'published_url' not in existing_columns:
            cursor.execute('ALTER TABLE generated_content ADD COLUMN published_url TEXT')
            migrations_applied.append('published_url')
            logger.info("✓ Added published_url column to generated_content table")
        
        if migrations_applied:
            logger.info(f"Database migration completed: {', '.join(migrations_applied)}")
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_source ON papers(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_published ON papers(published)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_status ON generated_content(status)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_papers(self, papers: List[Dict]) -> int:
        """Save fetched papers to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for paper in papers:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO papers 
                    (id, title, url, pdf_url, summary, authors, published, updated,
                     category, categories, primary_category, source, source_priority,
                     score, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    paper.get('fetched_at')
                ))
                saved_count += 1
            except Exception as e:
                logger.error(f"Failed to save paper {paper.get('id')}: {e}")
        
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
