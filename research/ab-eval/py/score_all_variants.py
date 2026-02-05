import json
import numpy as np
import argparse
import os

def cosine_similarity_matrix(queries, docs):
    """
    queries: (N_q, D)
    docs: (N_d, D)
    Returns: (N_q, N_d) matrix of similarities
    """
    # Normalize
    queries_norm = queries / (np.linalg.norm(queries, axis=1, keepdims=True) + 1e-9)
    docs_norm = docs / (np.linalg.norm(docs, axis=1, keepdims=True) + 1e-9)
    return np.dot(queries_norm, docs_norm.T)

def calculate_metrics_from_scores(score_matrix, doc_names, query_ids, labels, k_list=[10, 20]):
    """
    score_matrix: (N_q, N_d)
    doc_names: list of N_d strings
    query_ids: list of N_q strings
    labels: { query_id: [ doc_name, ... ] }
    """
    metrics = {
        "Recall@10": 0,
        "Recall@20": 0,
        "MRR@10": 0
    }
    num_queries = len(query_ids)
    valid_queries = 0

    per_query_results = {}

    for i, q_id in enumerate(query_ids):
        if q_id not in labels:
            continue
        
        valid_queries += 1
        ground_truth = labels[q_id]
        scores = score_matrix[i]
        
        # Get top-K indices
        top_indices = np.argsort(scores)[::-1]
        retrieved = [(doc_names[idx], float(scores[idx])) for idx in top_indices]
        per_query_results[q_id] = retrieved
        
        # Recall@K
        for k in k_list:
            top_k = [r[0] for r in retrieved[:k]]
            hits = len(set(top_k) & set(ground_truth))
            recall = hits / len(ground_truth) if ground_truth else 0
            metrics[f"Recall@{k}"] += recall
            
        # MRR@10
        mrr = 0
        for rank, (doc_name, score) in enumerate(retrieved[:10]):
            if doc_name in ground_truth:
                mrr = 1.0 / (rank + 1)
                break
        metrics["MRR@10"] += mrr

    if valid_queries > 0:
        for key in metrics:
            metrics[key] /= valid_queries
            
    return metrics, per_query_results

def main():
    parser = argparse.ArgumentParser()
    # A
    parser.add_argument("--a_docs", default="research/ab-eval/out/embeddings_text_docs.jsonl")
    parser.add_argument("--a_queries", default="research/ab-eval/out/embeddings_text_queries.jsonl")
    # B
    parser.add_argument("--b1_docs_npy", default="research/ab-eval/out/embeddings_vl_docs_b1.npy")
    parser.add_argument("--b2_docs_npy", default="research/ab-eval/out/embeddings_vl_docs_b2.npy")
    parser.add_argument("--vl_queries_npy", default="research/ab-eval/out/embeddings_vl_queries.npy")
    parser.add_argument("--docs_meta", default="research/ab-eval/out/metadata_docs.json")
    parser.add_argument("--queries_meta", default="research/ab-eval/out/metadata_queries.json")
    # Ground Truth
    parser.add_argument("--labels", default="research/ab-eval/data/labels.toy.json")
    # Output
    parser.add_argument("--out_json", default="research/ab-eval/out/report_all.json")
    parser.add_argument("--out_md", default="research/ab-eval/out/report_all.md")
    args = parser.parse_args()

    # Load labels
    with open(args.labels, 'r') as f:
        labels = json.load(f)

    # 1. Load Variant A (Text Baseline)
    print("Loading Variant A...")
    a_docs_raw = []
    if os.path.exists(args.a_docs):
        with open(args.a_docs, 'r') as f:
            for line in f: a_docs_raw.append(json.loads(line))
    
    a_queries_raw = []
    if os.path.exists(args.a_queries):
        with open(args.a_queries, 'r') as f:
            for line in f: a_queries_raw.append(json.loads(line))

    # 2. Load Metadata and VL Embeddings
    print("Loading Metadata and VL...")
    if not os.path.exists(args.docs_meta):
        print("Error: Missing metadata_docs.json")
        return
    with open(args.docs_meta, 'r') as f:
        docs_meta = json.load(f)
    with open(args.queries_meta, 'r') as f:
        queries_meta = json.load(f)

    doc_names = [d['name'] for d in docs_meta]
    query_ids = [q['id'] for q in queries_meta]

    b1_docs = np.load(args.b1_docs_npy) if os.path.exists(args.b1_docs_npy) else None
    b2_docs = np.load(args.b2_docs_npy) if os.path.exists(args.b2_docs_npy) else None
    vl_queries = np.load(args.vl_queries_npy) if os.path.exists(args.vl_queries_npy) else None

    # Re-align A to metadata order if needed (assuming A was generated from the same corpus)
    # Actually, let's just build matrices for A
    a_doc_map = {d['name']: np.array(d['embedding']) for d in a_docs_raw}
    a_query_map = {q['id']: np.array(q['embedding']) for q in a_queries_raw}
    
    # Check alignment
    a_docs_mtx = np.stack([a_doc_map[name] for name in doc_names]) if a_docs_raw else None
    a_queries_mtx = np.stack([a_query_map[q_id] for q_id in query_ids]) if a_queries_raw else None

    # 3. Compute Scores
    all_scores = {}
    if a_docs_mtx is not None and a_queries_mtx is not None:
        all_scores["A"] = cosine_similarity_matrix(a_queries_mtx, a_docs_mtx)
    
    if b1_docs is not None and vl_queries is not None:
        all_scores["B1"] = cosine_similarity_matrix(vl_queries, b1_docs)
    
    if b2_docs is not None and vl_queries is not None:
        all_scores["B2"] = cosine_similarity_matrix(vl_queries, b2_docs)

    # 4. Hybrid Fusion (Variant C) - Sweep Alpha for A + B2
    hybrid_results = []
    if "A" in all_scores and "B2" in all_scores:
        print("Sweeping alpha for Hybrid A + B2...")
        for alpha in np.linspace(0, 1, 11):
            fused_scores = alpha * all_scores["A"] + (1 - alpha) * all_scores["B2"]
            metrics, _ = calculate_metrics_from_scores(fused_scores, doc_names, query_ids, labels)
            hybrid_results.append({"alpha": round(alpha, 2), "metrics": metrics})
            if alpha == 0.5:
                all_scores["C (alpha=0.5)"] = fused_scores

    # 5. Evaluate all variants
    final_report = {
        "variants": {},
        "hybrid_sweep": hybrid_results
    }

    per_variant_top10 = {}

    for var_name, score_mtx in all_scores.items():
        metrics, results = calculate_metrics_from_scores(score_mtx, doc_names, query_ids, labels)
        final_report["variants"][var_name] = metrics
        
        # Keep top 10 for report
        top10_dump = {}
        for q_id in query_ids:
            if q_id in results:
                top10_dump[q_id] = results[q_id][:10]
        per_variant_top10[var_name] = top10_dump

    final_report["per_query_top10"] = per_variant_top10

    # 6. Save Reports
    with open(args.out_json, 'w') as f:
        json.dump(final_report, f, indent=2)

    with open(args.out_md, 'w') as f:
        f.write("# Overall Retrieval Evaluation Report\n\n")
        
        # Summary Table
        f.write("## Global Metrics\n\n")
        f.write("| Variant | Recall@10 | Recall@20 | MRR@10 |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for var_name, metrics in final_report["variants"].items():
            f.write(f"| {var_name} | {metrics['Recall@10']:.4f} | {metrics['Recall@20']:.4f} | {metrics['MRR@10']:.4f} |\n")
        
        # Alpha Sweep
        if hybrid_results:
            f.write("\n## Hybrid Fusion Alpha Sweep (A + B2)\n\n")
            f.write("| Alpha | Recall@10 | MRR@10 |\n")
            f.write("| :--- | :--- | :--- |\n")
            for entry in hybrid_results:
                f.write(f"| {entry['alpha']} | {entry['metrics']['Recall@10']:.4f} | {entry['metrics']['MRR@10']:.4f} |\n")

        # Per-Query Top 10
        f.write("\n## Per-Query Top 10 Results (Sample)\n\n")
        for q_idx, q_id in enumerate(query_ids[:3]): # Show first 3 queries
            q_text = next((q['text'] for q in queries_meta if q['id'] == q_id), q_id)
            f.write(f"### Query: {q_text} (`{q_id}`)\n\n")
            f.write("| Rank | Variant A | Variant B2 | Variant C (0.5) |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            rows = []
            for rank in range(10):
                row = [str(rank+1)]
                for var in ["A", "B2", "C (alpha=0.5)"]:
                    if var in per_variant_top10 and q_id in per_variant_top10[var]:
                        if rank < len(per_variant_top10[var][q_id]):
                            doc, score = per_variant_top10[var][q_id][rank]
                            row.append(f"{doc} ({score:.3f})")
                        else:
                            row.append("-")
                    else:
                        row.append("-")
                rows.append("| " + " | ".join(row) + " |")
            f.write("\n".join(rows) + "\n\n")

    print(f"Reports saved to {args.out_json} and {args.out_md}")

if __name__ == "__main__":
    main()
