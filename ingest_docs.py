import os
import glob
import sqlite3
import numpy as np

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from rag_engine import init_db, DB_PATH

DOCS_DIR = "./knowledge_docs"

def parse_and_ingest():
    init_db()
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"[!] Created directory '{DOCS_DIR}'. Drop .txt or .md agronomy manuals there.")
        return

    files = glob.glob(f"{DOCS_DIR}/*.txt") + glob.glob(f"{DOCS_DIR}/*.md")
    if not files:
        print(f"[!] No files found in '{DOCS_DIR}'. Drop text files to ingest.")
        return

    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    count = 0
    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Extract basic header info or fallback to filename
        lines = content.splitlines()
        title = lines[0].replace("#", "").strip() if lines else filename
        crop = filename.split("_")[0].capitalize() if "_" in filename else "General"
        topic = "Extension Guidance"

        text_to_embed = f"{crop} {topic} {title} {content}"
        vec = embedder.encode(text_to_embed).astype(np.float32).tobytes()

        cursor.execute("""
            INSERT INTO knowledge_base (crop, topic, title, content, embedding)
            VALUES (?, ?, ?, ?, ?)
        """, (crop, topic, title, content, vec))
        count += 1
        print(f"   [✓] Ingested: [{crop}] {title} ({filename})")

    conn.commit()
    conn.close()
    print(f"\n[✓] Successfully ingested {count} documents into {DB_PATH}.")

if __name__ == "__main__":
    parse_and_ingest()
