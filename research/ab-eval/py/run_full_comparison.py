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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def image_to_data_url(image_path: Path) -> str:
    b = image_path.read_bytes()
    b64 = base64.b64encode(b).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def call_openrouter_batched(queries: List[str], image_path: Path, model: str) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    queries_formatted = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(queries)])
    
    # FONT NAME REMOVED FROM PROMPT TO PREVENT BIAS
    prompt = f"""You are a typography expert judging font relevance to multiple queries.

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
            "matches": [{"query_index": i+1, "match": 0} for i in range(len(queries))],
            "latency_sec": round(latency, 2)
        }

def call_gemini_batched(queries: List[str], image_path: Path, model: str) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json",
    }
    
    queries_formatted = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(queries)])
    
    prompt = f"""You are a typography expert judging font relevance to multiple queries.

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
    
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": img_data
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "response_mime_type": "application/json"
        }
    }
    
    t0 = time.time()
    for attempt in range(5):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 429:
                print(f"  Rate limited. Sleeping 15s...")
                time.sleep(15)
                continue
            if resp.status_code == 503:
                print(f"  Model overloaded. Sleeping 20s...")
                time.sleep(20)
                continue
            if not resp.ok:
                print(f"  Gemini Error {resp.status_code}: {resp.text}")
                time.sleep(10)
                continue
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(10)
    else:
        raise RuntimeError(f"Failed to call Gemini after 5 attempts")
        
    latency = time.time() - t0
    
    body = resp.json()
    try:
        content = body['candidates'][0]['content']['parts'][0]['text'].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"Gemini returned unexpected format: {body}")
    
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
            "matches": [{"query_index": i+1, "match": 0} for i in range(len(queries))],
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Model name (OpenRouter slug)")
    parser.add_argument("--output", required=True, help="Output JSON filename")
    args = parser.parse_args()

    data_dir = Path("research/ab-eval/data")
    out_dir = Path("research/ab-eval/out")
    specimen_dir = out_dir / "specimens_v2_medium_nobias"
    
    # Load inputs
    with open(data_dir / "queries.medium.human.v1.json", "r") as f:
        queries = json.load(f)
    query_map = {q["id"]: q["text"] for q in queries}
    
    with open(data_dir / "candidate_pool.medium.v1.json", "r") as f:
        pool = json.load(f)
        
    with open(data_dir / "labels.medium.human.v1.json", "r") as f:
        labels_pos = json.load(f)

    cache_file = out_dir / args.output
    results = []
    if cache_file.exists():
        with open(cache_file, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "details" in data:
                results = data["details"]
            elif isinstance(data, list):
                results = data
            print(f"Loaded {len(results)} existing results from cache.")

    completed_keys = set((r["query_id"], r["font_name"]) for r in results)
    
    # Group todo by font
    font_to_queries = {}
    for qid, fonts in pool.items():
        for font in fonts:
            if (qid, font) not in completed_keys:
                if font not in font_to_queries:
                    font_to_queries[font] = []
                font_to_queries[font].append(qid)
    
    total_pairs = sum(len(qids) for qids in font_to_queries.values())
    print(f"Total pairs to evaluate for {args.model}: {total_pairs} across {len(font_to_queries)} fonts")
    
    processed_count = 0
    try:
        for font_name, qids in font_to_queries.items():
            image_path = specimen_dir / f"{font_name.replace(' ', '_')}.png"
            if not image_path.exists():
                print(f"  WARNING: Specimen not found at {image_path}")
                processed_count += len(qids)
                continue
                
            print(f"Evaluating {font_name} ({len(qids)} queries)...", end="", flush=True)
            
            # Split into batches of 10
            last_latency = 0
            for i in range(0, len(qids), 10):
                batch_qids = qids[i:i+10]
                batch_query_texts = [query_map.get(qid, "Unknown query") for qid in batch_qids]
                
                if "gemini" in args.model.lower() and not ("openrouter" in args.model.lower() or "google/" in args.model.lower()):
                    ai_resp = call_gemini_batched(batch_query_texts, image_path, args.model)
                else:
                    ai_resp = call_openrouter_batched(batch_query_texts, image_path, args.model)

                matches_map = {m['query_index']: m['match'] for m in ai_resp.get('matches', [])}
                last_latency = ai_resp.get('latency_sec', 0)
                
                for idx, qid in enumerate(batch_qids):
                    human_match = 1 if font_name in labels_pos.get(qid, []) else 0
                    ai_match = matches_map.get(idx + 1, 0)
                    
                    res = {
                        "query_id": qid,
                        "query_text": query_map.get(qid, "Unknown query"),
                        "font_name": font_name,
                        "human_match": human_match,
                        "ai_match": ai_match,
                        "thought": ai_resp.get("thought", ""),
                        "latency_sec": last_latency
                    }
                    results.append(res)
                
                processed_count += len(batch_qids)
            
            print(f" Done ({last_latency}s)")
            
            # Intermediate save
            with open(cache_file, "w") as f:
                json.dump({"details": results}, f, indent=2)
            
            time.sleep(2) # politeness
                    
    except KeyboardInterrupt:
        print("Interrupted. Saving progress...")
    finally:
        with open(cache_file, "w") as f:
            json.dump({"details": results}, f, indent=2)
            
    # Calculate and Print metrics
    metrics = calculate_metrics(results)
    print("\n" + "="*40)
    print(f"FINAL METRICS ({args.model})")
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
                
    # Summary report (Markdown)
    report_path = out_dir / args.output.replace(".json", ".md")
    source = "Gemini API" if "gemini" in args.model.lower() and "google/" not in args.model.lower() else "OpenRouter"
    report = f"""# Evaluation Report: {args.model}
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Run Configuration
- **Model:** `{args.model}`
- **Source:** {source}
- **Bias Prevention:** Font name removed from prompt and specimen image.
- **Population:** `candidate_pool.medium.v1.json` (Full set)
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
"""
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport written to {report_path}")

if __name__ == "__main__":
    main()
