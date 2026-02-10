import json
from pathlib import Path

def analyze_mismatches(results_path, ssot_path):
    with open(results_path, 'r') as f:
        results = json.load(f)
    with open(ssot_path, 'r') as f:
        ssot_data = json.load(f)
    
    ssot_map = {(d['query_id'], d['font_name']): d['casey_label'] for d in ssot_data['decisions']}
    
    fn_count = 0
    print(f"Analyzing False Negatives for {results_path}...")
    for r in results:
        key = (r["query_id"], r["font_name"])
        if key in ssot_map:
            h = ssot_map[key]
            a = r["ai_match"]
            if h == 1 and a == 0:
                fn_count += 1
                if fn_count <= 5:
                    print(f"FN {fn_count}: Query {r['query_id']} | Font {r['font_name']}")
                    print(f"  Thought: {r['thought']}")
                    print("-" * 20)
    print(f"Total FNs: {fn_count}")

if __name__ == "__main__":
    analyze_mismatches("research/ab-eval/out/gpt52_v3_gated_raw.json", "research/ab-eval/out/full_set_review_export_1770612809775.json")
    print("\n" + "="*40 + "\n")
    analyze_mismatches("research/ab-eval/out/g3_pro_v3_gated_raw.json", "research/ab-eval/out/full_set_review_export_1770612809775.json")
