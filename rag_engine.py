import os
import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer

embedder = None
documents = []
doc_embeddings = None

def detect_language(text: str) -> str:
    text_lower = text.lower()
    # Simple language matching based on key marker words
    swahili_keywords = ["jinsi", "gani", "naweza", "kuzuia", "wadudu", "kwenye", "mahindi", "shamba", "panda", "kwa"]
    hausa_keywords = ["yaya", "zan", "iya", "kariya", "kwarori", "a", "harshen", "hausa", "irin", "ruwan", "fari"]
    yoruba_keywords = ["bo", "se", "le", "gbingbin", "gbaguda", "ede", "yoruba", "ojo"]
    igbo_keywords = ["kama", "mmezu", "akwukwo", "asusu", "igbo", "nchekwa", "ji"]

    words = re.findall(r'\w+', text_lower)
    
    if any(w in words for w in swahili_keywords):
        return "sw"
    if any(w in words for w in hausa_keywords):
        return "ha"
    if any(w in words for w in yoruba_keywords):
        return "yo"
    if any(w in words for w in igbo_keywords):
        return "ig"
    return "en"

def get_kb_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "agri_kb.json")

def init_db():
    global embedder, documents, doc_embeddings
    
    kb_path = get_kb_path()
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            documents = json.load(f)
    else:
        documents = []

    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    
    if documents:
        texts = [doc["text"] for doc in documents]
        doc_embeddings = embedder.encode(texts, convert_to_numpy=True)
        norms = np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        doc_embeddings = doc_embeddings / norms

def query_knowledge_base(query_text: str, top_k: int = 2):
    global embedder, documents, doc_embeddings
    
    if not documents or doc_embeddings is None or embedder is None:
        return "No specific document context found."

    user_lang = detect_language(query_text)

    # Filter knowledge base strictly by detected user language (fallback to English if not found)
    filtered_indices = [
        idx for idx, doc in enumerate(documents) 
        if doc.get("language") == user_lang or doc.get("language") == "en"
    ]

    if not filtered_indices:
        filtered_indices = list(range(len(documents)))

    query_vec = embedder.encode([query_text], convert_to_numpy=True)[0]
    q_norm = np.linalg.norm(query_vec)
    if q_norm > 0:
        query_vec = query_vec / q_norm

    sub_embeddings = doc_embeddings[filtered_indices]
    similarities = np.dot(sub_embeddings, query_vec)
    sorted_sub_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for sub_idx in sorted_sub_indices:
        actual_idx = filtered_indices[sub_idx]
        if similarities[sub_idx] > 0.15:
            results.append(documents[actual_idx]["text"])

    if not results:
        return "No specific document context found."

    return "\n\n".join(results)
