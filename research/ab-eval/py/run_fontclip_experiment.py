import os
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
def load_env():
    root = Path(__file__).resolve().parents[3]
    load_dotenv(root / ".env", override=False)
    load_dotenv(root / ".env.local", override=False)

load_env()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def call_openrouter_proxy_batched(queries: List[str], description: str, model: str = "anthropic/claude-3-haiku") -> List[int]:
    """
    Simulates FontCLIP signal by judging match between Query and Typographic Description.
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    queries_formatted = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(queries)])
    
    prompt = f"""You are a FontCLIP-simulated typography expert. 
Your task is to judge if a font matches multiple queries based ONLY on a specialized typographic description.

Typographic Description:
{description}

Queries:
{queries_formatted}

For each query, determine if the description provides sufficient evidence that the font matches the user's intent (1 for match, 0 for no match).
Focus on micro-features (serifs, contrast, x-height, etc.) described.

Return STRICT JSON only (no markdown, no prose):
{{
  "matches": [
    {{"query_index": 1, "match": 1 or 0}},
    {{"query_index": 2, "match": 1 or 0}}
  ]
}}
"""
    
    payload = {
        "model": model,
        "temperature": 0.0,
        "messages": [
            {"role": "user", "content": prompt},
        ]
    }
    
    for attempt in range(5):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 429:
                time.sleep(15)
                continue
            if not resp.ok:
                print(f"Error {resp.status_code}: {resp.text}")
                time.sleep(5)
                continue
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
    else:
        return [0] * len(queries)
        
    content = ""
    try:
        data = resp.json()
        content = data['choices'][0]['message']['content']
        # Remove potential markdown block
        content = content.replace("```json", "").replace("```", "").strip()
        res = json.loads(content)
        matches = [0] * len(queries)
        for m in res.get("matches", []):
            idx = m["query_index"] - 1
            if 0 <= idx < len(queries):
                matches[idx] = m["match"]
        return matches
    except Exception as e:
        print(f"Parse error: {e}. Content snippet: {content[:100]}")
        return [0] * len(queries)

def calculate_metrics(results: List[Dict[str, Any]], match_key: str = "ai_match") -> Dict[str, Any]:
    tp = fp = fn = tn = 0
    for r in results:
        h = r["human_match"]
        a = r[match_key]
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--ssot", default="research/ab-eval/out/full_set_review_export_1770612809775.json")
    parser.add_argument("--baseline", default="research/ab-eval/out/full_set_no_bias_gemini3flashpreview_updated_ssot.json")
    parser.add_argument("--descriptions", default="research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl")
    parser.add_argument("--output", default="research/ab-eval/out/experiment_fontclip_results.json")
    args = parser.parse_args()

    # 1. Load SSoT
    print(f"Loading SSoT from {args.ssot}...")
    with open(args.ssot, 'r') as f:
        ssot_data = json.load(f)
    
    ssot_pairs = []
    for d in ssot_data["decisions"]:
        ssot_pairs.append({
            "query_id": d["query_id"],
            "font_name": d["font_name"],
            "human_match": d["casey_label"]
        })

    # 2. Load Baseline
    print(f"Loading Baseline from {args.baseline}...")
    with open(args.baseline, 'r') as f:
        baseline_data = json.load(f)
    baseline_map = {(r["query_id"], r["font_name"]): r["ai_match"] for r in baseline_data["details"]}

    # 3. Load Descriptions
    print(f"Loading Descriptions from {args.descriptions}...")
    font_descriptions = {}
    with open(args.descriptions, 'r') as f:
        for line in f:
            obj = json.loads(line)
            if obj["model"] == "qwen/qwen3-vl-235b-a22b-instruct":
                font_descriptions[obj["font_name"]] = obj["description"]

    # 4. Generate FontCLIP Proxy Judgments
    print("Generating FontCLIP Proxy Judgments...")
    # Map query_id to text
    query_text_map = {}
    for d in ssot_data["decisions"]:
        # We don't have query text in SSoT directly in all versions, 
        # but it's in the baseline or we can find it.
        pass
    
    # Try to get query text from baseline
    for r in baseline_data["details"]:
        query_text_map[r["query_id"]] = r["query_text"]

    # Group pairs by font_name to batch
    font_to_queries = {}
    for p in ssot_pairs:
        f_name = p["font_name"]
        if f_name not in font_to_queries: font_to_queries[f_name] = []
        font_to_queries[f_name].append(p["query_id"])

    fontclip_results_map = {}
    
    total_fonts = len(font_to_queries)
    for i, (f_name, q_ids) in enumerate(font_to_queries.items()):
        print(f"  [{i+1}/{total_fonts}] Processing {f_name} ({len(q_ids)} queries)...")
        desc = font_descriptions.get(f_name, "No description available.")
        q_texts = [query_text_map.get(qid, qid) for qid in q_ids]
        
        matches = call_openrouter_proxy_batched(q_texts, desc)
        for qid, m in zip(q_ids, matches):
            fontclip_results_map[(qid, f_name)] = m
        
        # Rate limiting safety
        time.sleep(0.5)

    # 5. Collate Results and Perform Fusion
    print("Collating results...")
    final_details = []
    for p in ssot_pairs:
        key = (p["query_id"], p["font_name"])
        baseline_vote = baseline_map.get(key, 0)
        fontclip_vote = fontclip_results_map.get(key, 0)
        
        # Fusion Arm: Consensus (AND)
        fusion_and = 1 if (baseline_vote == 1 and fontclip_vote == 1) else 0
        
        # Fusion Arm: Inclusive (OR)
        fusion_or = 1 if (baseline_vote == 1 or fontclip_vote == 1) else 0

        final_details.append({
            "query_id": p["query_id"],
            "query_text": query_text_map.get(p["query_id"], ""),
            "font_name": p["font_name"],
            "human_match": p["human_match"],
            "baseline_match": baseline_vote,
            "fontclip_match": fontclip_vote,
            "fusion_and": fusion_and,
            "fusion_or": fusion_or
        })

    # 6. Compute Metrics
    metrics = {
        "Baseline": calculate_metrics(final_details, "baseline_match"),
        "FontCLIP-Proxy": calculate_metrics(final_details, "fontclip_match"),
        "FontCLIP-Assisted (AND)": calculate_metrics(final_details, "fusion_and"),
        "FontCLIP-Assisted (OR)": calculate_metrics(final_details, "fusion_or")
    }

    # 7. Save and Report
    output_obj = {
        "metrics": metrics,
        "details": final_details
    }
    with open(args.output, 'w') as f:
        json.dump(output_obj, f, indent=2)

    print("\n" + "="*50)
    print("EXPERIMENT RESULTS")
    print("="*50)
    print("| Arm | Precision | Recall | F1 | Agreement |")
    print("|-----|-----------|--------|----|-----------|")
    for name, m in metrics.items():
        print(f"| {name} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {m['agreement']:.4f} |")
    
    print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()
