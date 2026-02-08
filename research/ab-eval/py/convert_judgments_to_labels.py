import json
import argparse
import os
from pathlib import Path

def convert_judgments_to_labels():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to raw judgments JSON file")
    parser.add_argument("--output", default="research/ab-eval/data/labels.medium.human.v1.json")
    parser.add_argument("--meta-output", default="research/ab-eval/data/labels.medium.human.v1.meta.json")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {input_path} not found.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    judgments = data.get("judgments", {})
    reviewer_id = data.get("reviewer_id", "unknown")
    
    canonical_labels = {}
    stats = {
        "reviewer_id": reviewer_id,
        "timestamp": data.get("timestamp"),
        "total_queries": len(judgments),
        "total_labeled_fonts": 0,
        "total_relevant_fonts": 0,
        "per_query_stats": {}
    }

    for qid, font_judgments in judgments.items():
        relevant_fonts = [name for name, score in font_judgments.items() if score == 1]
        canonical_labels[qid] = relevant_fonts
        
        labeled_count = len(font_judgments)
        relevant_count = len(relevant_fonts)
        
        stats["total_labeled_fonts"] += labeled_count
        stats["total_relevant_fonts"] += relevant_count
        stats["per_query_stats"][qid] = {
            "labeled": labeled_count,
            "relevant": relevant_count
        }

    # Save canonical labels
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(canonical_labels, f, indent=2)
    
    # Save metadata
    with open(args.meta_output, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"Converted {args.input} to {args.output}")
    print(f"Total queries: {stats['total_queries']}")
    print(f"Total relevant fonts: {stats['total_relevant_fonts']}")
    print(f"Metadata saved to {args.meta_output}")

if __name__ == "__main__":
    convert_judgments_to_labels()
