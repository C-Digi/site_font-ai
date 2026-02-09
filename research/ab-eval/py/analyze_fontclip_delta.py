import json
from collections import defaultdict

def main():
    with open("research/ab-eval/out/experiment_fontclip_results.json", "r") as f:
        data = json.load(f)
    
    details = data["details"]
    
    # 1. Per-query analysis
    query_stats = defaultdict(lambda: {"baseline_correct": 0, "and_correct": 0, "or_correct": 0, "total": 0, "proxy_correct": 0})
    
    for d in details:
        q_text = d["query_text"]
        h = 1 if d["human_match"] >= 1 else 0
        
        query_stats[q_text]["total"] += 1
        if d["baseline_match"] == h: query_stats[q_text]["baseline_correct"] += 1
        if d["fontclip_match"] == h: query_stats[q_text]["proxy_correct"] += 1
        if d["fusion_and"] == h: query_stats[q_text]["and_correct"] += 1
        if d["fusion_or"] == h: query_stats[q_text]["or_correct"] += 1

    print("=== PER-QUERY IMPACT (FontCLIP-Assisted AND vs Baseline) ===")
    print("| Query | Baseline Acc | AND Acc | Delta |")
    print("|-------|--------------|---------|-------|")
    
    deltas = []
    for q, s in query_stats.items():
        b_acc = s["baseline_correct"] / s["total"]
        a_acc = s["and_correct"] / s["total"]
        deltas.append((q, b_acc, a_acc, a_acc - b_acc))
    
    # Sort by delta
    deltas.sort(key=lambda x: x[3], reverse=True)
    
    for q, b, a, d in deltas:
        if d != 0:
            print(f"| {q[:50]}... | {b:.2f} | {a:.2f} | {d:+.2f} |")

    # 2. Specific examples of help/hurt
    print("\n=== TOP EXAMPLES WHERE FontCLIP HELPS (Reduces FPs) ===")
    helps = [d for d in details if d["baseline_match"] == 1 and d["human_match"] == 0 and d["fontclip_match"] == 0]
    for h in helps[:5]:
        print(f"- Query: \"{h['query_text']}\" | Font: {h['font_name']} | Baseline: FP | FontCLIP: Correct (Rejected)")

    print("\n=== TOP EXAMPLES WHERE FontCLIP HURTS (Causes FNs) ===")
    hurts = [d for d in details if d["baseline_match"] == 1 and d["human_match"] >= 1 and d["fontclip_match"] == 0]
    for h in hurts[:5]:
        print(f"- Query: \"{h['query_text']}\" | Font: {h['font_name']} | Baseline: TP | FontCLIP: Incorrect (Rejected)")

if __name__ == "__main__":
    main()
