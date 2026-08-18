import sys
import warnings
from rag_engine import query_knowledge_base
from query_interceptor import ContextGuardrail
from llama_cpp import Llama
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

warnings.filterwarnings("ignore", category=ResourceWarning)

console = Console()

llm = Llama(
    model_path="model/Qwen2.5-3B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    verbose=False
)

response_cache = {}

# Initialize guardrail instance to preserve session state across turns
guardrail = ContextGuardrail()

console.print("\n[bold green]🌾 ADTC Pan-African Agriculture Assistant Initialized.[/bold green]")
console.print("Type '[bold red]exit[/bold red]' or '[bold red]quit[/bold red]' to exit.\n")

while True:
    try:
        user_query = input("Ask Agri-Assistant: ").strip()
        if user_query.lower() in ["exit", "quit"]:
            break
        if not user_query:
            continue

        # --- STEP 1: INTERCEPT & ENRICH ---
        user_query = guardrail.check_and_enrich(user_query)
        query_key = user_query.lower()

        # --- STEP 2: CACHE CHECK ---
        if query_key in response_cache:
            console.print("\n[dim yellow]⚡ [Cache Hit] Serving response instantly from memory...[/dim yellow]\n")
            console.print(Markdown(response_cache[query_key]))
            console.print("\n" + "-" * 50)
            continue

        # --- STEP 3: RAG RETRIEVAL ---
        context = query_knowledge_base(user_query, top_k=4)

        system_prompt = (
            "You are the ADTC Pan-African Agriculture Assistant, an expert agronomist providing thorough, highly detailed, and actionable agricultural guidance for African farmers.\n\n"
            "Formatting & Style Rules:\n"
            "1. Use explicit Level 3 Markdown sub-headings (###) for each step or section.\n"
            "2. Under each sub-heading, provide detailed bullet points with **bold terms**.\n"
            "3. DO NOT give brief one-line summaries. Write expansive, multi-sentence explanations for every bullet point, including reasons why the step is important, specific metrics (quantities, distances, timings), and practical regional tips for smallholder farmers.\n\n"
            f"Knowledge Base Context:\n{context}"
        )

        prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{user_query}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        stream = llm(
            prompt,
            max_tokens=-1,
            temperature=0.30,
            repeat_penalty=1.15,
            stop=["<|im_end|>", "<|im_start|>", "User:", "\nUser"],
            stream=True
        )

        full_response = ""
        console.print()

        # --- STEP 4: RICH LIVE STREAMING WITH CONTROLLED REFRESH ---
        # auto_refresh=False prevents repeated duplicate lines in TTY scrollbacks
        with Live(Markdown(""), console=console, auto_refresh=False) as live:
            token_counter = 0
            for output in stream:
                token = output["choices"][0]["text"]
                full_response += token
                token_counter += 1
                
                # Refresh rendering every 3 tokens to keep speed fast and prevent flicker
                if token_counter % 3 == 0:
                    live.update(Markdown(full_response), refresh=True)

            # Final render to catch remaining tokens
            live.update(Markdown(full_response), refresh=True)

        response_cache[query_key] = full_response
        console.print("\n" + "-" * 50)

    except (KeyboardInterrupt, EOFError):
        break

try:
    if hasattr(llm, "close"):
        llm.close()
    del llm
except Exception:
    pass

sys.exit(0)
