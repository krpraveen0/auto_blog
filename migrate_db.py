#!/usr/bin/env python3
"""
Database migration script to add file_path and published_url columns
"""

import sqlite3
from pathlib import Path

def migrate_database():
    """Add new columns to existing database"""
    db_path = Path('data/research.db')
    
    if not db_path.exists():
        print("❌ Database not found. Run 'python main.py fetch' first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute('PRAGMA table_info(generated_content)')
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    print("Current columns:", existing_columns)
    print()
    
    # Add missing columns
    migrations_applied = 0
    
    if 'file_path' not in existing_columns:
        print("📝 Adding file_path column...")
        cursor.execute('ALTER TABLE generated_content ADD COLUMN file_path TEXT')
        print("✅ Added file_path")
        migrations_applied += 1
    else:
        print("⏭️  file_path column already exists")
    
    if 'published_url' not in existing_columns:
        print("📝 Adding published_url column...")
        cursor.execute('ALTER TABLE generated_content ADD COLUMN published_url TEXT')
        print("✅ Added published_url")
        migrations_applied += 1
    else:
        print("⏭️  published_url column already exists")
    
    conn.commit()
    
    # Verify final schema
    cursor.execute('PRAGMA table_info(generated_content)')
    final_columns = cursor.fetchall()
    
    print()
    print("📊 Final Schema:")
    print("-" * 60)
    for col in final_columns:
        col_id, name, type_, notnull, default, pk = col
        print(f"  {name:20} {type_:10} {'PK' if pk else ''}")
    
    conn.close()
    
    print()
    if migrations_applied > 0:
        print(f"🎉 Migration complete! Applied {migrations_applied} changes.")
    else:
        print("✅ Database already up to date!")
    
    print()
    print("💡 Next steps:")
    print("   1. Generate new content: python main.py generate --count 1")
    print("   2. File paths will be automatically saved to database")
    print("   3. Publish content: python main.py publish --platform linkedin")

if __name__ == '__main__':
    migrate_database()
