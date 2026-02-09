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

def call_gpt52(query: str, font_name: str, image_path: Path) -> Dict[str, Any]:
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
Pay close attention to the "Legibility Pairs" and character forms.
Determine if this font is a good match for the query.

Return STRICT JSON only (no markdown blocks, no prose):
{{
  "thought": "your reasoning here, referencing visual details from the image",
  "match": 1 or 0
}}
"""
    
    data_url = image_to_data_url(image_path)
    payload = {
        "model": "openai/gpt-5.2",
        "temperature": 0.1,
        "include_reasoning": True, # High-reasoning mode
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
    resp = requests.post(url, headers=headers, json=payload, timeout=180)
    latency = time.time() - t0
    
    if not resp.ok:
        raise RuntimeError(f"OpenRouter HTTP {resp.status_code}: {resp.text}")
    
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
        # Fallback for malformed JSON
        return {
            "thought": f"Failed to parse JSON. Raw content: {content}",
            "match": 0,
            "latency_sec": round(latency, 2)
        }

def main():
    data_dir = Path("research/ab-eval/data")
    out_dir = Path("research/ab-eval/out")
    specimen_dir = out_dir / "specimens_v2_medium"
    
    queries_path = data_dir / "queries.complex.v1.json"
    labels_path = data_dir / "labels.medium.human.v1.json"
    candidates_path = data_dir / "candidate_pool.medium.v1.json"
    
    if not all(p.exists() for p in [queries_path, labels_path, candidates_path, specimen_dir]):
        print("Required files missing. Ensure paths are correct and specimens are rendered.")
        return
    
    with open(queries_path, "r") as f:
        queries = {q['id']: q for q in json.load(f)}
    with open(labels_path, "r") as f:
        human_labels = json.load(f)
    with open(candidates_path, "r") as f:
        candidate_pool = json.load(f)
        
    # Spot-check selection (5 queries)
    target_query_ids = ["cq_002", "cq_011", "cq_025", "cq_033", "cq_016"]
    
    results = []
    
    for qid in target_query_ids:
        query_text = queries[qid]['text']
        print(f"\n[QUERY] {qid}: {query_text}")
        
        # Take up to 3 candidates per query for a quick spot check (15 pairs total)
        candidates = candidate_pool.get(qid, [])[:3]
        labeled_positive = set(human_labels.get(qid, []))
        
        for font_name in candidates:
            safe_name = font_name.replace(" ", "_").replace("/", "_")
            image_path = specimen_dir / f"{safe_name}.png"
            
            if not image_path.exists():
                print(f"  [MISSING] {font_name}")
                continue
                
            print(f"  [JUDGING] {font_name}...", end="", flush=True)
            judgment = call_gpt52(query_text, font_name, image_path)
            
            ai_match = judgment.get("match", 0)
            human_match = 1 if font_name in labeled_positive else 0
            
            print(f" AI: {ai_match} | Human: {human_match} ({judgment.get('latency_sec')}s)")
            
            results.append({
                "query_id": qid,
                "query_text": query_text,
                "font_name": font_name,
                "ai_match": ai_match,
                "human_match": human_match,
                "thought": judgment.get("thought", ""),
                "latency_sec": judgment.get("latency_sec", 0)
            })
            
            # Rate limiting / politeness
            time.sleep(1)
            
    # Metrics
    total = len(results)
    if total == 0:
        print("No results generated.")
        return
        
    tp = sum(1 for r in results if r['ai_match'] == 1 and r['human_match'] == 1)
    fp = sum(1 for r in results if r['ai_match'] == 1 and r['human_match'] == 0)
    fn = sum(1 for r in results if r['ai_match'] == 0 and r['human_match'] == 1)
    tn = sum(1 for r in results if r['ai_match'] == 0 and r['human_match'] == 0)
    
    agreement_rate = (tp + tn) / total
    
    summary = {
        "metrics": {
            "total_pairs": total,
            "agreement_rate": round(agreement_rate, 4),
            "confusion": {
                "tp": tp, "fp": fp, "fn": fn, "tn": tn
            }
        },
        "details": results
    }
    
    out_file = out_dir / "spot_check_alignment.json"
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)
        
    print(f"\nFinal Agreement Rate: {agreement_rate:.2%}")
    print(f"Confusion: TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(f"Detailed artifact: {out_file}")

if __name__ == "__main__":
    main()
