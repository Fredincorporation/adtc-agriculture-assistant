#!/usr/bin/env python3
"""
Main offline Agriculture Assistant
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MODEL = ROOT / "models" / "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
SYSTEM_PROMPT = (ROOT / "prompts" / "system_prompt.txt").read_text()
RETRIEVE_SCRIPT = ROOT / "rag" / "retrieve.py"
LLAMA_CLI = Path("/root/llama.cpp/build/bin/llama-cli")

def get_context(query: str) -> str:
    result = subprocess.run(
        ["python3", str(RETRIEVE_SCRIPT), query],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def ask(query: str, max_tokens: int = 350):
    context = get_context(query)
    
    full_prompt = f"""{SYSTEM_PROMPT}

{context}

User: {query}

Assistant:"""

    cmd = [
        str(LLAMA_CLI),
        "-m", str(MODEL),
        "-p", full_prompt,
        "-n", str(max_tokens),
        "--temp", "0.45",
        "-c", "3072",
        "-ngl", "0",
        "--single-turn",
        "--no-display-prompt"
    ]
    
    print("Thinking...\n")
    subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 src/ask.py \"your question\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    ask(query)
