import json
import sys
from pathlib import Path
from datetime import datetime, timezone

def run_oem_gating():
    manifest_path = Path("research/ab-eval/out/week4_p2_labeling_manifest.json")
    labels_path = Path("research/ab-eval/data/labels.medium.human.v1.json")
    v3_results_path = Path("research/ab-eval/out/week4_p2_v3_results.json")
    v5_1_results_path = Path("research/ab-eval/out/week4_p2_v5_1_results.json")
    
    report_path = Path("research/ab-eval/REPORT_WEEK4_P2_OEM_GATING.md")
    comparison_path = Path("research/ab-eval/out/week4_p2_v3_vs_v5_1_comparison.json")
    gates_path = Path("research/ab-eval/out/week4_p2_v3_vs_v5_1_gates.json")
    blocker_path = Path("research/ab-eval/out/week4_p2_v3_vs_v5_1_blocker.json")

    # 1. Load data
    if not manifest_path.exists():
        print(f"Error: Manifest missing at {manifest_path}")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if not labels_path.exists():
        labels = {}
    else:
        with open(labels_path, "r", encoding="utf-8") as f:
            labels = json.load(f)

    # 2. Coverage Check
    missing_coverage = []
    pairs = manifest.get("pairs", [])
    
    # We define coverage as: the query exists in the labels file.
    # If the labels file uses a dictionary format (query -> font -> label), we check the font too.
    # If it's the list format (query -> [positive_fonts]), we assume presence of query means all fonts were reviewed.
    
    for pair in pairs:
        qid = pair["query_id"]
        fname = pair["font_name"]
        
        if qid not in labels:
            missing_coverage.append({
                "query_id": qid,
                "font_name": fname,
                "reason": "Query missing from labels file"
            })
        elif isinstance(labels[qid], dict):
            if fname not in labels[qid]:
                missing_coverage.append({
                    "query_id": qid,
                    "font_name": fname,
                    "reason": "Font missing from query labels dictionary"
                })

    if missing_coverage:
        # HANDLE BLOCKER
        blocker_data = {
            "status": "BLOCKED",
            "reason": "Incomplete human labels for OEM pairs",
            "missing_count": len(missing_coverage),
            "missing_examples": missing_coverage[:10],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(blocker_path, "w", encoding="utf-8") as f:
            json.dump(blocker_data, f, indent=2)
            
        report_content = f"""# REPORT: Week 4 Phase 2 OEM Gating

## Status: BLOCKED 🛑

**Reason:** Incomplete coverage of human labels for the requested 100 OEM pairs.

- **Total OEM Pairs:** {len(pairs)}
- **Missing Coverage:** {len(missing_coverage)} pairs
- **Blocker Artifact:** `{blocker_path.as_posix()}`

### Missing Queries
The following queries are missing from `labels.medium.human.v1.json`:
{", ".join(sorted(set(m["query_id"] for m in missing_coverage)))}

### Next Steps
1. Use the adjudication UI at `research/ab-eval/out/week4_p2_adjudication.html` to review these pairs.
2. Update `labels.medium.human.v1.json` with the adjudicated results.
3. Rerun this gating script.
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        print(f"Gating BLOCKED. See {report_path}")
        return

    # 3. Compute Metrics (Coverage is complete)
    # Load results
    with open(v3_results_path, "r", encoding="utf-8") as f:
        v3_data = json.load(f)
    with open(v5_1_results_path, "r", encoding="utf-8") as f:
        v5_1_data = json.load(f)

    # Map results by (query_id, font_name)
    def map_results(data):
        return {(d["query_id"], d["font_name"]): d for d in data.get("details", [])}

    v3_map = map_results(v3_data)
    v5_1_map = map_results(v5_1_data)

    def get_human_label(qid, fname):
        label_data = labels.get(qid)
        if isinstance(label_data, list):
            # List format: 1 if present, 0 otherwise
            return 1 if fname in label_data else 0
        elif isinstance(label_data, dict):
            # Dictionary format: use score directly, remap 2 -> 0
            score = label_data.get(fname, 0)
            return 0 if score == 2 else score
        return 0

    metrics = {
        "v3": {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "total": 0},
        "v5_1": {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "total": 0}
    }
    
    helps = 0
    hurts = 0
    
    comparison_details = []

    for pair in pairs:
        qid = pair["query_id"]
        fname = pair["font_name"]
        key = (qid, fname)
        
        human = get_human_label(qid, fname)
        v3_match = v3_map[key]["ai_match"] if key in v3_map else 0
        v5_1_match = v5_1_map[key]["ai_match"] if key in v5_1_map else 0
        
        # Update metrics
        for variant, ai_match, m in [("v3", v3_match, metrics["v3"]), ("v5_1", v5_1_match, metrics["v5_1"])]:
            m["total"] += 1
            if ai_match == 1 and human == 1: m["tp"] += 1
            elif ai_match == 1 and human == 0: m["fp"] += 1
            elif ai_match == 0 and human == 1: m["fn"] += 1
            elif ai_match == 0 and human == 0: m["tn"] += 1
            
        # Helps/Hurts
        v3_correct = (v3_match == human)
        v5_1_correct = (v5_1_match == human)
        
        if v5_1_correct and not v3_correct:
            helps += 1
        elif v3_correct and not v5_1_correct:
            hurts += 1
            
        comparison_details.append({
            "query_id": qid,
            "font_name": fname,
            "human": human,
            "v3": v3_match,
            "v5_1": v5_1_match,
            "status": "HELP" if (v5_1_correct and not v3_correct) else ("HURT" if (v3_correct and not v5_1_correct) else "SAME")
        })

    def calc_derived(m):
        agreement = (m["tp"] + m["tn"]) / m["total"] if m["total"] > 0 else 0
        precision = m["tp"] / (m["tp"] + m["fp"]) if (m["tp"] + m["fp"]) > 0 else 0
        recall = m["tp"] / (m["tp"] + m["fn"]) if (m["tp"] + m["fn"]) > 0 else 0
        return {"agreement": agreement, "precision": precision, "recall": recall}

    v3_derived = calc_derived(metrics["v3"])
    v5_1_derived = calc_derived(metrics["v5_1"])

    comparison_data = {
        "metadata": {
            "run_id": "week4_p2_oem_gating",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "variants": {
            "v3": {**metrics["v3"], **v3_derived},
            "v5_1": {**metrics["v5_1"], **v5_1_derived}
        },
        "helps_hurts": {
            "helps_count": helps,
            "hurts_count": hurts,
            "net": helps - hurts
        },
        "details": comparison_details
    }

    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=2)

    # Gates
    ag_delta = v5_1_derived["agreement"] - v3_derived["agreement"]
    pr_delta = v5_1_derived["precision"] - v3_derived["precision"]
    
    gates = {
        "G1 (Agreement Delta)": {"status": "PASS" if ag_delta >= 0.01 else "FAIL", "value": ag_delta, "threshold": ">= 0.01"},
        "G2 (Precision Delta)": {"status": "PASS" if pr_delta >= -0.02 else "FAIL", "value": pr_delta, "threshold": ">= -0.02"},
        "G3 (Helps/Hurts Net)": {"status": "PASS" if (helps - hurts) > 0 else "FAIL", "value": helps - hurts, "threshold": "> 0"}
    }
    
    all_pass = all(g["status"] == "PASS" for g in gates.values())
    
    gates_output = {
        "summary": "GO" if all_pass else "NO-GO",
        "gates": gates
    }
    
    with open(gates_path, "w", encoding="utf-8") as f:
        json.dump(gates_output, f, indent=2)

    report_content = f"""# REPORT: Week 4 Phase 2 OEM Gating

## Status: {"GO ✅" if all_pass else "NO-GO ❌"}

### Summary Metrics (OEM 100 set)

| Metric | Variant V3 (Baseline) | Variant V5.1 (Treatment) | Delta |
| :--- | :--- | :--- | :--- |
| **Agreement** | {v3_derived['agreement']:.1%} | {v5_1_derived['agreement']:.1%} | {ag_delta:+.1%} |
| **Precision** | {v3_derived['precision']:.1%} | {v5_1_derived['precision']:.1%} | {pr_delta:+.1%} |
| **Recall** | {v3_derived['recall']:.1%} | {v5_1_derived['recall']:.1%} | {v5_1_derived['recall'] - v3_derived['recall']:+.1%} |

### Gate Results

| Gate | Metric | Value | Threshold | Status |
| :--- | :--- | :--- | :--- | :--- |
| **G1** | Agreement Delta | {ag_delta:+.1%} | >= +1.0% | {gates['G1 (Agreement Delta)']['status']} |
| **G2** | Precision Delta | {pr_delta:+.1%} | >= -2.0% | {gates['G2 (Precision Delta)']['status']} |
| **G3** | Helps/Hurts Net | {helps - hurts:+} | > 0 | {gates['G3 (Helps/Hurts Net)']['status']} |

### Helps/Hurts Analysis
- **Helps:** {helps}
- **Hurts:** {hurts}
- **Net:** {helps - hurts:+}

---
*Generated by `run_oem_gating.py`*
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Gating completed. Status: {gates_output['summary']}. See {report_path}")

if __name__ == "__main__":
    run_oem_gating()
