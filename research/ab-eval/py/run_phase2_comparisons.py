import os
import json
import base64
import time
import argparse
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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def image_to_base64(image_path: Path) -> str:
    if not image_path.exists():
        return ""
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")

def call_gemini_v3(queries: List[str], images: List[Path], model: str) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json",
    }
    
    queries_formatted = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(queries)])
    
    prompt = f"""You are a master typography auditor. Your task is to perform a rigorous evaluation of a font's relevance to specific user queries.

### DECISION RUBRIC
For a query to be a MATCH (1), the font must satisfy ALL primary technical constraints (e.g., if it says "geometric", it must have geometric forms) and the core "vibe" or "intent" described.
Partial matches or "almost matches" should be scored as NO MATCH (0) unless the query is broad.

### EVIDENCE REQUIREMENT
For EACH query, you must provide a short specific visual evidence snippet from the specimen.

### QUERIES
{queries_formatted}

### RESPONSE FORMAT
Return STRICT JSON only:
{{
  "audit_reasoning": "Overall evaluation of font family characteristics",
  "results": [
    {{
      "query_index": 1,
      "match": 1 or 0,
      "confidence": 0.0-1.0,
      "evidence": "Specific visual detail justifying this score",
      "counter_evidence": "Any visual detail that almost disqualified it (or empty)"
    }},
    ...
  ]
}}
"""
    
    parts = [{"text": prompt}]
    for img_path in images:
        b64 = image_to_base64(img_path)
        if b64:
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": b64
                }
            })
    
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.1,
            "response_mime_type": "application/json"
        }
    }
    
    for attempt in range(5):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 429:
                time.sleep(15)
                continue
            if resp.status_code == 503:
                time.sleep(20)
                continue
            if not resp.ok:
                time.sleep(10)
                continue
            
            res = resp.json()
            content_str = res['candidates'][0]['content']['parts'][0]['text'].strip()
            # Clean markdown if present
            if content_str.startswith("```json"): content_str = content_str[7:-3].strip()
            elif content_str.startswith("```"): content_str = content_str[3:-3].strip()
            
            return json.loads(content_str)
        except Exception as e:
            if attempt == 4: return {"error": f"Failed: {str(e)}"}
            time.sleep(10)
    return {"error": "Failed after 5 attempts"}

def call_openrouter_v3(queries: List[str], images: List[Path], model: str) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    queries_formatted = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(queries)])
    
    prompt = f"""You are a master typography auditor. Your task is to perform a rigorous evaluation of a font's relevance to specific user queries.

### DECISION RUBRIC
For a query to be a MATCH (1), the font must satisfy ALL primary technical constraints (e.g., if it says "geometric", it must have geometric forms) and the core "vibe" or "intent" described.
Partial matches or "almost matches" should be scored as NO MATCH (0) unless the query is broad.

### EVIDENCE REQUIREMENT
For EACH query, you must provide a short specific visual evidence snippet from the specimen.

### QUERIES
{queries_formatted}

### RESPONSE FORMAT
Return STRICT JSON only (no prose, no markdown blocks):
{{
  "audit_reasoning": "Overall evaluation of font family characteristics",
  "results": [
    {{
      "query_index": 1,
      "match": 1 or 0,
      "confidence": 0.0-1.0,
      "evidence": "Specific visual detail justifying this score",
      "counter_evidence": "Any visual detail that almost disqualified it (or empty)"
    }},
    ...
  ]
}}
"""
    
    content = [{"type": "text", "text": prompt}]
    for img_path in images:
        b64 = image_to_base64(img_path)
        if b64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64}"
                }
            })
    
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": content}],
        "response_format": {"type": "json_object"}
    }
    
    for attempt in range(5):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=240)
            if resp.status_code == 429:
                time.sleep(20)
                continue
            if not resp.ok:
                time.sleep(10)
                continue
            
            res = resp.json()
            content_str = res['choices'][0]['message']['content'].strip()
            # Clean markdown if present
            if content_str.startswith("```json"): content_str = content_str[7:-3].strip()
            elif content_str.startswith("```"): content_str = content_str[3:-3].strip()
            
            return json.loads(content_str)
        except Exception as e:
            if attempt == 4: return {"error": f"Failed: {str(e)}"}
            time.sleep(10)
    return {"error": "Failed after 5 attempts"}

def calculate_metrics(results: List[Dict[str, Any]], ssot_map: Dict[Tuple[str, str], int], confidence_gate: float = 0.9) -> Dict[str, Any]:
    tp = fp = fn = tn = 0
    gated_results = []
    
    for r in results:
        key = (r["query_id"], r["font_name"])
        if key not in ssot_map:
            continue
            
        h = ssot_map[key]
        raw_match = r.get("ai_match", 0)
        confidence = r.get("confidence", 1.0)
        ai_match = 1 if (raw_match == 1 and confidence >= confidence_gate) else 0
        
        if h == 1 and ai_match == 1: tp += 1
        elif h == 0 and ai_match == 1: fp += 1
        elif h == 1 and ai_match == 0: fn += 1
        elif h == 0 and ai_match == 0: tn += 1
        
        gated_results.append({**r, "ai_match_gated": ai_match, "human_match": h})
        
    total = len(gated_results)
    agreement = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "agreement": round(agreement, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "counts": {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "total": total},
        "details": gated_results
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--provider", choices=["gemini", "openrouter"], default="openrouter")
    parser.add_argument("--gate", type=float, default=0.9)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    out_dir = Path("research/ab-eval/out")
    data_dir = Path("research/ab-eval/data")
    spec_v3_dir = out_dir / "specimens_v3"
    
    # 1. Load SSoT
    ssot_path = out_dir / "full_set_review_export_1770612809775.json"
    with open(ssot_path, 'r') as f:
        ssot_data = json.load(f)
    
    ssot_map = {}
    font_to_queries = {}
    for d in ssot_data['decisions']:
        ssot_map[(d['query_id'], d['font_name'])] = d['casey_label']
        fname = d['font_name']
        if fname not in font_to_queries:
            font_to_queries[fname] = []
        font_to_queries[fname].append(d)

    # 2. Load Query Texts
    queries_path = data_dir / "queries.medium.human.v1.json"
    with open(queries_path, 'r') as f:
        queries_json = json.load(f)
    query_text_map = {q['id']: q['text'] for q in queries_json}

    results = []
    cache_path = out_dir / args.output
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            results = json.load(f)
        processed_keys = set((r['query_id'], r['font_name']) for r in results)
        print(f"Loaded {len(results)} existing results.")
    else:
        processed_keys = set()

    font_names = sorted(list(font_to_queries.keys()))
    
    print(f"Model={args.model} | Provider={args.provider} | Gate={args.gate}")
    
    try:
        for fname in font_names:
            font_pairs = font_to_queries[fname]
            # Filter pairs already in results
            font_pairs = [p for p in font_pairs if (p['query_id'], fname) not in processed_keys]
            if not font_pairs: continue
            
            safe_fname = fname.replace(" ", "_")
            images = [
                spec_v3_dir / f"{safe_fname}_top.png",
                spec_v3_dir / f"{safe_fname}_bottom.png"
            ]
            
            if not images[0].exists() or not images[1].exists():
                print(f"  WARNING: Missing specimens for {fname}")
                continue

            q_ids = [p['query_id'] for p in font_pairs]
            q_texts = [query_text_map[qid] for qid in q_ids]
            
            print(f"Evaluating {fname} ({len(q_texts)} pairs)...", end="", flush=True)
            
            # Batch call (max 10)
            for i in range(0, len(q_texts), 10):
                batch_texts = q_texts[i:i+10]
                batch_ids = q_ids[i:i+10]
                
                if args.provider == "gemini":
                    resp = call_gemini_v3(batch_texts, images, args.model)
                else:
                    resp = call_openrouter_v3(batch_texts, images, args.model)
                
                if "error" in resp:
                    print(f" ERROR: {resp['error']}")
                    continue
                
                matches = resp.get("results", [])
                reasoning = resp.get("audit_reasoning", "")
                
                for idx, qid in enumerate(batch_ids):
                    match_info = {}
                    for m in matches:
                        if m.get("query_index") == idx + 1:
                            match_info = m
                            break
                    
                    results.append({
                        "query_id": qid,
                        "font_name": fname,
                        "ai_match": match_info.get("match", 0),
                        "confidence": match_info.get("confidence", 0.5),
                        "evidence": match_info.get("evidence", ""),
                        "thought": reasoning + " | " + match_info.get("evidence", "")
                    })
            
            print(" Done")
            with open(cache_path, 'w') as f:
                json.dump(results, f, indent=2)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopped.")

    metrics = calculate_metrics(results, ssot_map, args.gate)
    final_results_path = out_dir / f"metrics_{args.output}"
    with open(final_results_path, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print("\nMETRICS:")
    print(f"Agreement: {metrics['agreement']}")
    print(f"F1: {metrics['f1']}")

if __name__ == "__main__":
    main()
