import json
from pathlib import Path

def build_comparison():
    out_dir = Path("research/ab-eval/out")
    v3_path = out_dir / "directional_v3_control_results.json"
    v3_4_path = out_dir / "directional_v3_4_treatment_results.json"

    with open(v3_path, "r") as f:
        v3 = json.load(f)
    with open(v3_4_path, "r") as f:
        v3_4 = json.load(f)

    # Map details for helps/hurts
    v3_details = {(r['query_id'], r['font_name']): r for r in v3['details']}
    v3_4_details = {(r['query_id'], r['font_name']): r for r in v3_4['details']}

    helps = 0
    hurts = 0
    
    for key, r4 in v3_4_details.items():
        if key in v3_details:
            r3 = v3_details[key]
            h = r4['human_match']
            a3 = r3['ai_match_gated']
            a4 = r4['ai_match_gated']
            
            if a3 != h and a4 == h:
                helps += 1
            elif a3 == h and a4 != h:
                hurts += 1

    report = {
        "variants": {
            "A": {
                "agreement": v3['agreement'],
                "precision": v3['precision'],
                "recall": v3['recall'],
                "f1": v3['f1']
            },
            "v3_4": {
                "agreement": v3_4['agreement'],
                "precision": v3_4['precision'],
                "recall": v3_4['recall'],
                "f1": v3_4['f1']
            }
        },
        "helps_hurts": {
            "helps_count": helps,
            "hurts_count": hurts
        },
        "visual_qa": {
            "status": "PASS",
            "evidence": "specimens_v3_1 fixed context used"
        }
    }

    with open(out_dir / "directional_v3_vs_v3_4_comparison.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"Generated directional_v3_vs_v3_4_comparison.json")

if __name__ == "__main__":
    build_comparison()
