import sqlite3
import pathlib
from typing import List, Optional, Dict, Any

DB_PATH = pathlib.Path(__file__).parent.parent / "storage.db"

def init_db() -> None:
    """Initialize the SQLite database and create necessary tables."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Drop and recreate table to add status column
        cursor.execute('DROP TABLE IF EXISTS processed_articles')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                summary TEXT,
                published TEXT,
                tags TEXT,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        ''')
        
        # Create metadata table for scheduling
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduler_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        conn.commit()

def has_article(url: str) -> bool:
    """Check if an article with the given URL exists in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM processed_articles WHERE url = ?', (url,))
        return cursor.fetchone() is not None

def add_article(url: str, title: str, summary: str, published: str, tags: List[str]) -> None:
    """Add a new article to the database. Ignores if URL already exists."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO processed_articles (url, title, summary, published, tags) VALUES (?, ?, ?, ?, ?)',
                (url, title, summary, published, ','.join(tags))
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # URL already exists, silently ignore
            pass

def list_processed_urls() -> List[str]:
    """Return a list of all processed article URLs."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT url FROM processed_articles')
        return [row[0] for row in cursor.fetchall()]

def count_pending_articles() -> int:
    """Return the count of articles with 'pending' status."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM processed_articles WHERE status = ?', ('pending',))
        return cursor.fetchone()[0]

def get_next_pending_article() -> Optional[Dict[str, Any]]:
    """
    Return the oldest pending article as a dictionary.
    Returns None if no pending articles exist.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, url, title, summary, published, tags
            FROM processed_articles 
            WHERE status = 'pending'
            ORDER BY published ASC
            LIMIT 1
        ''')
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'url': row[1],
                'link': row[1],  # Add link as alias for url
                'title': row[2],
                'summary': row[3],
                'published': row[4],
                'tags': row[5].split(',') if row[5] else []
            }
        return None

def mark_article_sent(article_id: int) -> None:
    """Mark an article as sent by its ID."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE processed_articles SET status = ? WHERE id = ?',
            ('sent', article_id)
        )
        conn.commit()

def save_last_publish_ts(ts: float) -> None:
    """Save the last publish timestamp to metadata table."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO scheduler_meta (key, value) VALUES (?, ?)',
            ('last_publish_ts', str(ts))
        )
        conn.commit()

def load_last_publish_ts() -> float:
    """Load the last publish timestamp from metadata table."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM scheduler_meta WHERE key = ?', ('last_publish_ts',))
        row = cursor.fetchone()
        return float(row[0]) if row else 0.0