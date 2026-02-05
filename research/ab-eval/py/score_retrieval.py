import json
import numpy as np
import argparse
import os

def cosine_similarity(v1, v2):
    """Computes cosine similarity between two vectors."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def calculate_metrics(results, labels, k_list=[10, 20]):
    """
    results: { query_id: [ (doc_name, score), ... ] } sorted by score desc
    labels: { query_id: [ doc_name, ... ] }
    """
    metrics = {
        "Recall@10": 0,
        "Recall@20": 0,
        "MRR@10": 0
    }
    num_queries = len(labels)
    if num_queries == 0:
        return metrics

    for q_id, ground_truth in labels.items():
        if q_id not in results:
            continue
        
        retrieved = results[q_id]
        
        # Recall@K
        for k in k_list:
            top_k = [r[0] for r in retrieved[:k]]
            hits = len(set(top_k) & set(ground_truth))
            recall = hits / len(ground_truth) if ground_truth else 0
            metrics[f"Recall@{k}"] += recall
            
        # MRR@10
        mrr = 0
        for i, (doc_name, score) in enumerate(retrieved[:10]):
            if doc_name in ground_truth:
                mrr = 1.0 / (i + 1)
                break
        metrics["MRR@10"] += mrr

    # Average
    for key in metrics:
        metrics[key] /= num_queries
        
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc_embeddings", default="research/ab-eval/out/embeddings_text_docs.jsonl")
    parser.add_argument("--query_embeddings", default="research/ab-eval/out/embeddings_text_queries.jsonl")
    parser.add_argument("--labels", default="research/ab-eval/data/labels.toy.json")
    parser.add_argument("--out_report_json", default="research/ab-eval/out/report_text.json")
    parser.add_argument("--out_report_md", default="research/ab-eval/out/report_text.md")
    args = parser.parse_args()

    # Load labels
    with open(args.labels, 'r') as f:
        labels = json.load(f)

    # Load doc embeddings
    doc_embeddings = []
    if not os.path.exists(args.doc_embeddings):
        print(f"Error: Doc embeddings file not found: {args.doc_embeddings}")
        return
    with open(args.doc_embeddings, 'r') as f:
        for line in f:
            doc_embeddings.append(json.loads(line))

    # Load query embeddings
    query_embeddings = []
    if not os.path.exists(args.query_embeddings):
        print(f"Error: Query embeddings file not found: {args.query_embeddings}")
        return
    with open(args.query_embeddings, 'r') as f:
        for line in f:
            query_embeddings.append(json.loads(line))

    # Compute similarities
    results = {}
    for q in query_embeddings:
        q_id = q['id']
        q_vec = np.array(q['embedding'])
        scores = []
        for doc in doc_embeddings:
            doc_vec = np.array(doc['embedding'])
            score = cosine_similarity(q_vec, doc_vec)
            scores.append((doc['name'], float(score)))
        
        # Sort by score desc
        scores.sort(key=lambda x: x[1], reverse=True)
        results[q_id] = scores

    # Calculate metrics
    metrics = calculate_metrics(results, labels)

    # Print results
    print("\n--- Retrieval Evaluation Results ---")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    # Save JSON report
    with open(args.out_report_json, 'w') as f:
        json.dump({
            "metrics": metrics,
            "config": {
                "doc_embeddings": args.doc_embeddings,
                "query_embeddings": args.query_embeddings,
                "labels": args.labels
            }
        }, f, indent=2)

    # Save Markdown report
    with open(args.out_report_md, 'w') as f:
        f.write("# Retrieval Evaluation Report (Text Baseline)\n\n")
        f.write("| Metric | Value |\n")
        f.write("| :--- | :--- |\n")
        for k, v in metrics.items():
            f.write(f"| {k} | {v:.4f} |\n")
        f.write(f"\n*Evaluated on {len(labels)} queries against {len(doc_embeddings)} fonts.*\n")

    print(f"\nReports saved to {args.out_report_json} and {args.out_report_md}")

if __name__ == "__main__":
    main()
