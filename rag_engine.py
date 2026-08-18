import sqlite3
import pickle
import os

# Suppress Hugging Face download warnings & progress outputs
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Read HF_TOKEN from environment if set
hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token

from sentence_transformers import SentenceTransformer

DB_PATH = "agriculture.db"
MODEL_NAME = "all-MiniLM-L6-v2"

# Lazy-load embedding model
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
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

def query_knowledge_base(query: str, top_k: int = 4) -> str:
    if not os.path.exists(DB_PATH):
        return ""

    model = get_model()
    query_emb = model.encode(query, normalize_embeddings=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT crop, title, topic, content, embedding FROM knowledge_base")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return ""

    results = []
    for crop, title, topic, content, emb_blob in rows:
        doc_emb = pickle.loads(emb_blob)
        # Cosine similarity for normalized vectors
        score = float(query_emb @ doc_emb)
        results.append((score, crop, title, topic, content))

    results.sort(key=lambda x: float(x[0]), reverse=True)
    top_matches = results[:top_k]

    context_str = "\n\n".join([
        f"[{crop} - {title}]\n{content}"
        for _, crop, title, topic, content in top_matches
    ])

    return context_str
