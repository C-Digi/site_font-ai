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

def image_to_data_url(image_path: Path) -> str:
    if not image_path.exists():
        return ""
    b = image_path.read_bytes()
    b64 = base64.b64encode(b).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def call_openrouter_batched(queries: List[str], images: List[Path], prompt_type: str, model: str) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    queries_formatted = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(queries)])
    
    if prompt_type == "v2":
        prompt = f"""You are a typography expert judging font relevance to multiple queries.

Analyze the provided specimen image(s) for this font. 
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
    else: # v3
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
    
    content = [{"type": "text", "text": prompt}]
    for img_path in images:
        data_url = image_to_data_url(img_path)
        if data_url:
            content.append({"type": "image_url", "image_url": {"url": data_url}})
    
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": content}],
        "response_format": {"type": "json_object"}
    }
    
    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 429:
                time.sleep(10)
                continue
            if not resp.ok:
                time.sleep(5)
                continue
            break
        except Exception:
            time.sleep(5)
    else:
        return {"error": "Failed after 3 attempts"}
        
    try:
        res = resp.json()
        content_str = res['choices'][0]['message']['content']
        return json.loads(content_str)
    except Exception as e:
        return {"error": f"JSON parse error: {str(e)}", "raw": content_str if 'content_str' in locals() else ""}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", choices=["prompt_v3", "render_v3", "full_v3", "baseline_v2"], required=True)
    parser.add_argument("--model", default="google/gemini-2.0-flash-001")
    args = parser.parse_args()

    out_dir = Path("research/ab-eval/out")
    data_dir = Path("research/ab-eval/data")
    
    # 1. Load Ground Truth to get the pairs
    ssot_path = out_dir / "full_set_review_export_1770612809775.json"
    with open(ssot_path, 'r') as f:
        ssot = json.load(f)
    
    pairs = ssot['decisions']
    
    # Load Queries
    queries_path = data_dir / "queries.medium.human.v1.json"
    with open(queries_path, 'r') as f:
        queries_data = json.load(f)
    query_map = {q['id']: q['text'] for q in queries_data}

    # Group pairs by font
    font_to_queries = {}
    for p in pairs:
        fname = p['font_name']
        if fname not in font_to_queries:
            font_to_queries[fname] = []
        font_to_queries[fname].append(p)

    results = []
    
    # Setup paths
    spec_v2_dir = out_dir / "specimens_v2_medium_nobias" # Assuming this is where the baseline images are
    if not spec_v2_dir.exists():
        spec_v2_dir = out_dir / "specimens_v2"
        
    spec_v3_dir = out_dir / "specimens_v3"

    prompt_type = "v3" if "prompt" in args.exp or "full" in args.exp else "v2"
    render_v3 = "render" in args.exp or "full" in args.exp

    print(f"Running Experiment: {args.exp} | Prompt: {prompt_type} | Render V3: {render_v3}")
    
    processed_count = 0
    for fname, font_pairs in font_to_queries.items():
        safe_fname = fname.replace(" ", "_")
        
        if render_v3:
            images = [
                spec_v3_dir / f"{safe_fname}_top.png",
                spec_v3_dir / f"{safe_fname}_bottom.png"
            ]
        else:
            images = [spec_v2_dir / f"{fname}.png"] # Baseline uses .png with spaces often
            if not images[0].exists():
                images = [spec_v2_dir / f"{safe_fname}.png"]

        q_texts = [query_map[p['query_id']] for p in font_pairs]
        
        print(f"[{processed_count}/{len(font_to_queries)}] Processing {fname} ({len(q_texts)} queries)...")
        
        response = call_openrouter_batched(q_texts, images, prompt_type, args.model)
        
        if "error" in response:
            print(f"  Error: {response['error']}")
            continue

        # Map back to results
        if prompt_type == "v2":
            matches = response.get("matches", [])
            thought = response.get("thought", "")
            for i, p in enumerate(font_pairs):
                match_val = 0
                for m in matches:
                    if m.get("query_index") == i + 1:
                        match_val = m.get("match", 0)
                        break
                results.append({
                    "query_id": p['query_id'],
                    "font_name": fname,
                    "ai_match": match_val,
                    "thought": thought
                })
        else: # v3
            matches = response.get("results", [])
            reasoning = response.get("audit_reasoning", "")
            for i, p in enumerate(font_pairs):
                match_info = {}
                for m in matches:
                    if m.get("query_index") == i + 1:
                        match_info = m
                        break
                results.append({
                    "query_id": p['query_id'],
                    "font_name": fname,
                    "ai_match": match_info.get("match", 0),
                    "confidence": match_info.get("confidence", 0.5),
                    "evidence": match_info.get("evidence", ""),
                    "thought": reasoning + " | " + match_info.get("evidence", "")
                })
        
        processed_count += 1
        # To avoid rate limits on some models
        time.sleep(1)

    # Save results
    output_path = out_dir / f"intervention_{args.exp}_results.json"
    with open(output_path, 'w') as f:
        json.dump({"details": results}, f, indent=2)
    
    print(f"Saved results to {output_path}")

if __name__ == "__main__":
    main()
