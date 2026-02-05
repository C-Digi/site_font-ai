import subprocess
import sys
import os

def run_script(script_name, args=[]):
    """Helper to run a python script and stream output."""
    script_path = os.path.join("research", "ab-eval", "py", script_name)
    print(f"\n{'='*60}")
    print(f"Running: {script_name} {' '.join(args)}")
    print(f"{'='*60}\n")
    
    # Use sys.executable to ensure we use the same python interpreter
    cmd = [sys.executable, script_path] + args
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"\nError: {script_name} failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    # Ensure we are in the project root
    if not os.path.exists("research/ab-eval"):
        print("Error: Run this script from the project root.")
        sys.exit(1)

    # 1. Render glyph sheets
    run_script("render_glyph_sheet.py", ["--corpus", "research/ab-eval/data/corpus.toy.json"])

    # 2. Generate Text Embeddings (Variant A)
    run_script("embed_openrouter_text.py", [
        "--corpus", "research/ab-eval/data/corpus.toy.json",
        "--queries", "research/ab-eval/data/queries.toy.json"
    ])

    # 3. Score retrieval
    run_script("score_retrieval.py", [
        "--doc_embeddings", "research/ab-eval/out/embeddings_text_docs.jsonl",
        "--query_embeddings", "research/ab-eval/out/embeddings_text_queries.jsonl",
        "--labels", "research/ab-eval/data/labels.toy.json"
    ])

    print(f"\n{'='*60}")
    print("Full Text Baseline Evaluation Pipeline Complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
