import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "cache.db")

def init_cache_db():
    """Initialize the SQLite cache database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS response_cache (
            query TEXT PRIMARY KEY,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_cached_response(query: str):
    """Retrieve a cached answer if it exists."""
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM response_cache WHERE query = ?", (query.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def cache_response(query: str, response: str):
    """Save a query and response pair to the cache."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO response_cache (query, response) VALUES (?, ?)",
        (query.strip().lower(), response)
    )
    conn.commit()
    conn.close()
