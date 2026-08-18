# ADTC 2026 Submission Report: Offline Agriculture AI Assistant

## 1. Problem Statement & Mission
Smallholder farmers across rural Africa face critical gaps in agricultural advisory services. Reliable internet connectivity is often non-existent in remote farmlands, and conventional extension services are understaffed. Standard cloud-based AI solutions fail in these environments due to latency, connectivity dependency, and recurring API costs.

This project delivers a **100% offline, localized, and privacy-first AI advisory engine** designed to run efficiently on low-spec edge hardware (such as 8 GB RAM consumer laptops). By bringing agronomic intelligence directly to the edge, the assistant provides immediate, context-aware agricultural guidance without sending a single byte over the internet.

---

## 2. Tools & Technologies Stack

| Component | Tool / Technology | Purpose & Justification |
| :--- | :--- | :--- |
| **Base OS / Runtime** | Ubuntu 22.04 LTS / Docker | Provides a deterministic, lightweight environment for execution on budget hardware. |
| **Inference Engine** | `llama.cpp` (`llama-cpp-python`) | Executes GGUF quantized models on CPU with AVX/AVX2 acceleration without requiring dedicated GPUs. |
| **Language Model** | `Qwen2.5-3B-Instruct` (`GGUF Q4_K_M`) | Delivers instruction-following accuracy and multilingual support across 10 African languages within a ~2.2 GB RAM footprint. |
| **Vector Retrieval / RAG** | Python (`rag_engine.py`) | In-memory semantic vector lookup returning localized agronomic context to ground model outputs. |
| **Query & Context Manager** | `query_interceptor.py` | Detects regional variables (location, crop type) and injects contextual parameters before LLM inference. |
| **CLI & UI Layout** | Python `rich` Library | Provides real-time streaming, interactive terminal layouts, and formatted Markdown rendering. |
| **Benchmarking Suite** | `adtc-profiler 0.1.0` | Evaluates peak memory footprint (RSS), generation throughput, TTFT latency, and model accuracy. |

---

## 3. How It Was Built (Step-by-Step Architecture)

1. **Model Quantization & Setup:** Configured `llama.cpp` bindings to load `Qwen2.5-3B-Instruct` in 4-bit `GGUF Q4_K_M` quantization, strictly capping VRAM/RAM allocation (`n_ctx=4096`).
2. **Agronomic Vector Base Integration:** Built a local vector retrieval engine (`rag_engine.py`) that performs top-k semantic searches (`top_k=4`) against indexed agricultural extension manuals.
3. **Context Interception & Guardrails:** Developed `ContextGuardrail` (`query_interceptor.py`) to preserve state across multi-turn user conversations and auto-fill required geographical and crop variables into system prompts.
4. **Terminal UI & Live Streaming:** Implemented `app.py` using `rich.live.Live(auto_refresh=False)`, updating terminal layouts every 3 tokens to achieve fluid real-time streaming without text flicker or scrollback duplication in Docker TTY wrappers.
5. **Offline Caching:** Added in-memory response caching for exact or canonical user query keys to return immediate answers for repeated agronomic prompts without re-executing model inference.

---

## 4. Hardware & Efficiency Benchmarks (Official Audit Record)
Measured directly via the official ADTC verification suite (`audit.json` on `audit_cloud_vm` with Intel i7-3840QM CPU @ 2.80GHz, 7.8 GB RAM, Ubuntu 22.04 LTS):

* **Peak Memory Footprint (RSS):** `2271.66 MB` (~2.27 GB RAM, well under the 7.0 GB budget limit).
* **Steady State Memory (RSS):** `2085.02 MB`.
* **Generation Throughput:** `4.05 tokens/second` (CPU-only execution).
* **Time to First Token (TTFT):** `53.6s` (512 prompt token context evaluation).
* **Accuracy Score (ARC-Easy):** `0.78` (`acc_norm` across 50 samples).
* **Network Status:** 100% offline with zero external API dependencies post-initialization.

---

## 5. Key Engineering Challenges Faced & Solutions

### A. Terminal Streaming vs. Rich Formatting
* **Challenge:** Token-by-token streaming in TTY containers caused line duplication and scrollback glitches when rendering multi-line Rich Markdown blocks.
* **Solution:** Applied dynamic token batching with `rich.live.Live(auto_refresh=False)`, updating the terminal renderer every 3 tokens to ensure clean layout formatting.

### B. Memory Efficiency under Low Hardware Limits
* **Challenge:** Maintaining multi-turn context without exceeding the strict memory constraints of target evaluation hardware.
* **Solution:** Combined `Q4_K_M` quantization with bounded context limits (`n_ctx=4096`), keeping memory usage strictly under 2.3 GB RAM.

### C. Preventing Agronomic Hallucinations
* **Challenge:** Low-parameter offline models can generate inaccurate agronomic instructions if ungrounded.
* **Solution:** Enforced strict RAG context grounding using semantic retrieval (`top_k=4`) combined with system prompt instructions mandating concrete metrics (distances, application timing, and quantities).

---

## 6. Future Expansion Roadmap
* **Quantized Vector Indexing:** SQLite-backed vector storage for sub-second retrieval lookup.
* **Speech Interface:** Integrating lightweight offline Whisper models (`whisper.cpp`) for voice input in local languages.
