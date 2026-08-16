# ADTC 2026 Submission Report: Offline Agriculture AI Assistant

## 1. Problem Statement
Smallholder farmers across West Africa frequently lack access to reliable internet or real-time agricultural extension services. This project delivers a 100% offline, privacy-first AI advisory assistant that provides localized agronomic guidance directly on low-spec hardware.

## 2. Design Decisions & Architecture
* **Language Model:** `Qwen2.5-3B-Instruct` in `GGUF Q4_K_M` format. Chosen for its instruction-following accuracy and low memory footprint (~2.2 GB RAM).
* **Inference Engine:** `llama.cpp` bindings via Python (`llama-cpp-python`).
* **Retrieval-Augmented Generation (RAG):** Local vector lookup returning agronomic context to ground responses.
* **UI & Memory:** Single-prompt Rich terminal interface with 3-turn multi-turn conversation memory and 2,500-character context safety bounds.

## 3. Hardware & Efficiency Benchmarks
* **Target Hardware Profile:** Standard 8 GB RAM laptop (Ubuntu 22.04 LTS, CPU-only execution).
* **Peak RAM (RSS):** ~2.4 GB (Well below the 7.0 GB limit).
* **Inference Speed:** ~12 to 18 tokens/sec.
* **Network Status:** Zero external API calls post-initialization.
