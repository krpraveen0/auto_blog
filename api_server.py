#!/usr/bin/env python3
"""
Simple API server for admin panel operations
Provides endpoints for posting content to LinkedIn from the admin panel
"""

import os
import sys
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from utils.database import Database
from publishers.linkedin_api import LinkedInPublisher
import yaml

logger = setup_logger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for admin panel

# Initialize services
db = Database()

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

config = load_config()
linkedin_config = config.get('publishers', {}).get('linkedin', {})
linkedin_publisher = LinkedInPublisher(linkedin_config)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API server is running'
    })


@app.route('/api/content/<int:content_id>', methods=['GET'])
def get_content(content_id):
    """Get content details by ID"""
    try:
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gc.*, p.title as paper_title, p.url as paper_url
            FROM generated_content gc
            JOIN papers p ON gc.paper_id = p.id
            WHERE gc.id = ?
        ''', (content_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Content not found'
            }), 404
        
        content = dict(row)
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        logger.error(f"Error fetching content {content_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/publish/linkedin/<int:content_id>', methods=['POST'])
def publish_to_linkedin(content_id):
    """
    Publish a drafted LinkedIn post to LinkedIn
    
    Args:
        content_id: ID of the content in the database
        
    Returns:
        JSON response with success status and post URL
    """
    try:
        # Validate LinkedIn credentials
        if not linkedin_publisher.access_token or not linkedin_publisher.user_id:
            return jsonify({
                'success': False,
                'error': 'LinkedIn credentials not configured. Please set LINKEDIN_ACCESS_TOKEN and LINKEDIN_USER_ID in .env'
            }), 400
        
        # Get content from database
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gc.*, p.title as paper_title, p.url as paper_url
            FROM generated_content gc
            JOIN papers p ON gc.paper_id = p.id
            WHERE gc.id = ?
        ''', (content_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Content not found'
            }), 404
        
        content_data = dict(row)
        
        # Validate it's LinkedIn content
        if content_data['content_type'] != 'linkedin':
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Content is not a LinkedIn post'
            }), 400
        
        # Check if already published
        if content_data['status'] == 'published':
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Content already published',
                'published_url': content_data.get('published_url')
            }), 400
        
        conn.close()
        
        # Get the content text
        post_content = content_data['content']
        
        # Post to LinkedIn using the public publish method
        # Create a temporary file to match the expected interface
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(post_content)
            tmp_file_path = tmp_file.name
        
        try:
            logger.info(f"Publishing content {content_id} to LinkedIn...")
            result = linkedin_publisher.publish(Path(tmp_file_path))
        finally:
            # Clean up temporary file
            Path(tmp_file_path).unlink(missing_ok=True)
        
        if result.get('success'):
            # Update database status
            db.update_content_status(
                content_id, 
                'published', 
                result.get('post_url')
            )
            
            logger.info(f"Successfully published content {content_id} to LinkedIn")
            return jsonify({
                'success': True,
                'message': 'Successfully published to LinkedIn',
                'post_url': result.get('post_url'),
                'post_id': result.get('post_id')
            })
        else:
            logger.error(f"Failed to publish to LinkedIn: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        logger.error(f"Error publishing to LinkedIn: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/content', methods=['GET'])
def list_content():
    """List all content with optional filtering"""
    try:
        content_type = request.args.get('type')
        status = request.args.get('status')
        
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT gc.*, p.title as paper_title, p.url as paper_url, p.source as paper_source
            FROM generated_content gc
            LEFT JOIN papers p ON gc.paper_id = p.id
            WHERE 1=1
        '''
        params = []
        
        if content_type:
            query += ' AND gc.content_type = ?'
            params.append(content_type)
        
        if status:
            query += ' AND gc.status = ?'
            params.append(status)
        
        query += ' ORDER BY gc.created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        content_list = [dict(row) for row in rows]
        
        return jsonify({
            'success': True,
            'content': content_list,
            'count': len(content_list)
        })
    except Exception as e:
        logger.error(f"Error listing content: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting API server on port {port}...")
    logger.info(f"Admin panel should be accessible at http://localhost:{port}/admin")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
