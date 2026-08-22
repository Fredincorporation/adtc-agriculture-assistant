# ADTC 2026 - Offline Agriculture AI Assistant

An offline-first, RAG-enhanced conversational AI assistant tailored for West African farming practices. Built using **Qwen2.5-3B-Instruct GGUF**, **llama-cpp-python**, **SentenceTransformers**, and **Rich** to run entirely without internet access.

---

## Features

- **100% Local Inference:** Operates fully offline with zero external API calls or network requirements.
- **Retrieval-Augmented Generation (RAG):** Context-aware agricultural responses powered by local vector search.
- **Context Guardrails:** Active session slot extraction for regional locations and expanded African crop entities.
- **Conversational Memory:** Retains multi-turn dialogue state across user interactions.
- **Real-time Token Streaming:** Instant visual feedback with terminal-rendered Markdown formatting via `rich`.
- **Single-File Binary Compilation:** Bundled using PyInstaller for deployment across target Linux environments.

---

## Directory Structure

```text
adtc-agriculture-assistant/
 model/
   └── Qwen2.5-3B-Instruct-Q4_K_M.gguf   # Quantized GGUF LLM weights
 dist/
   └── agri_assistant                   # Compiled standalone binary
 app.py                               # Terminal UI & streaming pipeline
 rag_engine.py                        # Vector DB initialization & query logic
 query_interceptor.py                 # Entity extraction & guardrail context enrichment
 agri_assistant.spec                  # PyInstaller build specification
 test_offline.sh                      # Network isolation test script
 README.md
```

---

## Prerequisites & Setup

### System Requirements
- **OS:** Ubuntu 22.04 LTS (or compatible Linux distribution)
- **Python:** 3.10+
- **System RAM:** 8 GB minimum (Peak RSS: ~2.3 GB)

## 🛠️ Setup & Installation

### System Prerequisites (For Clean Ubuntu Systems)
If deploying on a fresh Ubuntu instance, install Python and build essentials first:

```bash
sudo apt-get update && sudo apt-get install -y \
    python3 \
    python3-pip \
    git \
    build-essential\
    curl\
    cmake\
    ninja-build
```

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Fredincorporation/adtc-agriculture-assistant.git
cd adtc-agriculture-assistant
```

2. Download model weights:
```bash
chmod +x download_model.sh
./download_model.sh
```

3. Install Python dependencies:
```bash
pip install -r ./requirements.txt
```
#If pip throws an externally-managed-environment error, pass the break-system-packages flag
```bash
pip install -r ./requirements.txt --break-system-packages
```

4. Initialize the agronomy knowledge base:
```bash
python3 seed_db.py
```

5. Run the assistant:
```bash
python3 app.py
```

---

## Reproducing Profiler Telemetry

To verify offline benchmark scores and telemetry locally:

```bash
adtc-profiler run \
  --submission . \
  --mode participant \
  --output submission.json
```

