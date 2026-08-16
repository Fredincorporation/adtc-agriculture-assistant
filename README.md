# 🌾 ADTC 2026 - Offline Agriculture AI Assistant

An offline-first, RAG-enhanced conversational AI assistant tailored for West African farming practices. Built using **Qwen2.5-3B-Instruct GGUF**, **`llama-cpp-python`**, **SentenceTransformers**, and **Rich** to run entirely without internet access.

---

## 📌 Features

* **100% Local Inference:** Operates fully offline with zero external API calls or network requirements.
* **Retrieval-Augmented Generation (RAG):** Context-aware agricultural responses powered by local vector search.
* **Conversational Memory:** Retains multi-turn dialogue state across user interactions.
* **Real-time Token Streaming:** Instant visual feedback with terminal-rendered Markdown formatting via `rich`.
* **Single-File Binary Compilation:** Bundled using `PyInstaller` for deployment across target Linux environments.

---

## 📁 Directory Structure

```text
adtc-agriculture-assistant/
 model/
   └── Qwen2.5-3B-Instruct-Q4_K_M.gguf  # Quantized GGUF LLM weights
 dist/
   └── agri_assistant                   # Compiled standalone binary
 app.py                               # Terminal UI & streaming pipeline
 rag_engine.py                        # Vector DB initialization & query logic
 agri_assistant.spec                  # PyInstaller build specification
 test_offline.sh                      # Network isolation test script
 README.md 
