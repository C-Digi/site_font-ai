import os
import json
import base64
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import requests
from dotenv import load_dotenv

# Load environment variables
def load_env():
    root = Path(__file__).resolve().parents[3]
    load_dotenv(root / ".env", override=False)
    load_dotenv(root / ".env.local", override=False)

load_env()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "qwen/qwen3-vl-235b-a22b-instruct"

def image_to_data_url(image_path: Path) -> str:
    b = image_path.read_bytes()
    b64 = base64.b64encode(b).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def call_openrouter(query: str, font_name: str, image_path: Path) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    prompt = f"""You are a typography expert judging font relevance to a query.
Query: "{query}"
Font: "{font_name}"

Analyze the provided specimen image for this font. 
Pay close attention to the "Legibility Pairs" (il1I, O0, etc.) and character forms.
Determine if this font is a good match for the query.

Return STRICT JSON only (no markdown blocks, no prose):
{{
  "thought": "your reasoning here, referencing visual details from the image",
  "match": 1 or 0
}}
"""
    
    data_url = image_to_data_url(image_path)
    payload = {
        "model": MODEL,
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
    }
    
    t0 = time.time()
    # Adding retry logic
    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 429:
                print(f"  Rate limited. Sleeping 10s...")
                time.sleep(10)
                continue
            if not resp.ok:
                print(f"  OpenRouter Error {resp.status_code}: {resp.text}")
                time.sleep(5)
                continue
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    else:
        raise RuntimeError(f"Failed to call OpenRouter after 3 attempts")
        
    latency = time.time() - t0
    
    body = resp.json()
    choices = body.get('choices', [])
    if not choices:
        raise RuntimeError("OpenRouter returned no choices")
        
    content = choices[0].get('message', {}).get('content', '').strip()
    
    # Clean up JSON if necessary
    if content.startswith("```json"):
        content = content[7:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
        
    try:
        data = json.loads(content)
        data['latency_sec'] = round(latency, 2)
        return data
    except json.JSONDecodeError:
        return {
            "thought": f"Failed to parse JSON. Raw content: {content}",
            "match": 0,
            "latency_sec": round(latency, 2)
        }

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
    data_dir = Path("research/ab-eval/data")
    out_dir = Path("research/ab-eval/out")
    specimen_dir = out_dir / "specimens_v2_medium"
    
    # Load inputs
    with open(data_dir / "queries.medium.human.v1.json", "r") as f:
        queries = json.load(f)
    query_map = {q["id"]: q["text"] for q in queries}
    
    with open(data_dir / "candidate_pool.medium.v1.json", "r") as f:
        pool = json.load(f)
        
    with open(data_dir / "labels.medium.human.v1.json", "r") as f:
        labels_pos = json.load(f)

    cache_file = out_dir / "comprehensive_235b_results.json"
    results = []
    if cache_file.exists():
        with open(cache_file, "r") as f:
            results = json.load(f).get("details", [])
            print(f"Loaded {len(results)} existing results from cache.")

    completed_keys = set((r["query_id"], r["font_name"]) for r in results)
    
    todo = []
    for qid, fonts in pool.items():
        for font in fonts:
            if (qid, font) not in completed_keys:
                todo.append((qid, font))
    
    print(f"Total pairs to evaluate: {len(todo)}")
    
    try:
        for i, (qid, font) in enumerate(todo):
            print(f"[{i+1}/{len(todo)}] Evaluating {qid} | {font}")
            
            image_path = specimen_dir / f"{font.replace(' ', '_')}.png"
            if not image_path.exists():
                print(f"  WARNING: Specimen not found at {image_path}")
                continue
                
            query_text = query_map.get(qid, "Unknown query")
            
            # Call AI
            ai_resp = call_openrouter(query_text, font, image_path)
            
            # Get human label
            human_match = 1 if font in labels_pos.get(qid, []) else 0
            
            res = {
                "query_id": qid,
                "query_text": query_text,
                "font_name": font,
                "human_match": human_match,
                "ai_match": ai_resp.get("match", 0),
                "thought": ai_resp.get("thought", ""),
                "latency_sec": ai_resp.get("latency_sec", 0)
            }
            results.append(res)
            
            # Intermediate save
            if (i + 1) % 5 == 0:
                with open(cache_file, "w") as f:
                    json.dump({"details": results}, f, indent=2)
                    
    except KeyboardInterrupt:
        print("Interrupted. Saving progress...")
    finally:
        with open(cache_file, "w") as f:
            json.dump({"details": results}, f, indent=2)
            
    # Calculate and Print metrics
    metrics = calculate_metrics(results)
    print("\n" + "="*40)
    print("FINAL METRICS (Comprehensive 235B)")
    print("="*40)
    print(json.dumps(metrics, indent=2))
    
    # Per-query breakdown
    query_metrics = {}
    for r in results:
        qid = r["query_id"]
        if qid not in query_metrics: query_metrics[qid] = []
        query_metrics[qid].append(r)
        
    print("\nPer-Query Agreement:")
    disagreements = []
    for qid, q_results in query_metrics.items():
        m = calculate_metrics(q_results)
        agree = m["agreement"]
        print(f"  {qid}: {agree*100:.1f}% ({m['counts']['total']} pairs)")
        
        # Track disagreements
        for r in q_results:
            if r["human_match"] != r["ai_match"]:
                disagreements.append(r)
                
    # Summary report
    report = f"""# Comprehensive 235B Evaluation Report
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Run Configuration
- **Model:** `{MODEL}`
- **Source:** OpenRouter
- **Population:** `candidate_pool.medium.v1.json` (ALL pairs)
- **Ground Truth:** `labels.medium.human.v1.json` (Human labeling)

## Aggregate Metrics
- **Agreement:** {metrics['agreement']*100:.2f}%
- **Precision:** {metrics['precision']*100:.2f}%
- **Recall:** {metrics['recall']*100:.2f}%
- **F1 Score:** {metrics['f1']*100:.2f}%

### Confusion Matrix
| | AI Match=1 | AI Match=0 |
|---|---|---|
| **Human Match=1** | {metrics['counts']['tp']} (TP) | {metrics['counts']['fn']} (FN) |
| **Human Match=0** | {metrics['counts']['fp']} (FP) | {metrics['counts']['tn']} (TN) |
| **Total** | | {metrics['counts']['total']} |

## Notable Disagreement Patterns
Total disagreements: {len(disagreements)} out of {metrics['counts']['total']} pairs.

### Highest Disagreement Queries
"""
    # Find queries with most disagreements
    q_dis_counts = {}
    for d in disagreements:
        q_dis_counts[d['query_id']] = q_dis_counts.get(d['query_id'], 0) + 1
    
    sorted_q_dis = sorted(q_dis_counts.items(), key=lambda x: x[1], reverse=True)
    for qid, count in sorted_q_dis[:5]:
        report += f"- **{qid}**: {count} disagreements\n"
        
    with open("research/ab-eval/REPORT_COMPREHENSIVE_235B.md", "w") as f:
        f.write(report)
    print(f"\nReport written to research/ab-eval/REPORT_COMPREHENSIVE_235B.md")

if __name__ == "__main__":
    main()
