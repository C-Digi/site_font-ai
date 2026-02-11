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

def calculate_metrics_from_scores(score_matrix, doc_names, query_ids, labels, k_list=[10, 20], query_id_to_class=None):
    """
    score_matrix: (N_q, N_d)
    doc_names: list of N_d strings
    query_ids: list of N_q strings
    labels: { query_id: [ doc_name, ... ] }
    query_id_to_class: { query_id: class_name }
    """
    metrics = {
        "Recall@10": 0,
        "Recall@20": 0,
        "MRR@10": 0
    }
    num_queries = len(query_ids)
    valid_queries = 0

    per_query_results = {}
    
    # Initialize class metrics
    class_metrics = {}
    if query_id_to_class:
        for cls in set(query_id_to_class.values()):
            class_metrics[cls] = {
                "Recall@10": 0,
                "Recall@20": 0,
                "MRR@10": 0,
                "count": 0
            }

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
        
        q_recall10 = 0
        q_recall20 = 0
        q_mrr10 = 0

        # Recall@K
        for k in k_list:
            top_k = [r[0] for r in retrieved[:k]]
            hits = len(set(top_k) & set(ground_truth))
            recall = hits / len(ground_truth) if ground_truth else 0
            metrics[f"Recall@{k}"] += recall
            if k == 10: q_recall10 = recall
            if k == 20: q_recall20 = recall
            
        # MRR@10
        mrr = 0
        for rank, (doc_name, score) in enumerate(retrieved[:10]):
            if doc_name in ground_truth:
                mrr = 1.0 / (rank + 1)
                break
        metrics["MRR@10"] += mrr
        q_mrr10 = mrr

        # Class breakdown
        if query_id_to_class and q_id in query_id_to_class:
            cls = query_id_to_class[q_id]
            class_metrics[cls]["Recall@10"] += q_recall10
            class_metrics[cls]["Recall@20"] += q_recall20
            class_metrics[cls]["MRR@10"] += q_mrr10
            class_metrics[cls]["count"] += 1

    if valid_queries > 0:
        for key in metrics:
            metrics[key] /= valid_queries
            
    # Finalize class metrics
    final_class_metrics = {}
    for cls, cm in class_metrics.items():
        if cm["count"] > 0:
            final_class_metrics[cls] = {
                "Recall@10": cm["Recall@10"] / cm["count"],
                "Recall@20": cm["Recall@20"] / cm["count"],
                "MRR@10": cm["MRR@10"] / cm["count"],
                "count": cm["count"]
            }
            
    return metrics, per_query_results, final_class_metrics

def reciprocal_rank_fusion(score_matrices, k=60):
    """
    score_matrices: list of (N_q, N_d) matrices
    Returns: fused (N_q, N_d) matrix
    """
    fused_scores = np.zeros_like(score_matrices[0])
    for m in score_matrices:
        for i in range(m.shape[0]):
            scores = m[i]
            ranks = np.empty_like(scores, dtype=int)
            indices = np.argsort(scores)[::-1]
            ranks[indices] = np.arange(len(scores)) + 1
            fused_scores[i] += 1.0 / (k + ranks)
    return fused_scores

def main():
    parser = argparse.ArgumentParser()
    # A
    parser.add_argument("--a_docs", default="research/ab-eval/out/embeddings_text_docs.jsonl")
    parser.add_argument("--a_queries", default="research/ab-eval/out/embeddings_text_queries.jsonl")
    # B
    parser.add_argument("--b1_docs_npy", default="research/ab-eval/out/embeddings_vl_docs_b1.npy")
    parser.add_argument("--b2_docs_npy", default="research/ab-eval/out/embeddings_vl_docs_b2.npy")
    parser.add_argument("--b2plus_docs_npy", default="research/ab-eval/out/embeddings_vl_docs_b2plus.npy")
    parser.add_argument("--vl_queries_npy", default="research/ab-eval/out/embeddings_vl_queries.npy")
    parser.add_argument("--docs_meta", default="research/ab-eval/out/metadata_docs.json")
    parser.add_argument("--queries_meta", default="research/ab-eval/out/metadata_queries.json")
    parser.add_argument("--queries", help="Path to original queries file (to get classes)")
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

    # Load classes if queries file is provided
    query_id_to_class = None
    if args.queries and os.path.exists(args.queries):
        with open(args.queries, 'r') as f:
            q_data = json.load(f)
            query_id_to_class = {q['id']: q.get('class', 'unclassified') for q in q_data}

    # Load VL and check alignment
    vl_queries = None
    if os.path.exists(args.vl_queries_npy):
        raw_vl = np.load(args.vl_queries_npy)
        if len(raw_vl) == len(query_ids):
            vl_queries = raw_vl
        else:
            print(f"Warning: VL query embeddings shape {raw_vl.shape} doesn't match query count {len(query_ids)}. Skipping VL variants.")

    b1_docs = np.load(args.b1_docs_npy) if os.path.exists(args.b1_docs_npy) else None
    b2_docs = np.load(args.b2_docs_npy) if os.path.exists(args.b2_docs_npy) else None
    b2plus_docs = np.load(args.b2plus_docs_npy) if os.path.exists(args.b2plus_docs_npy) else None

    # Re-align A to metadata order if needed
    a_doc_map = {d['name']: np.array(d['embedding']) for d in a_docs_raw}
    a_query_map = {q['id']: np.array(q['embedding']) for q in a_queries_raw}
    
    # Check alignment
    a_docs_mtx = np.stack([a_doc_map[name] for name in doc_names]) if a_docs_raw and all(name in a_doc_map for name in doc_names) else None
    a_queries_mtx = np.stack([a_query_map[q_id] for q_id in query_ids]) if a_queries_raw and all(q_id in a_query_map for q_id in query_ids) else None

    # 3. Compute Scores
    all_scores = {}
    if a_docs_mtx is not None and a_queries_mtx is not None:
        all_scores["A"] = cosine_similarity_matrix(a_queries_mtx, a_docs_mtx)
    
    if b1_docs is not None and vl_queries is not None:
        all_scores["B1"] = cosine_similarity_matrix(vl_queries, b1_docs)
    
    if b2_docs is not None and vl_queries is not None:
        all_scores["B2"] = cosine_similarity_matrix(vl_queries, b2_docs)
    
    if b2plus_docs is not None and vl_queries is not None:
        all_scores["B2-plus"] = cosine_similarity_matrix(vl_queries, b2plus_docs)

    # 4. Hybrid Fusion (Variant C) - Sweep Alpha for A + B2
    hybrid_results = []
    if "A" in all_scores and "B2" in all_scores:
        if all_scores["A"].shape == all_scores["B2"].shape:
            print("Sweeping alpha for Hybrid A + B2...")
            for alpha in np.linspace(0, 1, 11):
                fused_scores = alpha * all_scores["A"] + (1 - alpha) * all_scores["B2"]
                metrics, _, _ = calculate_metrics_from_scores(fused_scores, doc_names, query_ids, labels, query_id_to_class=query_id_to_class)
                hybrid_results.append({"alpha": round(alpha, 2), "metrics": metrics})
                if alpha == 0.5:
                    all_scores["C (alpha=0.5)"] = fused_scores
        else:
            print(f"Warning: Skipping Hybrid fusion (C) due to shape mismatch: A={all_scores['A'].shape}, B2={all_scores['B2'].shape}")

    # 4b. Variant D (RRF of A and B2)
    if "A" in all_scores and "B2" in all_scores:
        if all_scores["A"].shape == all_scores["B2"].shape:
            print("Computing Variant D (RRF of A and B2)...")
            all_scores["D (RRF)"] = reciprocal_rank_fusion([all_scores["A"], all_scores["B2"]])
        else:
            print(f"Warning: Skipping Variant D (RRF) due to shape mismatch: A={all_scores['A'].shape}, B2={all_scores['B2'].shape}")

    # 5. Evaluate all variants
    final_report = {
        "variants": {},
        "hybrid_sweep": hybrid_results
    }

    per_variant_top10 = {}
    per_variant_class_metrics = {}

    for var_name, score_mtx in all_scores.items():
        metrics, results, class_metrics = calculate_metrics_from_scores(score_mtx, doc_names, query_ids, labels, query_id_to_class=query_id_to_class)
        final_report["variants"][var_name] = metrics
        per_variant_class_metrics[var_name] = class_metrics
        
        # Keep top 10 for report
        top10_dump = {}
        for q_id in query_ids:
            if q_id in results:
                top10_dump[q_id] = results[q_id][:10]
        per_variant_top10[var_name] = top10_dump

    final_report["per_query_top10"] = per_variant_top10

    # Helps/Hurts Analysis (B2 vs A)
    if "A" in variants and "B2" in variants:
        helps = []
        hurts = []
        for q_id in query_ids:
            if q_id not in labels: continue
            
            # Re-calculate recall for this query
            ground_truth = labels[q_id]
            
            def get_recall10(var_name):
                top_k = [r[0] for r in per_variant_top10[var_name][q_id][:10]]
                hits = len(set(top_k) & set(ground_truth))
                return hits / len(ground_truth) if ground_truth else 0
            
            r_a = get_recall10("A")
            r_b = get_recall10("B2")
            
            if r_b > r_a:
                helps.append(q_id)
            elif r_b < r_a:
                hurts.append(q_id)
        
        final_report["helps_hurts"] = {
            "helps_count": len(helps),
            "hurts_count": len(hurts),
            "helps": helps,
            "hurts": hurts
        }

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
        
        if "helps_hurts" in final_report:
            hh = final_report["helps_hurts"]
            f.write("\n## Helps/Hurts Analysis (B2 vs A)\n")
            f.write(f"- **Helps**: {hh['helps_count']}\n")
            f.write(f"- **Hurts**: {hh['hurts_count']}\n")
            f.write(f"- **Net**: {hh['helps_count'] - hh['hurts_count']}\n")

        if "helps_hurts" in final_report:
            hh = final_report["helps_hurts"]
            f.write("\n## Helps/Hurts Analysis (B2 vs A)\n")
            f.write(f"- **Helps**: {hh['helps_count']}\n")
            f.write(f"- **Hurts**: {hh['hurts_count']}\n")
            f.write(f"- **Net**: {hh['helps_count'] - hh['hurts_count']}\n")

        # Class Breakdown Tables
        if query_id_to_class:
            f.write("\n## Per-Class Breakdown\n")
            classes = sorted(set(query_id_to_class.values()))
            for cls in classes:
                f.write(f"\n### Class: {cls}\n\n")
                f.write("| Variant | Recall@10 | Recall@20 | MRR@10 | Count |\n")
                f.write("| :--- | :--- | :--- | :--- | :--- |\n")
                for var_name in all_scores.keys():
                    if var_name in per_variant_class_metrics and cls in per_variant_class_metrics[var_name]:
                        cm = per_variant_class_metrics[var_name][cls]
                        f.write(f"| {var_name} | {cm['Recall@10']:.4f} | {cm['Recall@20']:.4f} | {cm['MRR@10']:.4f} | {cm['count']} |\n")

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
            f.write("| Rank | Variant A | Variant B2 | Variant B2-plus | Variant D (RRF) |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            
            rows = []
            for rank in range(10):
                row = [str(rank+1)]
                for var in ["A", "B2", "B2-plus", "D (RRF)"]:
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
