import json
import random
import os
from pathlib import Path

def prepare_human_labeling():
    # 1. Define the medium query set
    medium_query_ids = [
        "cq_002", "cq_003", "cq_008", "cq_009", "cq_010",
        "cq_011", "cq_012", "cq_015", "cq_016", "cq_019",
        "cq_021", "cq_024", "cq_025", "cq_029", "cq_030",
        "cq_032", "cq_033", "cq_038", "cq_039", "cq_040"
    ]

    queries_path = Path("research/ab-eval/data/queries.complex.v1.json")
    labels_path = Path("research/ab-eval/data/labels.complex.v1.json")
    corpus_path = Path("research/ab-eval/data/corpus.200.json")

    if not queries_path.exists() or not labels_path.exists() or not corpus_path.exists():
        print("Required data files missing.")
        return

    with open(queries_path, "r", encoding="utf-8") as f:
        all_queries = json.load(f)
    
    with open(labels_path, "r", encoding="utf-8") as f:
        all_labels = json.load(f)
    
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    corpus_map = {f["name"]: f for f in corpus}
    font_names = list(corpus_map.keys())

    # Filter to medium set
    medium_queries = [q for q in all_queries if q["id"] in medium_query_ids]
    
    # 2. Generate Candidate Pool
    candidate_pool = {}
    random.seed(42) # Deterministic pool

    for qid in medium_query_ids:
        # Start with provisional labels as "hits"
        hits = all_labels.get(qid, [])
        # Add random distractors from corpus
        distractors = random.sample(font_names, min(len(font_names), 25))
        
        # Combine and unique
        pool = list(set(hits) | set(distractors))
        # Shuffle for blinding
        random.shuffle(pool)
        candidate_pool[qid] = pool

    # 3. Save Artifacts
    output_dir = Path("research/ab-eval/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    queries_out = output_dir / "queries.medium.human.v1.json"
    pool_out = output_dir / "candidate_pool.medium.v1.json"

    with open(queries_out, "w", encoding="utf-8") as f:
        json.dump(medium_queries, f, indent=2)
    
    with open(pool_out, "w", encoding="utf-8") as f:
        json.dump(candidate_pool, f, indent=2)

    print(f"Generated {queries_out} with {len(medium_queries)} queries.")
    print(f"Generated {pool_out} with candidate pools.")

if __name__ == "__main__":
    prepare_human_labeling()
