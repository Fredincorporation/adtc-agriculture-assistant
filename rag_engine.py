\import sqlite3
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Read HF_TOKEN from environment instead of hardcoding
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token

# Suppress warnings
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

DB_PATH = os.path.join(os.path.dirname(__file__), "agriculture.db")
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT,
            title TEXT,
            topic TEXT,
            content TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    conn.close()

def query_knowledge_base(query, top_k=4):
    if not os.path.exists(DB_PATH):
        return ""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT content, embedding FROM knowledge_base WHERE embedding IS NOT NULL")
    rows = cursor.fetchall()
    
    if not rows:
        # Fallback to basic text match if embeddings aren't populated
        cursor.execute("SELECT content FROM knowledge_base LIMIT ?", (top_k,))
        results = [r[0] for r in cursor.fetchall()]
        conn.close()
        return "\n\n".join(results)
    
    model = get_model()
    query_emb = model.encode(query, normalize_embeddings=True)
    
    scored_results = []
    for content, emb_blob in rows:
        emb = pickle.loads(emb_blob)
        similarity = np.dot(query_emb, emb)
        scored_results.append((similarity, content))
    
    conn.close()
    
    # Sort by similarity score descending
    scored_results.sort(key=lambda x: x[0], reverse=True)
    top_results = [item[1] for item in scored_results[:top_k]]
    
    return "\n\n".join(top_results)
