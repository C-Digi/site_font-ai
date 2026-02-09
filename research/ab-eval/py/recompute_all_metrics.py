import json
from pathlib import Path
from typing import List, Dict, Any

def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    tp = fp = fn = tn = 0
    for r in results:
        h = r["human_match"]
        a = r["ai_match"]
        if h == 1 and a == 1: tp += 1
        elif h == 0 and a == 1: fp += 1
        elif h == 1 and a == 0: fn += 1
        elif h == 0 and a == 0: tn += 1
        
    total = len(results)
    agreement = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "agreement": round(agreement, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "counts": {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "total": total}
    }

def main():
    out_dir = Path("research/ab-eval/out")
    ssot_path = out_dir / "full_set_review_export_1770612809775.json"
    
    with open(ssot_path, "r") as f:
        ssot_data = json.load(f)
        
    # Create mapping: (query_id, font_name) -> label
    ssot_map = {}
    for decision in ssot_data["decisions"]:
        key = (decision["query_id"], decision["font_name"])
        ssot_map[key] = decision["casey_label"]
        
    models = {
        "Qwen 235B": "full_set_no_bias_qwen235b.json",
        "VL-Plus": "full_set_no_bias_vl_plus.json",
        "Gemini 2.5 Flash Lite": "full_set_no_bias_gemini25.json",
        "Gemini 3 Flash Preview": "full_set_no_bias_gemini3flashpreview.json"
    }
    
    final_metrics = {}
    
    for model_name, filename in models.items():
        path = out_dir / filename
        if not path.exists():
            print(f"Skipping {model_name}: {path} not found")
            continue
            
        with open(path, "r") as f:
            data = json.load(f)
            details = data.get("details", [])
            
        # Update results with amended SSoT
        updated_results = []
        missing_ssot = 0
        for r in details:
            key = (r["query_id"], r["font_name"])
            if key in ssot_map:
                r["human_match"] = ssot_map[key]
                updated_results.append(r)
            else:
                # If missing in SSoT, we can't reliably recompute metrics for this pair
                # but let's keep it if we want to see model output, 
                # just might not be part of "official" recomputation
                missing_ssot += 1
        
        metrics = calculate_metrics(updated_results)
        final_metrics[model_name] = {
            "metrics": metrics,
            "total_updated": len(updated_results),
            "missing_ssot": missing_ssot
        }
        
        # Save updated results back? Maybe better to save to a new file to be safe
        updated_filename = filename.replace(".json", "_updated_ssot.json")
        with open(out_dir / updated_filename, "w") as f:
            json.dump({"details": updated_results, "metrics": metrics}, f, indent=2)

    # Print summary table
    print("| Model | Agreement | Precision | Recall | F1 | TP | FP | FN | TN | Total |")
    print("|-------|-----------|-----------|--------|----|----|----|----|----|-------|")
    for name, data in final_metrics.items():
        m = data["metrics"]
        c = m["counts"]
        print(f"| {name} | {m['agreement']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {c['tp']} | {c['fp']} | {c['fn']} | {c['tn']} | {c['total']} |")

    # Generate Markdown Report
    report_path = Path("research/ab-eval/comprehensive_model_comparison_report.md")
    with open(report_path, "w") as f:
        f.write("# Comprehensive Model Comparison Report (Updated SSoT)\n\n")
        f.write(f"Generated on: {ssot_data['timestamp']}\n\n")
        f.write("## Overview\n")
        f.write("This report compares multiple vision models on the font discovery task using the amended human Source of Truth (SSoT) labels from `full_set_review_export_1770612809775.json`.\n\n")
        
        f.write("## Batching Implementation Summary\n")
        f.write("- Upgraded `run_full_comparison.py` to support batched requests (up to 10 queries per specimen).\n")
        f.write("- Ported logic from `run_spot_check_alignment_models.py`.\n")
        f.write("- Ensured deterministic behavior and bias prevention (no font names in prompt).\n\n")
        
        f.write("## Amended SSoT Parsing Assumptions\n")
        f.write("- Used `casey_label` from the review export JSON as the canonical ground truth.\n")
        f.write("- Mapping is performed using `(query_id, font_name)` pairs.\n")
        f.write("- Only pairs present in the review export are included in the recomputed metrics.\n\n")
        
        f.write("## Updated Metrics Table\n\n")
        f.write("| Model | Agreement | Precision | Recall | F1 | TP | FP | FN | TN | Total |\n")
        f.write("|-------|-----------|-----------|--------|----|----|----|----|----|-------|\n")
        for name, data in final_metrics.items():
            m = data["metrics"]
            c = m["counts"]
            f.write(f"| {name} | {m['agreement']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {c['tp']} | {c['fp']} | {c['fn']} | {c['tn']} | {c['total']} |\n")
        
        f.write("\n## Artifact Paths\n")
        f.write("- Amended SSoT: `research/ab-eval/out/full_set_review_export_1770612809775.json`\n")
        f.write("- Qwen 235B Results: `research/ab-eval/out/full_set_no_bias_qwen235b_updated_ssot.json`\n")
        f.write("- VL-Plus Results: `research/ab-eval/out/full_set_no_bias_vl_plus_updated_ssot.json`\n")
        f.write("- Gemini 2.5 Results: `research/ab-eval/out/full_set_no_bias_gemini25_updated_ssot.json`\n")
        f.write("- Gemini 3 Results: `research/ab-eval/out/full_set_no_bias_gemini3flashpreview_updated_ssot.json`\n")

    print(f"\nReport generated at {report_path}")

if __name__ == "__main__":
    main()
