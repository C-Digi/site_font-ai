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

def image_to_data_url(image_path: Path) -> str:
    b = image_path.read_bytes()
    b64 = base64.b64encode(b).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def call_openrouter_batched(model: str, queries: List[str], font_name: str, image_path: Path) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    queries_formatted = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(queries)])
    
    prompt = f"""You are a typography expert judging font relevance to multiple queries.
Font: "{font_name}"

Analyze the provided specimen image for this font. 
Pay close attention to the "Legibility Pairs" (il1I, O0, etc.) and character forms.
Determine if this font is a good match for EACH of the following queries.

Queries:
{queries_formatted}

Return STRICT JSON only (no markdown blocks, no prose):
{{
  "thought": "your overall reasoning here, referencing visual details from the image",
  "matches": [
    {{"query_index": 1, "match": 1 or 0}},
    {{"query_index": 2, "match": 1 or 0}},
    ...
  ]
}}
"""
    
    data_url = image_to_data_url(image_path)
    payload = {
        "model": model,
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
    # Retry logic
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
            print(f"  Connection error: {e}")
            time.sleep(5)
    else:
        raise RuntimeError(f"OpenRouter failed after 3 attempts")

    latency = time.time() - t0
    
    body = resp.json()
    choices = body.get('choices', [])
    if not choices:
        raise RuntimeError("OpenRouter returned no choices")
        
    content = choices[0].get('message', {}).get('content', '').strip()
    
    # Clean up JSON
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
            "matches": [{"query_index": i+1, "match": 0} for i in range(len(queries))],
            "latency_sec": round(latency, 2)
        }

def run_evaluation(model_id: str):
    print(f"\n=== Starting Evaluation for {model_id} ===")
    data_dir = Path("research/ab-eval/data")
    out_dir = Path("research/ab-eval/out")
    specimen_dir = out_dir / "specimens_v2_medium"
    
    queries_path = data_dir / "queries.complex.v1.json"
    labels_path = data_dir / "labels.medium.human.v1.json"
    candidates_path = data_dir / "candidate_pool.medium.v1.json"
    
    if not all(p.exists() for p in [queries_path, labels_path, candidates_path, specimen_dir]):
        print("Required files missing.")
        return None
    
    with open(queries_path, "r") as f:
        queries_all = {q['id']: q for q in json.load(f)}
    with open(labels_path, "r") as f:
        human_labels = json.load(f)
    with open(candidates_path, "r") as f:
        candidate_pool = json.load(f)
        
    target_query_ids = ["cq_002", "cq_011", "cq_025", "cq_033", "cq_016"]
    
    # Group pairs by font
    font_to_queries = {}
    for qid in target_query_ids:
        candidates = candidate_pool.get(qid, [])[:3]
        for font_name in candidates:
            if font_name not in font_to_queries:
                font_to_queries[font_name] = []
            font_to_queries[font_name].append(qid)
            
    results = []
    
    for font_name, qids in font_to_queries.items():
        safe_name = font_name.replace(" ", "_").replace("/", "_")
        image_path = specimen_dir / f"{safe_name}.png"
        
        if not image_path.exists():
            print(f"  [MISSING] {font_name}")
            continue
            
        print(f"  [JUDGING BATCH] {font_name} ({len(qids)} queries)...", end="", flush=True)
        
        # Split into batches of 10
        for i in range(0, len(qids), 10):
            batch_qids = qids[i:i+10]
            batch_query_texts = [queries_all[qid]['text'] for qid in batch_qids]
            
            try:
                judgment = call_openrouter_batched(model_id, batch_query_texts, font_name, image_path)
            except Exception as e:
                print(f" Error: {e}")
                judgment = {"thought": f"Error: {e}", "matches": [], "latency_sec": 0}
            
            matches_map = {m['query_index']: m['match'] for m in judgment.get('matches', [])}
            
            for idx, qid in enumerate(batch_qids):
                ai_match = matches_map.get(idx + 1, 0)
                human_match = 1 if font_name in human_labels.get(qid, []) else 0
                
                results.append({
                    "query_id": qid,
                    "query_text": queries_all[qid]['text'],
                    "font_name": font_name,
                    "ai_match": ai_match,
                    "human_match": human_match,
                    "thought": judgment.get("thought", ""),
                    "latency_sec": judgment.get("latency_sec", 0)
                })
        
        print(f" Done ({judgment.get('latency_sec')}s)")
        time.sleep(1) # OpenRouter politeness
            
    total = len(results)
    if total == 0:
        return None
        
    tp = sum(1 for r in results if r['ai_match'] == 1 and r['human_match'] == 1)
    fp = sum(1 for r in results if r['ai_match'] == 1 and r['human_match'] == 0)
    fn = sum(1 for r in results if r['ai_match'] == 0 and r['human_match'] == 1)
    tn = sum(1 for r in results if r['ai_match'] == 0 and r['human_match'] == 0)
    
    agreement_rate = (tp + tn) / total if total > 0 else 0
    
    summary = {
        "model_id": model_id,
        "metrics": {
            "total_pairs": total,
            "agreement_rate": round(agreement_rate, 4),
            "confusion": {
                "tp": tp, "fp": fp, "fn": fn, "tn": tn
            }
        },
        "details": results
    }
    return summary

def main():
    out_dir = Path("research/ab-eval/out")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Model 1: Qwen 235B
    model_235b = "qwen/qwen3-vl-235b-a22b-instruct"
    res_235b = run_evaluation(model_235b)
    if res_235b:
        with open(out_dir / "spot_check_alignment_qwen3vl_235b.json", "w") as f:
            json.dump(res_235b, f, indent=2)
            
    # Model 2: Qwen VL Plus
    model_vl_plus = "qwen/qwen-vl-plus"
    res_vl_plus = run_evaluation(model_vl_plus)
    if res_vl_plus:
        with open(out_dir / "spot_check_alignment_vl_plus.json", "w") as f:
            json.dump(res_vl_plus, f, indent=2)

if __name__ == "__main__":
    main()
