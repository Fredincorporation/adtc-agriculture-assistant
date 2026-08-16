#!/usr/bin/env python3
import os
import sys
import time
import psutil
from rich.console import Console
from rich.table import Table

from app import process_query, init_db, init_cache_db

console = Console()

TEST_QUERIES = [
    {
        "category": "Indexed Crop (Cassava)",
        "query": "what fertilizer should i apply for cassava"
    },
    {
        "category": "Semantic Cache Hit",
        "query": "which fertilizer is recommended for cassava plants"
    },
    {
        "category": "Indexed Crop (Legumes)",
        "query": "what fertilizer should i apply for legumes"
    },
    {
        "category": "Out-of-Domain Crop (Yam - Pre-ingestion)",
        "query": "what fertilizer should i apply for yam"
    }
]

def run_benchmarks():
    console.rule("[bold cyan]📊 ADTC 2026 - SYSTEM BENCHMARK & PERFORMANCE SUITE[/bold cyan]")
    
    process = psutil.Process(os.getpid())
    idle_ram = process.memory_info().rss / (1024 * 1024)
    console.print(f"[dim]Initial RAM Baseline: {idle_ram:.1f} MB[/dim]\n")
    
    results = []

    for idx, test in enumerate(TEST_QUERIES, 1):
        console.print(f"[bold yellow]Test {idx}/{len(TEST_QUERIES)}: {test['category']}[/bold yellow]")
        
        start_time = time.time()
        response = process_query(test["query"])
        elapsed = time.time() - start_time
        peak_ram = process.memory_info().rss / (1024 * 1024)
        
        status = "⚡ CACHE HIT" if elapsed < 1.0 else "🧠 FULL INFERENCE"
        
        results.append({
            "id": idx,
            "category": test["category"],
            "status": status,
            "time_sec": elapsed,
            "ram_mb": peak_ram
        })
        console.print("-" * 60)

    table = Table(title="System Performance Summary", header_style="bold magenta")
    table.add_column("ID", justify="center")
    table.add_column("Category", style="cyan")
    table.add_column("Execution Mode", style="green")
    table.add_column("Latency", justify="right")
    table.add_column("Peak RAM", justify="right")

    for r in results:
        table.add_row(
            str(r["id"]),
            r["category"],
            r["status"],
            f"{r['time_sec']:.2f}s",
            f"{r['ram_mb']:.1f} MB"
        )

    console.print("\n", table)

if __name__ == "__main__":
    run_benchmarks()
