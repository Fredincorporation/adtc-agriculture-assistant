#!/bin/bash
set -e

MODEL_DIR="model"
MODEL_PATH="${MODEL_DIR}/Qwen2.5-3B-Instruct-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"

mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_PATH" ]; then
    echo "✅ Model file already exists at $MODEL_PATH."
    exit 0
fi

echo "📦 Downloading Qwen2.5-3B-Instruct-Q4_K_M.gguf from Hugging Face..."
curl -L -o "$MODEL_PATH" "$MODEL_URL"

echo "✅ Download complete!"
