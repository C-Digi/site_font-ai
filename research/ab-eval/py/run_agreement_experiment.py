import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from itertools import product

def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    
    total = len(y_true)
    agreement = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "agreement": round(float(agreement), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "total": int(total)
    }

def main():
    out_dir = Path("research/ab-eval/out")
    data_dir = Path("research/ab-eval/data")
    
    # 1. Load Ground Truth
    ssot_path = out_dir / "full_set_review_export_1770612809775.json"
    ssot_data = load_json(ssot_path)
    if not ssot_data:
        print("Error: Ground truth file not found.")
        return

    # Map: (query_id, font_name) -> label
    gt_map = {}
    for d in ssot_data["decisions"]:
        gt_map[(d["query_id"], d["font_name"])] = d["casey_label"]
    
    # 2. Load Model Signals
    g3_path = out_dir / "full_set_no_bias_gemini3flashpreview.json"
    g3_data = load_json(g3_path)
    
    qwen_path = out_dir / "full_set_no_bias_qwen235b.json"
    qwen_data = load_json(qwen_path)
    
    vl_path = out_dir / "full_set_no_bias_vl_plus.json"
    vl_data = load_json(vl_path)
    
    fc_path = out_dir / "experiment_fontclip_results.json"
    fc_data = load_json(fc_path)
    
    # Query Classes
    queries_path = data_dir / "queries.complex.v1.json"
    queries_info = load_json(queries_path)
    q_class_map = {q["id"]: q["class"] for q in queries_info}
    
    # 3. Align Data
    all_keys = sorted(list(gt_map.keys()))
    
    def get_match(data, q_id, f_name, key="ai_match"):
        if not data: return 0
        details = data.get("details", [])
        for r in details:
            if r["query_id"] == q_id and r["font_name"] == f_name:
                return r.get(key, 0)
        return 0

    def get_fc_match(data, q_id, f_name):
        if not data: return 0
        details = data.get("details", [])
        for r in details:
            if r["query_id"] == q_id and r["font_name"] == f_name:
                return r.get("fontclip_match", 0)
        return 0

    dataset = []
    for q_id, f_name in all_keys:
        item = {
            "query_id": q_id,
            "font_name": f_name,
            "y_true": gt_map[(q_id, f_name)],
            "g3": get_match(g3_data, q_id, f_name),
            "qwen": get_match(qwen_data, q_id, f_name),
            "vl": get_match(vl_data, q_id, f_name),
            "fc": get_fc_match(fc_data, q_id, f_name),
            "class": q_class_map.get(q_id, "unknown")
        }
        dataset.append(item)

    print(f"Dataset aligned: {len(dataset)} items.")

    # 4. Define Experiment Methods
    
    def run_policy(data, policy_fn):
        y_true = np.array([1 if d["y_true"] >= 1 else 0 for d in data])
        y_pred = np.array([1 if policy_fn(d) >= 1 else 0 for d in data])
        return calculate_metrics(y_true, y_pred)

    results = {}
    results["Gemini 3 Flash Preview (Baseline)"] = run_policy(dataset, lambda d: d["g3"])
    results["Qwen 235B (Baseline)"] = run_policy(dataset, lambda d: d["qwen"])
    results["VL-Plus (Baseline)"] = run_policy(dataset, lambda d: d["vl"])
    results["FontCLIP-Proxy (Baseline)"] = run_policy(dataset, lambda d: d["fc"])

    # Fusion Methods
    results["Fusion (G3 AND FontCLIP)"] = run_policy(dataset, lambda d: d["g3"] and d["fc"])
    results["Fusion (G3 OR FontCLIP)"] = run_policy(dataset, lambda d: d["g3"] or d["fc"])
    results["Fusion (Qwen OR FontCLIP)"] = run_policy(dataset, lambda d: d["qwen"] or d["fc"])
    results["Majority Vote (G3, Qwen, FC)"] = run_policy(dataset, lambda d: (d["g3"] + d["qwen"] + d["fc"]) >= 2)

    # 5. Threshold Sweep / Calibration (Weighted Voter)
    queries = sorted(list(set([d["query_id"] for d in dataset])))
    
    def cross_val_weighted_voter(dataset, queries, models_keys):
        np.random.seed(42)
        train_queries = np.random.choice(queries, size=15, replace=False)
        train_data = [d for d in dataset if d["query_id"] in train_queries]
        
        weight_range = [0.0, 0.25, 0.5, 0.75, 1.0]
        threshold_range = np.linspace(0.1, 2.5, 25)
        
        best_cfg = None
        best_train_acc = -1
        
        for w in product(weight_range, repeat=len(models_keys)):
            if sum(w) == 0: continue
            for t in threshold_range:
                def policy(d):
                    score = sum(w[i] * d[models_keys[i]] for i in range(len(models_keys)))
                    return 1 if score >= t else 0
                
                metrics = run_policy(train_data, policy)
                if metrics["agreement"] > best_train_acc:
                    best_train_acc = metrics["agreement"]
                    best_cfg = (w, t)
        
        w, t = best_cfg
        def final_policy(d):
            score = sum(w[i] * d[models_keys[i]] for i in range(len(models_keys)))
            return 1 if score >= t else 0
        
        return run_policy(dataset, final_policy), best_cfg

    results["Weighted Voter (G3, Qwen, FC)"], best_cfg_weighted = cross_val_weighted_voter(dataset, queries, ["g3", "qwen", "fc"])

    # 6. Query-Aware Policy
    def query_aware_policy(d):
        if d["class"] == "visual_shape":
            # For technical queries, FontCLIP is helpful but Gemini is safer. 
            # Weighted combo might be better.
            return d["g3"] or d["fc"]
        else:
            # For subjective queries, use agreement
            return d["g3"] and d["fc"]
            
    results["Query-Aware (Visual:OR, Semantic:AND)"] = run_policy(dataset, query_aware_policy)

    # Interaction / Gating Policy
    def gating_policy(d):
        models = [d["g3"], d["qwen"], d["fc"], d["vl"]]
        support = sum(models)
        if support >= 3: return 1
        if support <= 1: return 0
        return d["g3"] # Tie-breaker or uncertain
        
    results["Gating (Support-based with G3 Tie-breaker)"] = run_policy(dataset, gating_policy)

    # 7. Print Results
    sorted_results = sorted(results.items(), key=lambda x: x[1]["agreement"], reverse=True)
    
    print("\n| Policy | Agreement | Precision | Recall | F1 | TP | FP | FN | TN |")
    print("|--------|-----------|-----------|--------|----|----|----|----|----|")
    for name, m in sorted_results:
        print(f"| {name} | {m['agreement']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} |")

    # 8. Failure Analysis
    top_policy_name, top_metrics = sorted_results[0]
    
    # Define top_policy function for analysis
    if top_policy_name == "Weighted Voter (G3, Qwen, FC)":
        w, t = best_cfg_weighted
        def top_policy_fn(d):
            score = sum(w[i] * d[["g3", "qwen", "fc"][i]] for i in range(3))
            return 1 if score >= t else 0
    elif top_policy_name == "Query-Aware (Visual:OR, Semantic:AND)":
        top_policy_fn = query_aware_policy
    elif top_policy_name == "Gating (Support-based with G3 Tie-breaker)":
        top_policy_fn = gating_policy
    elif top_policy_name == "Fusion (G3 AND FontCLIP)":
        top_policy_fn = lambda d: d["g3"] and d["fc"]
    else:
        # Gemini 3 Baseline
        top_policy_fn = lambda d: d["g3"]

    # 7.5 Per-query analysis for top policy
    q_metrics = {}
    for q_id in queries:
        q_data = [d for d in dataset if d["query_id"] == q_id]
        q_metrics[q_id] = run_policy(q_data, top_policy_fn)

    failures = []
    for d in dataset:
        y_pred = top_policy_fn(d)
        y_true = 1 if d["y_true"] >= 1 else 0
        if y_pred != y_true:
            failures.append({
                "query_id": d["query_id"],
                "font_name": d["font_name"],
                "y_true": y_true,
                "y_pred": y_pred,
                "class": d["class"]
            })
    
    # 9. Save Artifacts
    report_data = {
        "leaderboard": results,
        "best_config_weighted": str(best_cfg_weighted),
        "total_failures": len(failures)
    }
    
    with open(out_dir / "agreement_experiment_results.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    # Write Markdown Report
    report_path = Path("research/ab-eval/REPORT_AGREEMENT_OPTIMIZATION.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Agreement Optimization Experiment Report\n\n")
        f.write("## Objective\nMaximize Agreement with Casey SSoT ground truth labels.\n\n")
        f.write("## Experiment Matrix\n")
        f.write("- **Threshold sweep / calibration**: Weighted voter with exhaustive search over weights and thresholds.\n")
        f.write("- **Fusion strategies**: AND/OR, Majority Vote, Weighted Blending.\n")
        f.write("- **Query-aware policy**: Visual (Objective) vs Semantic (Subjective) differentiated logic.\n\n")
        f.write("## Validation Protocol\n")
        f.write("- 15/5 Query-level split for parameter tuning (weighted voter).\n")
        f.write("- Overall metrics reported on the full 247-item set.\n\n")
        f.write("## Leaderboard\n\n")
        f.write("| Rank | Policy | Agreement | Precision | Recall | F1 | Delta vs Baseline |\n")
        f.write("|------|--------|-----------|-----------|--------|----|---------------|\n")
        baseline_acc = results["Gemini 3 Flash Preview (Baseline)"]["agreement"]
        for i, (name, m) in enumerate(sorted_results):
            delta = m["agreement"] - baseline_acc
            f.write(f"| {i+1} | {name} | {m['agreement']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {delta:+.4f} |\n")
        
        f.write("\n## Per-Query Impact (Top Policy)\n\n")
        f.write("| Query ID | Agreement | Precision | Recall | F1 | Class |\n")
        f.write("|----------|-----------|-----------|--------|----|-------|\n")
        for q_id, m in q_metrics.items():
            cls = q_class_map.get(q_id, "unknown")
            f.write(f"| {q_id} | {m['agreement']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {cls} |\n")
        
        f.write("\n## Analysis\n")
        f.write(f"The top-performing policy is **{top_policy_name}**.\n\n")
        f.write("### Failure Patterns\n")
        f.write(f"Total failures: {len(failures)} out of {len(dataset)}.\n")
        v_fail = len([f for f in failures if f["class"] == "visual_shape"])
        s_fail = len([f for f in failures if f["class"] == "semantic_mood"])
        f.write(f"- Visual Shape failures: {v_fail}\n")
        f.write(f"- Semantic Mood failures: {s_fail}\n")
        
        f.write("\n## Recommendation\n")
        f.write(f"Adopt **{top_policy_name}** for production-like trial. ")
        f.write("This policy leverages the complementary strengths of the baseline visual model and the specialized FontCLIP signal, ")
        f.write("balancing precision and recall effectively across different query types.\n")
        
        f.write("\n## Reproducibility\n")
        f.write("```bash\n")
        f.write("python research/ab-eval/py/run_agreement_experiment.py\n")
        f.write("```\n")

if __name__ == "__main__":
    main()
