import subprocess
import sys
import os
import argparse

def run_script(script_name, args=[]):
    """Helper to run a python script and stream output."""
    script_path = os.path.join("research", "ab-eval", "py", script_name)
    print(f"\n{'='*60}")
    print(f"Running: {script_name} {' '.join(args)}")
    print(f"{'='*60}\n")
    
    cmd = [sys.executable, script_path] + args
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"\nError: {script_name} failed with exit code {result.returncode}")
        # Don't exit immediately if we are running 'all', maybe some parts can still work
        return False
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["A", "B", "all"], default="all",
                        help="Which variant to run. A: Text, B: VL, all: A+B+C")
    parser.add_argument("--dataset", choices=["toy", "200"], default=None,
                        help="Preset dataset to use (toy or 200). Overrides file paths if set.")
    parser.add_argument("--corpus", help="Path to corpus file")
    parser.add_argument("--queries", help="Path to queries file")
    parser.add_argument("--labels", help="Path to labels file")
    args = parser.parse_args()

    # Set defaults based on dataset preset if provided
    if args.dataset == "200":
        if not args.corpus: args.corpus = "research/ab-eval/data/corpus.200.json"
        if not args.queries: args.queries = "research/ab-eval/data/queries.200.json"
        if not args.labels: args.labels = "research/ab-eval/data/labels.200.json"
    elif args.dataset == "toy" or (not args.dataset and not args.corpus):
        if not args.corpus: args.corpus = "research/ab-eval/data/corpus.toy.json"
        if not args.queries: args.queries = "research/ab-eval/data/queries.toy.json"
        if not args.labels: args.labels = "research/ab-eval/data/labels.toy.json"

    # Ensure we are in the project root
    if not os.path.exists("research/ab-eval"):
        print("Error: Run this script from the project root.")
        sys.exit(1)

    success_a = False
    success_b = False

    # 1. Run Variant A (Text)
    if args.variant in ["A", "all"]:
        print("\n>>> RUNNING VARIANT A (TEXT) PIPELINE <<<")
        success_a = run_script("embed_openrouter_text.py", [
            "--corpus", args.corpus,
            "--queries", args.queries
        ])

    # 2. Run Variant B (VL)
    if args.variant in ["B", "all"]:
        print("\n>>> RUNNING VARIANT B (VL) PIPELINE <<<")
        # embed_qwen3_vl_batch.py already calls render_glyph_sheet.py internally
        success_b = run_script("embed_qwen3_vl_batch.py", [
            "--corpus", args.corpus,
            "--queries", args.queries
        ])

    # 3. Final Scoring (Variant C / All)
    if args.variant == "all":
        print("\n>>> RUNNING FINAL SCORING (A + B + C) <<<")
        run_script("score_all_variants.py", [
            "--labels", args.labels
        ])
    elif args.variant == "A" and success_a:
        run_script("score_retrieval.py", [
            "--labels", args.labels
        ])
    elif args.variant == "B" and success_b:
        # B doesn't have a standalone scorer for just B in the old script, 
        # so we use score_all_variants which handles missing A gracefully.
        run_script("score_all_variants.py", [
            "--labels", args.labels
        ])

    print(f"\n{'='*60}")
    print("Evaluation Pipeline Run Complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
