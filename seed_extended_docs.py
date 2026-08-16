#!/usr/bin/env python3
import os
import sqlite3
import numpy as np

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from rag_engine import init_db, DB_PATH

init_db()
embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)

EXTENDED_DOCS = [
    {
        "crop": "Yam",
        "topic": "Fertilization & Soil Health",
        "title": "Yam Fertilizer Application Guide",
        "content": "Yam requires soil rich in organic matter and potassium. Apply NPK 15-15-15 at 200–300 kg/ha at 8–10 weeks after emergence when vines develop. Top-dress with Muriate of Potash (MOP) at vine branching to promote tuber elongation."
    },
    {
        "crop": "Yam",
        "topic": "Pest & Disease Control",
        "title": "Yam Anthracnose Disease Management",
        "content": "Yam Anthracnose causes leaf necrosis and vine dieback. Prevent outbreaks by planting disease-free seed tubers, practicing crop rotation with non-host crops, and applying copper-based fungicides at early symptoms."
    },
    {
        "crop": "Sorghum",
        "topic": "Fertilization & Agronomy",
        "title": "Sorghum Nutrient & Water Management Guide",
        "content": "Sorghum is drought-tolerant. Apply NPK 15-15-15 at 150–200 kg/ha as basal application during planting. Top-dress with Urea at 50–100 kg/ha at 3–4 weeks after emergence."
    },
    {
        "crop": "Rice",
        "topic": "Fertilization & Soil Health",
        "title": "Lowland & Upland Rice Fertilizer Schedule",
        "content": "For lowland rice, apply NPK 15-15-15 at 200 kg/ha at basal planting. Split top-dressing with Urea: 50 kg/ha at tillering (21 days post-transplant) and 50 kg/ha at panicle initiation (45–50 days)."
    },
    {
        "crop": "Tomato",
        "topic": "Pest & Disease Control",
        "title": "Tomato Early & Late Blight Management",
        "content": "Tomato blight causes brown leaf spots and stem rotting. Control via staking, avoiding overhead irrigation, removing infected leaves, and applying Mancozeb fungicides."
    },
    {
        "crop": "Plantain",
        "topic": "Soil Fertility & Mulching",
        "title": "Plantain Organic & Inorganic Fertilizer Requirements",
        "content": "Plantain requires high potassium and organic mulch. Apply 300–400 kg/ha NPK 12-12-17 split across 3 applications yearly. Maintain deep organic mulch around sucker mats."
    },
    {
        "crop": "Cocoa",
        "topic": "Pruning & Soil Health",
        "title": "Cocoa Establishment & Shade Management",
        "content": "Apply Cocoa NPK 0-20-20 or 12-24-12 during pod formation (200–300 g per tree). Maintain 30–40% canopy shade and prune chupons twice yearly to reduce Black Pod disease."
    }
]

def seed_extended_knowledge():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    added_count = 0
    for doc in EXTENDED_DOCS:
        cursor.execute("SELECT id FROM knowledge_base WHERE title = ?", (doc['title'],))
        if cursor.fetchone():
            continue

        text_to_embed = f"{doc['crop']} {doc['topic']} {doc['title']} {doc['content']}"
        vec = embedder.encode(text_to_embed).astype(np.float32).tobytes()

        cursor.execute("""
            INSERT INTO knowledge_base (crop, topic, title, content, embedding)
            VALUES (?, ?, ?, ?, ?)
        """, (doc['crop'], doc['topic'], doc['title'], doc['content'], vec))
        added_count += 1
        print(f"   [✓] Indexed: [{doc['crop']}] {doc['title']}")

    conn.commit()
    conn.close()
    print(f"\n[✓] Ingestion complete! Added {added_count} new extension documents.")

if __name__ == "__main__":
    seed_extended_knowledge()
