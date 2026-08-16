import os
import sqlite3
import numpy as np

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from rag_engine import init_db, DB_PATH

init_db()
embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)

documents = [
    {
        "crop": "Maize",
        "topic": "Fertilization & Soil Health",
        "title": "Maize Fertilizer Application Guide",
        "content": "For optimal maize yields in West Africa, apply NPK 15-15-15 at planting (200 kg/ha) as basal application. Top-dress with Urea (100 kg/ha) at 4-6 weeks after emergence when maize is knee-high."
    },
    {
        "crop": "Maize",
        "topic": "Planting Schedule",
        "title": "Maize Seasonal Planting Windows",
        "content": "In tropical rainforest zones, plant early maize with the onset of steady rains (March to April). For the late season, plant in early August."
    },
    {
        "crop": "Legumes",
        "topic": "Fertilization & Soil Health",
        "title": "Legume (Cowpea & Groundnut) Fertilizer Requirements",
        "content": "Legumes fix atmospheric nitrogen via Rhizobium nodules and require minimal nitrogen fertilizer. Apply Single Super Phosphate (SSP) at 100-150 kg/ha or NPK 12-24-12 at planting to boost root and pod development. Avoid high Urea applications as excessive nitrogen inhibits biological nitrogen fixation."
    },
    {
        "crop": "Cassava",
        "topic": "Fertilization & Soil Health",
        "title": "Cassava Fertilizer Recommendation Guide",
        "content": "Cassava is a heavy potassium feeder. Apply NPK 15-15-15 or NPK 12-12-17 at 200-300 kg/ha around 4-8 weeks after planting (basal). Top-dress with Muriate of Potash (MOP) or Urea at 12-16 weeks to support root tuber expansion."
    },
    {
        "crop": "Cassava",
        "topic": "Pest & Disease Control",
        "title": "Cassava Mosaic Disease (CMD) Management",
        "content": "Cassava Mosaic Disease causes yellow leaf distortion and stunting. Control it by planting CMD-resistant varieties such as TME 419 or TMS 30572, and rogue infected plants."
    }
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DELETE FROM knowledge_base")

for doc in documents:
    text_to_embed = f"{doc['crop']} {doc['topic']} {doc['title']} {doc['content']}"
    vec = embedder.encode(text_to_embed).astype(np.float32).tobytes()
    
    cursor.execute("""
        INSERT INTO knowledge_base (crop, topic, title, content, embedding)
        VALUES (?, ?, ?, ?, ?)
    """, (doc['crop'], doc['topic'], doc['title'], doc['content'], vec))

conn.commit()
conn.close()
print("[✓] Database re-seeded with Cassava fertilizer records!")
