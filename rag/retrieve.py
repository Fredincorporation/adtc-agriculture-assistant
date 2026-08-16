#!/usr/bin/env python3
"""
Improved offline RAG for ADTC Agriculture Assistant
"""

import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

def load_documents():
    docs = []
    for file in DATA_DIR.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            docs.append({
                "source": file.name,
                "content": content
            })
    return docs

def simple_score(query: str, text: str) -> float:
    query_lower = query.lower()
    text_lower = text.lower()
    query_terms = set(re.findall(r'\w+', query_lower))
    
    score = 0.0
    
    for term in query_terms:
        if len(term) < 3:
            continue
        count = text_lower.count(term)
        score += count * (2.2 if len(term) > 5 else 1.3)
    
    boosts = {
        "fall armyworm": 16, "faw": 13, "armyworm": 11,
        "striga": 15, "witchweed": 13,
        "cassava": 12, "mosaic": 10, "brown streak": 10,
        "soil": 8, "compost": 10, "manure": 9, "fertility": 9,
        "drought": 12, "mulch": 8, "zai": 10,
        "storage": 11, "post-harvest": 11, "weevil": 9, "hermetic": 10,
        "tick": 14, "ticks": 14, "livestock": 9, "cattle": 9, "goat": 9, "goats": 9,
        "sorghum": 11, "millet": 11,
        "bean": 9, "beans": 9, "legume": 10, "cowpea": 9, "groundnut": 9,
        "vegetable": 14, "vegetables": 14, "tomato": 10, "onion": 9, 
        "cabbage": 9, "kale": 8, "okra": 8, "amaranth": 8,
        "conservation": 9, "residue": 7,
        "maize": 6, "plant": 3, "grow": 4
    }
    
    for term, weight in boosts.items():
        if term in query_lower and term in text_lower:
            score += weight
    
    return score

def retrieve(query: str, top_k: int = 2) -> list:
    docs = load_documents()
    scored = []
    
    for doc in docs:
        score = simple_score(query, doc["content"])
        if score > 0:
            scored.append((score, doc))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored[:top_k]]

def format_context(docs: list) -> str:
    if not docs:
        return "No highly relevant local knowledge was found for this specific question."
    
    context = "Relevant knowledge from local agriculture guides:\n\n"
    for doc in docs:
        context += f"--- Source: {doc['source']} ---\n"
        content = doc["content"]
        if len(content) > 1100:
            content = content[:1100] + "..."
        context += content + "\n\n"
    return context.strip()

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "fall armyworm"
    docs = retrieve(query)
    print(format_context(docs))
