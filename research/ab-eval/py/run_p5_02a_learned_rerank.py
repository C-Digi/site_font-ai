"""
P5-02A Learned Reranker Trial
Deterministic offline evaluation path for cross-encoder reranking.

Implementation:
- Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2 (sentence-transformers)
- Top-K: 20 candidates from baseline retrieval
- Payload: name + category + tags + desc
- Score Fusion: final_score = 0.6 * normalized_sim + 0.4 * rerank_score
- Normalization: per-query min-max + epsilon safety
- Threshold Sweep: [0.40, 0.45, 0.50]
- Determinism: seed 42, stable sorting/tie-break
- Variant ID: p5_02a_learned_rerank
"""
import json
import argparse
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


def remap_label(label: Any) -> int:
    """Governance policy: non-binary label 2 is treated as 0 for primary metrics."""
    if label == 2:
        return 0
    return 1 if label == 1 else 0


def normalize_scores(scores: List[float], epsilon: float = 1e-9) -> List[float]:
    """Per-query min-max normalization with epsilon safety."""
    if not scores:
        return scores
    
    min_s = min(scores)
    max_s = max(scores)
    range_s = max_s - min_s
    
    if range_s < epsilon:
        return [0.5] * len(scores)
    
    return [(s - min_s) / range_s for s in scores]


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_font_payload(font_data: Dict[str, Any]) -> str:
    """Build text payload for reranker: name + category + tags + desc."""
    parts = []
    
    name = font_data.get("name", "")
    if name:
        parts.append(f"Font: {name}")
    
    category = font_data.get("category", "")
    if category:
        parts.append(f"Category: {category}")
    
    tags = font_data.get("tags", [])
    if isinstance(tags, list) and tags:
        parts.append(f"Tags: {', '.join(tags)}")
    elif isinstance(tags, str) and tags:
        parts.append(f"Tags: {tags}")
    
    desc = font_data.get("description", "")
    if desc:
        parts.append(f"Description: {desc}")
    
    return " | ".join(parts)


def compute_metrics(results: List[Dict], ssot_map: Dict) -> Dict[str, Any]:
    """Compute confusion matrix metrics for a result set."""
    tp = fp = fn = tn = 0
    
    for r in results:
        key = (r["query_id"], r["font_name"])
        if key not in ssot_map:
            continue
        
        h = ssot_map[key]
        a = r["predicted_match"]
        
        if h == 1 and a == 1:
            tp += 1
        elif h == 0 and a == 1:
            fp += 1
        elif h == 1 and a == 0:
            fn += 1
        elif h == 0 and a == 0:
            tn += 1
    
    total = tp + fp + fn + tn
    agreement = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "agreement": round(agreement, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "counts": {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "total": total},
    }


def compute_helps_hurts(
    results: List[Dict],
    ssot_map: Dict,
    baseline_key: str = "v3_match"
) -> Tuple[List[Dict], List[Dict]]:
    """Compute helps/hurts analysis comparing treatment to baseline."""
    helps = []
    hurts = []
    
    for r in results:
        key = (r["query_id"], r["font_name"])
        if key not in ssot_map:
            continue
        
        h = ssot_map[key]
        baseline_pred = r.get(baseline_key, 0)
        treatment_pred = r["predicted_match"]
        
        baseline_ok = baseline_pred == h
        treatment_ok = treatment_pred == h
        
        if (not baseline_ok) and treatment_ok:
            helps.append({
                "query_id": r["query_id"],
                "font_name": r["font_name"],
                "human": h,
                "v3_pred": baseline_pred,
                "p5_02a_pred": treatment_pred,
            })
        elif baseline_ok and (not treatment_ok):
            hurts.append({
                "query_id": r["query_id"],
                "font_name": r["font_name"],
                "human": h,
                "v3_pred": baseline_pred,
                "p5_02a_pred": treatment_pred,
            })
    
    return helps, hurts


def run_reranker_trial(
    v3_results: Dict,
    ssot_data: Dict,
    corpus: List[Dict],
    queries: List[Dict],
    cross_encoder,
    top_k: int = 20,
    alpha: float = 0.6,
    threshold: float = 0.45,
) -> Tuple[List[Dict], Dict]:
    """
    Run the learned reranker trial with specified parameters.
    
    Args:
        v3_results: Baseline v3 gated results
        ssot_data: Human labels SSoT
        corpus: Font corpus
        queries: Query set
        cross_encoder: The cross-encoder model
        top_k: Number of candidates to rerank
        alpha: Weight for normalized similarity (1-alpha for rerank)
        threshold: Decision threshold for final_score
    
    Returns:
        Tuple of (results_list, metrics_dict)
    """
    # Build lookup maps
    font_map = {f["name"]: f for f in corpus}
    query_text_map = {q["id"]: q["text"] for q in queries}
    
    # Build SSoT map
    ssot_map = {}
    for d in ssot_data["decisions"]:
        key = (d["query_id"], d["font_name"])
        ssot_map[key] = remap_label(d.get("casey_label", 0))
    
    # Extract v3 details
    v3_details = v3_results.get("details", [])
    
    # Group by query for reranking
    query_to_candidates: Dict[str, List[Dict[str, Any]]] = {}
    for d in v3_details:
        qid = d["query_id"]
        if qid not in query_to_candidates:
            query_to_candidates[qid] = []
        query_to_candidates[qid].append(d)
    
    # Process each query
    reranked_results = []
    
    for qid in sorted(query_to_candidates.keys()):
        candidates = query_to_candidates[qid]
        query_text = query_text_map.get(qid, "")
        
        # Sort by confidence (stable sort for determinism) and take top-K
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (-x.get("confidence", 0), x.get("font_name", "")),
        )
        top_k_candidates = sorted_candidates[:top_k]
        
        if not top_k_candidates:
            continue
        
        # Build payloads for cross-encoder
        font_payloads = []
        for c in top_k_candidates:
            font_name = c["font_name"]
            font_data = font_map.get(font_name, {})
            payload = build_font_payload(font_data)
            font_payloads.append(payload)
        
        # Compute cross-encoder scores
        query_font_pairs = [(query_text, payload) for payload in font_payloads]
        try:
            rerank_scores = cross_encoder.predict(query_font_pairs)
            # Convert to list if numpy array
            if hasattr(rerank_scores, 'tolist'):
                rerank_scores = rerank_scores.tolist()
        except Exception as e:
            print(f"Warning: Cross-encoder failed for query {qid}: {e}")
            rerank_scores = [0.5] * len(query_font_pairs)
        
        # Normalize rerank scores
        norm_rerank = normalize_scores(rerank_scores)
        
        # Normalize confidence (as proxy for similarity)
        confidences = [c.get("confidence", 0.5) for c in top_k_candidates]
        norm_conf = normalize_scores(confidences)
        
        # Apply fusion and decision
        for i, c in enumerate(top_k_candidates):
            final_score = alpha * norm_conf[i] + (1 - alpha) * norm_rerank[i]
            
            original_ai_match = c.get("ai_match", 0)
            original_gated = c.get("ai_match_gated", 0)
            
            # Decision logic: require original AI match AND fusion threshold
            if original_ai_match == 1 and final_score >= threshold:
                predicted_match = 1
            else:
                predicted_match = 0
            
            reranked_results.append({
                "query_id": qid,
                "font_name": c["font_name"],
                "ai_match": original_ai_match,
                "confidence": c.get("confidence", 0.5),
                "v3_match": original_gated,
                "rerank_score": round(rerank_scores[i], 4),
                "norm_rerank": round(norm_rerank[i], 4),
                "norm_conf": round(norm_conf[i], 4),
                "final_score": round(final_score, 4),
                "predicted_match": predicted_match,
            })
    
    # Compute metrics
    metrics = compute_metrics(reranked_results, ssot_map)
    
    return reranked_results, metrics


def main():
    parser = argparse.ArgumentParser(description="P5-02A Learned Reranker Trial")
    parser.add_argument("--v3-results", default="research/ab-eval/out/g3_v3_gated_results.json",
                        help="Path to v3 champion results")
    parser.add_argument("--ssot", default="research/ab-eval/out/full_set_review_export_1770612809775.json",
                        help="Path to SSoT human labels")
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.200.json",
                        help="Path to font corpus")
    parser.add_argument("--queries", default="research/ab-eval/data/queries.medium.human.v1.json",
                        help="Path to queries")
    parser.add_argument("--output-dir", default="research/ab-eval/out",
                        help="Output directory")
    parser.add_argument("--top-k", type=int, default=20,
                        help="Top-K candidates for reranking")
    parser.add_argument("--alpha", type=float, default=0.6,
                        help="Weight for normalized similarity (1-alpha for rerank)")
    parser.add_argument("--thresholds", type=str, default="0.40,0.45,0.50",
                        help="Comma-separated threshold values to sweep")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for determinism")
    parser.add_argument("--model", default="cross-encoder/ms-marco-MiniLM-L-6-v2",
                        help="Cross-encoder model name")
    args = parser.parse_args()
    
    # Set seeds for determinism
    random.seed(args.seed)
    np.random.seed(args.seed)
    
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("Loading data...")
    v3_results = load_json(Path(args.v3_results))
    ssot_data = load_json(Path(args.ssot))
    corpus = load_json(Path(args.corpus))
    queries = load_json(Path(args.queries))
    
    # Build SSoT map for later use
    ssot_map = {}
    for d in ssot_data["decisions"]:
        key = (d["query_id"], d["font_name"])
        ssot_map[key] = remap_label(d.get("casey_label", 0))
    
    # Load cross-encoder model
    print(f"Loading cross-encoder model: {args.model}")
    try:
        from sentence_transformers import CrossEncoder
        cross_encoder = CrossEncoder(args.model)
        # Set to eval mode for deterministic behavior
        cross_encoder.eval()
    except ImportError:
        print("ERROR: sentence-transformers not installed.")
        print("Install with: pip install sentence-transformers")
        return
    except Exception as e:
        print(f"ERROR: Failed to load cross-encoder: {e}")
        return
    
    # Parse thresholds
    thresholds = [float(t.strip()) for t in args.thresholds.split(",")]
    
    # Run threshold sweep
    print(f"\nRunning threshold sweep: {thresholds}")
    sweep_results = {}
    
    for threshold in thresholds:
        print(f"\n--- Threshold: {threshold} ---")
        
        results, metrics = run_reranker_trial(
            v3_results=v3_results,
            ssot_data=ssot_data,
            corpus=corpus,
            queries=queries,
            cross_encoder=cross_encoder,
            top_k=args.top_k,
            alpha=args.alpha,
            threshold=threshold,
        )
        
        sweep_results[threshold] = {
            "metrics": metrics,
            "results_count": len(results),
        }
        
        print(f"Agreement: {metrics['agreement']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1: {metrics['f1']:.4f}")
    
    # Select best threshold by agreement (tie-break: precision)
    best_threshold = max(
        thresholds,
        key=lambda t: (
            sweep_results[t]["metrics"]["agreement"],
            sweep_results[t]["metrics"]["precision"]
        )
    )
    print(f"\nBest threshold by Agreement (tie-break Precision): {best_threshold}")
    
    # Run final evaluation with best threshold
    final_results, final_metrics = run_reranker_trial(
        v3_results=v3_results,
        ssot_data=ssot_data,
        corpus=corpus,
        queries=queries,
        cross_encoder=cross_encoder,
        top_k=args.top_k,
        alpha=args.alpha,
        threshold=best_threshold,
    )
    
    # Extract v3 metrics for comparison
    v3_metrics = {
        "agreement": v3_results.get("agreement", 0),
        "precision": v3_results.get("precision", 0),
        "recall": v3_results.get("recall", 0),
        "f1": v3_results.get("f1", 0),
        "counts": v3_results.get("counts", {}),
    }
    
    # Compute helps/hurts
    helps, hurts = compute_helps_hurts(final_results, ssot_map)
    
    # Build comparison output
    comparison = {
        "metadata": {
            "run_id": "p5_02a_learned_rerank",
            "variant_id": "p5_02a_learned_rerank",
            "baseline": "v3",
            "model": args.model,
            "top_k": args.top_k,
            "alpha": args.alpha,
            "best_threshold": best_threshold,
            "threshold_sweep": thresholds,
            "seed": args.seed,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
        "variants": {
            "v3": v3_metrics,
            "p5_02a_learned_rerank": final_metrics,
        },
        "delta_treatment_minus_baseline": {
            "agreement": round(final_metrics["agreement"] - v3_metrics["agreement"], 4),
            "precision": round(final_metrics["precision"] - v3_metrics["precision"], 4),
            "recall": round(final_metrics["recall"] - v3_metrics["recall"], 4),
            "f1": round(final_metrics["f1"] - v3_metrics["f1"], 4),
        },
        "threshold_sweep_results": {
            str(t): sweep_results[t]["metrics"] for t in thresholds
        },
        "helps_hurts": {
            "helps_count": len(helps),
            "hurts_count": len(hurts),
            "net": len(helps) - len(hurts),
        },
        "helps": helps,
        "hurts": hurts,
    }
    
    # Save comparison
    comparison_path = out_dir / "p5_02a_v3_vs_p5_02a_comparison.json"
    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)
    print(f"\nSaved comparison to {comparison_path}")
    
    # Build gates output
    gates = {
        "G1 (Agreement Delta)": {
            "status": "PASS" if comparison["delta_treatment_minus_baseline"]["agreement"] >= 0.01 else "FAIL",
            "value": comparison["delta_treatment_minus_baseline"]["agreement"],
            "threshold": ">= 0.01",
        },
        "G2 (Precision Delta)": {
            "status": "PASS" if comparison["delta_treatment_minus_baseline"]["precision"] >= -0.02 else "FAIL",
            "value": comparison["delta_treatment_minus_baseline"]["precision"],
            "threshold": ">= -0.02",
        },
        "G3 (Helps/Hurts Net)": {
            "status": "PASS" if comparison["helps_hurts"]["net"] > 0 else "FAIL",
            "value": comparison["helps_hurts"]["net"],
            "threshold": "> 0",
        },
        "G4 (Visual QA)": {
            "status": "PENDING",
            "value": "Manual",
            "threshold": "Zero clipping/overlap",
        },
    }
    
    all_pass = all(g["status"] == "PASS" for g in gates.values())
    
    gates_output = {
        "success": all_pass,
        "gates": gates,
        "metadata": comparison["metadata"],
    }
    
    gates_path = out_dir / "p5_02a_v3_vs_p5_02a_gates.json"
    with open(gates_path, "w", encoding="utf-8") as f:
        json.dump(gates_output, f, indent=2)
    print(f"Saved gates to {gates_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("P5-02A LEARNED RERANKER TRIAL RESULTS")
    print("=" * 60)
    print(f"\nVariant: p5_02a_learned_rerank")
    print(f"Baseline: v3")
    print(f"Model: {args.model}")
    print(f"Top-K: {args.top_k}")
    print(f"Alpha (sim weight): {args.alpha}")
    print(f"Best Threshold: {best_threshold}")
    
    print("\n--- THRESHOLD SWEEP ---")
    print(f"{'Threshold':<12} {'Agreement':<12} {'Precision':<12} {'Recall':<12}")
    print("-" * 48)
    for t in thresholds:
        m = sweep_results[t]["metrics"]
        marker = " *" if t == best_threshold else ""
        print(f"{t:<12} {m['agreement']:<12.4f} {m['precision']:<12.4f} {m['recall']:<12.4f}{marker}")
    
    print("\n--- METRICS (Best Threshold) ---")
    print(f"{'Metric':<15} {'v3':<10} {'p5_02a':<10} {'Delta':<10}")
    print("-" * 45)
    for m in ["agreement", "precision", "recall", "f1"]:
        v3_v = v3_metrics.get(m, 0)
        p5_v = final_metrics.get(m, 0)
        delta = comparison["delta_treatment_minus_baseline"][m]
        print(f"{m:<15} {v3_v:<10.4f} {p5_v:<10.4f} {delta:+.4f}")
    
    print("\n--- GATES ---")
    for name, g in gates.items():
        print(f"{name}: {g['status']} (value={g['value']}, threshold={g['threshold']})")
    
    print(f"\nHelps/Hurts/Net: {len(helps)}/{len(hurts)}/{len(helps)-len(hurts)}")
    print(f"\nOverall: {'PASS (GO)' if all_pass else 'FAIL (NO-GO)'}")


if __name__ == "__main__":
    main()
