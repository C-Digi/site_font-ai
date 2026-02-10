import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from collections import defaultdict

# --- Configuration ---
RESULTS_PATH = Path("research/ab-eval/out/week2_g3pro_v3_1_results.json")
QUERIES_PATH = Path("research/ab-eval/data/queries.medium.human.v1.json")
SSOT_PATH = Path("research/ab-eval/out/full_set_review_export_1770612809775.json")
OUTPUT_DIR = Path("research/ab-eval/out")
REPORT_PATH = Path("research/ab-eval/REPORT_WEEK3_CALIBRATION.md")

TECHNICAL_CLASSES = ["visual_shape"]

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, total_denominator: int = None) -> Dict[str, Any]:
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    
    total = total_denominator if total_denominator is not None else len(y_true)
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
        "total": int(total),
        "coverage": round(float((tp + fp) / total), 4) if total > 0 else 0
    }

def accuracy_score_local(y_true, y_pred):
    if len(y_true) == 0: return 0
    mask = (y_true == 0) | (y_true == 1)
    if np.sum(mask) == 0: return 0
    return np.sum(y_true[mask] == y_pred[mask]) / np.sum(mask)

def main():
    print(f"Loading results from {RESULTS_PATH}...")
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Loading queries from {QUERIES_PATH}...")
    with open(QUERIES_PATH, "r", encoding="utf-8") as f:
        queries = json.load(f)
    q_class_map = {q["id"]: q.get("class", "unclassified") for q in queries}
    
    print(f"Loading SSoT from {SSOT_PATH}...")
    with open(SSOT_PATH, "r", encoding="utf-8") as f:
        ssot_data = json.load(f)
    ssot_map = {(d["query_id"], d["font_name"]): d["casey_label"] for d in ssot_data["decisions"]}

    # 1. Align Data
    dataset = []
    total_items = data["counts"]["total"]
    
    for r in data["details"]:
        q_id = r["query_id"]
        f_name = r["font_name"]
        y_true = ssot_map.get((q_id, f_name), -1) 
        dataset.append({
            "query_id": q_id,
            "font_name": f_name,
            "y_true": y_true,
            "ai_match": r["ai_match"],
            "confidence": r["confidence"],
            "group": "Technical" if q_class_map.get(q_id) in TECHNICAL_CLASSES else "Subjective"
        })

    y_true_all = np.array([d["y_true"] for d in dataset])
    ai_match_all = np.array([d["ai_match"] for d in dataset])
    conf_all = np.array([d["confidence"] for d in dataset])
    q_groups_all = np.array([d["group"] for d in dataset])
    q_ids_all = np.array([d["query_id"] for d in dataset])

    # 2. Baseline (0.9 Gate)
    baseline_pred = np.where((ai_match_all == 1) & (conf_all >= 0.9), 1, 0)
    baseline_metrics = calculate_metrics(y_true_all, baseline_pred, total_denominator=total_items)

    # 3. Global Threshold Sweep
    thresholds = np.linspace(0.0, 1.0, 101)
    global_results = []
    for t in thresholds:
        pred = np.where((ai_match_all == 1) & (conf_all >= t), 1, 0)
        m = calculate_metrics(y_true_all, pred, total_denominator=total_items)
        m["threshold"] = t
        global_results.append(m)
    best_global = max(global_results, key=lambda x: x["agreement"])

    # 4. Group-Aware Thresholding
    groups = np.unique(q_groups_all)
    group_policies = {}
    for grp in groups:
        mask = (q_groups_all == grp)
        grp_results = []
        for t in thresholds:
            pred = np.where((ai_match_all[mask] == 1) & (conf_all[mask] >= t), 1, 0)
            acc = accuracy_score_local(y_true_all[mask], pred)
            grp_results.append({"threshold": t, "accuracy": acc})
        group_policies[grp] = max(grp_results, key=lambda x: x["accuracy"])

    # 5. Validation Protocol (K-Fold by Query)
    unique_queries = np.unique(q_ids_all)
    np.random.seed(42)
    np.random.shuffle(unique_queries)
    folds = np.array_split(unique_queries, 5)
    
    cv_family_metrics = []
    for i in range(5):
        test_mask = np.isin(q_ids_all, folds[i])
        train_mask = ~test_mask
        best_t_family = {}
        for grp in groups:
            mask = train_mask & (q_groups_all == grp)
            if np.sum(mask) == 0: continue
            train_results = []
            for t in thresholds:
                pred = np.where((ai_match_all[mask] == 1) & (conf_all[mask] >= t), 1, 0)
                train_results.append((t, accuracy_score_local(y_true_all[mask], pred)))
            best_t_family[grp] = max(train_results, key=lambda x: x[1])[0]
        
        test_pred = np.zeros(np.sum(test_mask))
        tm, tc, tg = ai_match_all[test_mask], conf_all[test_mask], q_groups_all[test_mask]
        for idx in range(len(test_pred)):
            t = best_t_family.get(tg[idx], 0.9)
            if tm[idx] == 1 and tc[idx] >= t: test_pred[idx] = 1
        cv_family_metrics.append(calculate_metrics(y_true_all[test_mask], test_pred))

    def aggregate(ml):
        agg = defaultdict(float)
        for m in ml:
            for k, v in m.items():
                if k != "counts" and not isinstance(v, dict): agg[k] += v
        return {k: round(v / len(ml), 4) for k, v in agg.items()}
    cv_final = aggregate(cv_family_metrics)

    # 6. Final Selection
    final_pred = np.zeros_like(y_true_all)
    for i in range(len(final_pred)):
        t = group_policies[q_groups_all[i]]["threshold"]
        if ai_match_all[i] == 1 and conf_all[i] >= t: final_pred[i] = 1
    final_metrics = calculate_metrics(y_true_all, final_pred, total_denominator=total_items)

    # 7. Calibration Curve
    cal_bins = [0.8, 0.85, 0.9, 0.95, 1.0]
    cal_stats = []
    for b in cal_bins:
        mask = (conf_all == b) & (ai_match_all == 1) & ((y_true_all == 0) | (y_true_all == 1))
        if np.sum(mask) > 0:
            acc = np.sum(y_true_all[mask] == 1) / np.sum(mask)
            cal_stats.append({"conf": b, "accuracy": round(acc, 4), "count": int(np.sum(mask))})

    # 8. Output
    results = {
        "baseline": baseline_metrics,
        "global_best": best_global,
        "group_policies": group_policies,
        "cv_final": cv_final,
        "final_policy": final_metrics,
        "calibration": cal_stats
    }
    with open(OUTPUT_DIR / "week3_calibration_results.json", "w") as f:
        json.dump(results, f, indent=2)

    with open(REPORT_PATH, "w") as f:
        f.write("# Week 3 Report: Dynamic Threshold Calibration\n\n")
        f.write("## Objective\nMaximize Agreement with SSoT using dynamic confidence gating.\n\n")
        f.write("## Calibration Methods\n- Baseline: Fixed 0.9 gate\n- Global Sweep: Optimal single T\n- Group-Aware: T optimized for Technical vs Subjective queries\n\n")
        
        f.write("## Leaderboard\n\n")
        f.write("| Policy | Agreement | Precision | Recall | F1 | TP | FP | FN | TN | Cov | Delta |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        f.write(f"| Baseline (0.9) | {baseline_metrics['agreement']:.4f} | {baseline_metrics['precision']:.4f} | {baseline_metrics['recall']:.4f} | {baseline_metrics['f1']:.4f} | {baseline_metrics['tp']} | {baseline_metrics['fp']} | {baseline_metrics['fn']} | {baseline_metrics['tn']} | {baseline_metrics['coverage']:.4f} | +0.0000 |\n")
        f.write(f"| Global ({best_global['threshold']:.2f}) | {best_global['agreement']:.4f} | {best_global['precision']:.4f} | {best_global['recall']:.4f} | {best_global['f1']:.4f} | {best_global['tp']} | {best_global['fp']} | {best_global['fn']} | {best_global['tn']} | {best_global['coverage']:.4f} | {best_global['agreement']-baseline_metrics['agreement']:+.4f} |\n")
        f.write(f"| **Dynamic** | **{final_metrics['agreement']:.4f}** | {final_metrics['precision']:.4f} | {final_metrics['recall']:.4f} | {final_metrics['f1']:.4f} | {final_metrics['tp']} | {final_metrics['fp']} | {final_metrics['fn']} | {final_metrics['tn']} | {final_metrics['coverage']:.4f} | {final_metrics['agreement']-baseline_metrics['agreement']:+.4f} |\n\n")
        
        f.write("## Recommended Policy\n\n| Group | Threshold |\n| :--- | :--- |\n")
        for g, p in group_policies.items(): f.write(f"| {g} | {p['threshold']:.2f} |\n")
        
        f.write("\n## Observed Accuracy vs Confidence\n\n| Conf | Accuracy | Count |\n| :--- | :--- | :--- |\n")
        for s in cal_stats: f.write(f"| {s['conf']} | {s['accuracy']:.4f} | {s['count']} |\n")

    print(f"Report: {REPORT_PATH}")

if __name__ == "__main__":
    main()
