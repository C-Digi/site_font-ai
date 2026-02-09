import json
from pathlib import Path

def main():
    out_dir = Path("research/ab-eval/out")
    
    # Load New Results
    with open(out_dir / "g3_v3_gated_results.json", "r") as f:
        new_data = json.load(f)
        
    # Load Baseline Results (Gemini 3 Flash Preview Updated)
    with open(out_dir / "full_set_no_bias_gemini3flashpreview_updated_ssot.json", "r") as f:
        baseline_data = json.load(f)
        
    baseline_details = baseline_data["details"]
    new_details = new_data["details"]
    
    # Map by (query_id, font_name)
    baseline_map = {(r["query_id"], r["font_name"]): r for r in baseline_details}
    new_map = {(r["query_id"], r["font_name"]): r for r in new_details}
    
    impacts = []
    
    # Common pairs
    common_keys = set(baseline_map.keys()) & set(new_map.keys())
    
    for key in common_keys:
        b = baseline_map[key]
        n = new_map[key]
        
        h = n["human_match"]
        b_ai = b["ai_match"]
        n_ai = n["ai_match_gated"]
        
        impact = "neutral"
        if b_ai != h and n_ai == h:
            impact = "helped"
        elif b_ai == h and n_ai != h:
            impact = "hurt"
            
        impacts.append({
            "key": key,
            "query_id": n["query_id"],
            "font_name": n["font_name"],
            "impact": impact,
            "baseline_ai": b_ai,
            "new_ai": n_ai,
            "human": h,
            "evidence": n.get("evidence", "")
        })
        
    # Summary
    helped = [i for i in impacts if i["impact"] == "helped"]
    hurt = [i for i in impacts if i["impact"] == "hurt"]
    
    print(f"Total pairs: {len(impacts)}")
    print(f"Helped: {len(helped)}")
    print(f"Hurt: {len(hurt)}")
    print(f"Net Gain: {len(helped) - len(hurt)}")
    
    # Per Query Analysis
    query_impact = {}
    for i in impacts:
        qid = i["query_id"]
        if qid not in query_impact:
            query_impact[qid] = {"helped": 0, "hurt": 0, "neutral": 0}
        query_impact[qid][i["impact"]] += 1
        
    print("\nPer-Query Impact:")
    for qid, stats in sorted(query_impact.items()):
        net = stats["helped"] - stats["hurt"]
        if net != 0:
            print(f"  {qid}: {'+' if net > 0 else ''}{net} (Helped: {stats['helped']}, Hurt: {stats['hurt']})")

    # Write report artifact
    report_path = out_dir / "g3_v3_gated_impact_summary.md"
    with open(report_path, "w") as f:
        f.write("# Impact Summary: G3 V3 Gated Policy\n\n")
        f.write(f"- **Helped:** {len(helped)} pairs\n")
        f.write(f"- **Hurt:** {len(hurt)} pairs\n")
        f.write(f"- **Net Gain:** {len(helped) - len(hurt)} pairs\n\n")
        
        f.write("## Per-Query Impact\n")
        f.write("| Query ID | Helped | Hurt | Net |\n")
        f.write("|----------|--------|------|-----|\n")
        for qid, stats in sorted(query_impact.items()):
            net = stats["helped"] - stats["hurt"]
            f.write(f"| {qid} | {stats['helped']} | {stats['hurt']} | {'+' if net > 0 else ''}{net} |\n")
            
        f.write("\n## Notable Examples of Improvement\n")
        for i in helped[:10]:
            f.write(f"- **{i['font_name']}** for **{i['query_id']}**: Corrected from {i['baseline_ai']} to {i['human']}. Evidence: {i['evidence']}\n")

if __name__ == "__main__":
    main()
