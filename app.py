import os
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import argparse
import warnings
import atexit

warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console(force_terminal=sys.stdout.isatty())

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

from rag_engine import init_db, query_knowledge_base
from llama_cpp import Llama

init_db()

possible_paths = [
    get_resource_path("model/Qwen2.5-3B-Instruct-Q4_K_M.gguf"),
    get_resource_path("model/model.gguf"),
    os.path.abspath("model/Qwen2.5-3B-Instruct-Q4_K_M.gguf"),
    os.path.abspath("model/model.gguf"),
]

MODEL_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        MODEL_PATH = path
        break

if not MODEL_PATH or not os.path.exists(MODEL_PATH):
    console.print("\n[bold red][ERROR][/bold red] No valid .gguf model file found in model/.")
    sys.exit(1)

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=os.cpu_count() or 4,
    verbose=False
)

def cleanup():
    global llm
    if llm is not None:
        try:
            if hasattr(llm, 'close'):
                llm.close()
            del llm
            llm = None
        except Exception:
            pass

atexit.register(cleanup)

chat_history = []

def process_query(user_query: str) -> str:
    global chat_history
    try:
        retrieved_context = query_knowledge_base(user_query, top_k=1)

        # Direct context passthrough if high quality match exists
        if retrieved_context and retrieved_context != "No specific document context found.":
            full_text = retrieved_context.strip()
            if sys.stdout.isatty():
                console.print(Markdown(full_text))
            else:
                sys.stdout.write(full_text + "\n")
                sys.stdout.flush()
            chat_history.append((user_query, full_text))
            return full_text

        # Fallback to LLM if no exact RAG document matches
        system_prompt = "You are a helpful pan-African agricultural assistant."
        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_query}<|im_end|>\n<|im_start|>assistant\n"

        stream = llm(
            prompt,
            max_tokens=200,
            temperature=0.1,
            stop=["<|im_end|>", "<|im_start|>"],
            echo=False,
            stream=True
        )

        full_text = ""
        for output in stream:
            token = output["choices"][0]["text"]
            full_text += token
            sys.stdout.write(token)
            sys.stdout.flush()
        sys.stdout.write("\n")

        chat_history.append((user_query, full_text.strip()))
        return full_text.strip()

    except Exception as e:
        err_msg = f"Error during inference: {e}"
        console.print(f"\n[bold red]{err_msg}[/bold red]")
        return err_msg

def main():
    parser = argparse.ArgumentParser(description="ADTC Pan-African Agri Assistant")
    parser.add_argument("--prompt", type=str, help="Single query execution")
    parser.add_argument("--export", type=str, help="Path to export response text file")
    args = parser.parse_args()

    if args.prompt:
        response = process_query(args.prompt)
        if args.export:
            with open(args.export, "w", encoding="utf-8") as f:
                f.write(response)
            console.print(f"\n[bold green]Response exported to {args.export}[/bold green]")
        return

    console.print("\n🌾 [bold yellow]ADTC Pan-African Agriculture Assistant Initialized.[/bold yellow]")
    console.print("Type 'exit' or 'quit' to exit.\n")

    while True:
        try:
            user_input = console.input("[bold blue]Ask Agri-Assistant:[/bold blue] ")
            if not user_input.strip():
                continue
            if user_input.strip().lower() in ['exit', 'quit']:
                break
            
            response = process_query(user_input)
            
            if args.export:
                with open(args.export, "a", encoding="utf-8") as f:
                    f.write(f"Q: {user_input}\nA: {response}\n{'-'*40}\n")
                console.print(f"[dim]Appended response to {args.export}[/dim]")
                
            console.print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
