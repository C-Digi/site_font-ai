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
    elif prompt_type == "v3_2":
        prompt = f"""You are a master typography auditor (V3.2 - Calibration Guardrails). Your task is to perform a rigorous evaluation of a font's relevance to specific user queries.

### DECISION RUBRIC
For a query to be a MATCH (1), the font must satisfy ALL primary technical constraints and the core vibe/intent described.
Partial matches or "almost matches" should be scored as NO MATCH (0) unless the query is broad.

### SPECIMEN INTERPRETATION GUARDRAILS
1. **Diagnostic Neutrality (Critical Distinction block)**
   - The Critical Distinction block appears on ALL specimens and is diagnostic-only.
   - Do NOT treat this block as category proof (e.g., monospace/coding) by itself.
   - For technical classification, verify evidence in body text/alphabet first (e.g., width consistency across letters, overall construction patterns).
2. **Geometric Inclusivity**
   - Geometric classification can still be valid when core geometric evidence is strong (e.g., round/simple construction in key glyphs like o/p/b), even if minor humanist traits are present.
   - Minor humanist cues alone must NOT override strong core geometric evidence.
3. **Luxury Anchor (Stricter High-End Requirement)**
   - Assign luxury/high-end serif only with stronger high-end signals (e.g., pronounced contrast and distinctive refined flourishes such as swash Q, teardrop terminals, couture-like detailing).
   - Do NOT elevate standard editorial/book serifs to luxury without those stronger signals.

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
    elif prompt_type == "v3_3":
        prompt = f"""You are a master typography auditor (V3.3 - Calibration + Vibe Over-extension Guardrails). Your task is to perform a rigorous evaluation of a font's relevance to specific user queries.

### DECISION RUBRIC
For a query to be a MATCH (1), the font must satisfy ALL primary technical constraints and the core vibe/intent described.
Partial matches or "almost matches" should be scored as NO MATCH (0) unless the query is broad.

### SPECIMEN INTERPRETATION GUARDRAILS
1. **Diagnostic Neutrality (Critical Distinction block)**
   - The Critical Distinction block appears on ALL specimens and is diagnostic-only.
   - Do NOT treat this block as category proof (e.g., monospace/coding) by itself.
   - For technical classification, verify evidence in body text/alphabet first (e.g., width consistency across letters, overall construction patterns).
2. **Geometric Inclusivity**
   - Geometric classification can still be valid when core geometric evidence is strong (e.g., round/simple construction in key glyphs like o/p/b), even if minor humanist traits are present.
   - Minor humanist cues alone must NOT override strong core geometric evidence.
3. **Luxury Anchor (Stricter High-End Requirement)**
   - Assign luxury/high-end serif only with stronger high-end signals (e.g., pronounced contrast and distinctive refined flourishes such as swash Q, teardrop terminals, couture-like detailing).
   - Do NOT elevate standard editorial/book serifs to luxury without those stronger signals.
4. **Vibe Over-extension (Display/Mood queries)**
   - For playful/whimsical/quirky/themed mood queries, require explicit structural novelty (e.g., irregular baseline, varying rhythm/width behavior, novelty stroke endings, asymmetrical construction).
   - Do NOT classify as playful based only on minor flourish details if the underlying architecture is formal/traditional.

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
    elif prompt_type == "v3_4":
        prompt = f"""You are a master typography auditor (V3.4 - Category/Architecture Consistency). Your task is to perform a rigorous evaluation of a font's relevance to specific user queries.

### DECISION RUBRIC
For a query to be a MATCH (1), the font must satisfy ALL primary technical constraints and the core vibe/intent described.
Partial matches or "almost matches" should be scored as NO MATCH (0) unless the query is broad.

### SPECIMEN INTERPRETATION GUARDRAILS
1. **Diagnostic Neutrality (Critical Distinction block)**
   - The Critical Distinction block appears on ALL specimens and is diagnostic-only.
   - Do NOT treat this block as category proof (e.g., monospace/coding) by itself.
   - For technical classification, verify evidence in body text/alphabet first (e.g., width consistency across letters, overall construction patterns).
2. **Geometric Inclusivity**
   - Geometric classification can still be valid when core geometric evidence is strong (e.g., round/simple construction in key glyphs like o/p/b), even if minor humanist traits are present.
   - Minor humanist cues alone must NOT override strong core geometric evidence.
3. **Luxury Anchor (Stricter High-End Requirement)**
   - Assign luxury/high-end serif only with stronger high-end signals (e.g., pronounced contrast and distinctive refined flourishes such as swash Q, teardrop terminals, couture-like detailing).
   - Do NOT elevate standard editorial/book serifs to luxury without those stronger signals.
4. **Vibe Over-extension (Display/Mood queries)**
   - For playful/whimsical/quirky/themed mood queries, require explicit structural novelty (e.g., irregular baseline, varying rhythm/width behavior, novelty stroke endings, asymmetrical construction).
   - Do NOT classify as playful based only on minor flourish details if the underlying architecture is formal/traditional.
5. **Category/Architecture Consistency (Structural Guardrail)**
   - Mood or style cues MUST NOT override explicit or implicit architectural category constraints (e.g., a formal serif cannot match a 'handwritten' query just because it feels 'personal').
   - Architectural category (sans, serif, slab, script, mono) is the primary filter; mood is the secondary filter.
   - Only override this if the user intent clearly prioritizes a 'look' that transcends category (e.g., 'something that looks like a chalkboard' might allow a non-script if it has chalky texture).

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
    elif prompt_type == "v4_2":
        prompt = f"""You are a master typography auditor (V4.2 - Technical Modifier Precedence). Your task is to perform a rigorous evaluation of a font's relevance to specific user queries.

### DECISION RUBRIC
For a query to be a MATCH (1), the font must satisfy ALL primary technical constraints and the core vibe/intent described.
Partial matches or "almost matches" should be scored as NO MATCH (0) unless the query is broad.

### SPECIMEN INTERPRETATION GUARDRAILS
1. **Diagnostic Neutrality (Critical Distinction block)**
   - The Critical Distinction block appears on ALL specimens and is diagnostic-only.
   - Do NOT treat this block as category proof (e.g., monospace/coding) by itself.
   - For technical classification, verify evidence in body text/alphabet first (e.g., width consistency across letters, overall construction patterns).
2. **Geometric Inclusivity**
   - Geometric classification can still be valid when core geometric evidence is strong (e.g., round/simple construction in key glyphs like o/p/b), even if minor humanist traits are present.
   - Minor humanist cues alone must NOT override strong core geometric evidence.
3. **Luxury Anchor (Stricter High-End Requirement)**
   - Assign luxury/high-end serif only with stronger high-end signals (e.g., pronounced contrast and distinctive refined flourishes such as swash Q, teardrop terminals, couture-like detailing).
   - Do NOT elevate standard editorial/book serifs to luxury without those stronger signals.
4. **Vibe Over-extension (Display/Mood queries)**
   - For playful/whimsical/quirky/themed mood queries, require explicit structural novelty (e.g., irregular baseline, varying rhythm/width behavior, novelty stroke endings, asymmetrical construction).
   - Do NOT classify as playful based only on minor flourish details if the underlying architecture is formal/traditional.
5. **Category/Architecture Consistency (Technical Modifier Precedence)**
   - Category/Architecture Consistency is necessary but not sufficient; primary technical modifiers (e.g., condensed, monoline, slab weight) take precedence. Do not match solely on category when primary technical modifiers fail.

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
    elif prompt_type == "v5_1":
        prompt = f"""You are a master typography auditor (V5.1 - Diagnostic Neutrality). Your task is to perform a rigorous evaluation of a font's relevance to specific user queries.

### DECISION RUBRIC
For a query to be a MATCH (1), the font must satisfy ALL primary technical constraints and the core vibe/intent described.
Partial matches or "almost matches" should be scored as NO MATCH (0) unless the query is broad.

### SPECIMEN INTERPRETATION GUARDRAILS
1. **Diagnostic Neutrality (Critical Distinction block)**
   - Critical Distinction block is diagnostic-only; do not treat it as category proof by itself; verify category/technical classification primarily from body/alphabet evidence.

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
            content.append({
                "type": "image_url",
                "image_url": {"url": data_url}
            })
            
    payload = {
        "model": model,
        "temperature": 0.0, # Strict for auditing
        "messages": [
            {
                "role": "user",
                "content": content,
            },
        ],
        "response_format": { "type": "json_object" }
    }
    
    t0 = time.time()
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
        
    content_str = choices[0].get('message', {}).get('content', '').strip()
    
    try:
        data = json.loads(content_str)
        data['latency_sec'] = round(latency, 2)
        return data
    except json.JSONDecodeError:
        return {
            "audit_reasoning": f"Failed to parse JSON. Raw content: {content_str}",
            "results": [{"query_index": i+1, "match": 0, "confidence": 0, "evidence": "PARSE FAILURE"} for i in range(len(queries))],
            "latency_sec": round(latency, 2)
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="google/gemini-2.0-flash-lite-preview-02-05:free")
    parser.add_argument("--exp", choices=["prompt_v3", "prompt_v3_2", "prompt_v3_3", "prompt_v3_4", "render_v3", "full_v3", "full_v3_2", "full_v3_3", "full_v3_4", "baseline_v2", "segmented_v4_1", "prompt_v4_2", "prompt_v5_1"], required=True)
    parser.add_argument("--n", type=int, default=0, help="Number of pairs to run (0 for all)")
    parser.add_argument("--output", required=True)
    parser.add_argument("--specimen_dir", default="specimens_v3")
    args = parser.parse_args()

    data_dir = Path("research/ab-eval/data")
    out_dir = Path("research/ab-eval/out")
    spec_v3_dir = out_dir / args.specimen_dir
    
    # Intervention Logic
    prompt_type = "v5_1" if "v5_1" in args.exp else ("v4_2" if "v4_2" in args.exp else ("v3_4" if "v3_4" in args.exp else ("v3_3" if "v3_3" in args.exp else ("v3_2" if "v3_2" in args.exp else ("v3" if "prompt" in args.exp or "full" in args.exp or "segmented_v4_1" in args.exp else "v2")))))
    render_v3 = "render" in args.exp or "full" in args.exp or "segmented_v4_1" in args.exp or "v4_2" in args.exp or "v3" in args.specimen_dir
    
    print(f"Running Experiment: {args.exp} | Prompt: {prompt_type} | Render V3: {render_v3}")

    # Load labels for G2 calculation
    with open(data_dir / "labels.medium.human.v1.json", "r") as f:
        labels_v1 = json.load(f)
    
    # Load queries
    with open(data_dir / "queries.medium.human.v1.json", "r") as f:
        queries = json.load(f)
    query_map = {q["id"]: q["text"] for q in queries}

    # Load candidate pool
    with open(data_dir / "candidate_pool.medium.v1.json", "r") as f:
        pool = json.load(f)

    # Flatten pool into pairs
    pairs = []
    for qid, font_list in pool.items():
        for font in font_list:
            pairs.append((qid, font))
    
    if args.n > 0:
        # Use fixed seed for reproducibility
        import random
        random.seed(42)
        random.shuffle(pairs)
        pairs = pairs[:args.n]

    results = []
    
    # Group by font to save on image loading/batches
    font_to_qids = {}
    for qid, font in pairs:
        if font not in font_to_qids:
            font_to_qids[font] = []
        font_to_qids[font].append(qid)

    for font_name, qids in font_to_qids.items():
        safe_fname = font_name.replace(" ", "_")
        images = []
        if render_v3:
            images = [
                spec_v3_dir / f"{safe_fname}_top.png",
                spec_v3_dir / f"{safe_fname}_bottom.png"
            ]
        else:
            images = [out_dir / "specimens_v2_medium_nobias" / f"{safe_fname}.png"]
        
        # Check if images exist
        if not all(img.exists() for img in images):
            print(f"  Skipping {font_name}: Missing specimens")
            continue

        print(f"  Auditing {font_name} ({len(qids)} queries)...", end="", flush=True)
        
        # Split into batches of 5 to avoid context limit / timeout
        for i in range(0, len(qids), 5):
            batch_qids = qids[i:i+5]
            batch_texts = [query_map[qid] for qid in batch_qids]
            
            current_prompt_type = prompt_type
            if args.exp == "segmented_v4_1":
                # placeholder for segmentation logic if needed
                # strict path = v3_4 for categories: monospace, sans-serif, serif
                # relaxed path = v3 for categories: display, handwriting, unknown/unclassified
                # For now just use v3_4 as treatment in segmented
                current_prompt_type = "v3_4"
            
            resp = call_openrouter_batched(batch_texts, images, current_prompt_type, args.model)
            
            res_map = {r['query_index']: r for r in resp.get('results', [])}
            
            for idx, qid in enumerate(batch_qids):
                ai_res = res_map.get(idx + 1, {"match": 0, "confidence": 0, "evidence": "MISSING"})
                human_match = 1 if font_name in labels_v1.get(qid, []) else 0
                
                results.append({
                    "query_id": qid,
                    "query_text": query_map[qid],
                    "font_name": font_name,
                    "human_match": human_match,
                    "ai_match": ai_res.get("match", 0),
                    "confidence": ai_res.get("confidence", 0),
                    "evidence": ai_res.get("evidence", ""),
                    "counter_evidence": ai_res.get("counter_evidence", ""),
                    "thought": resp.get("audit_reasoning", ""),
                    "latency_sec": resp.get("latency_sec", 0)
                })
        
        print(" Done")

    # Calculate metrics
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

    final_output = {
        "exp": args.exp,
        "prompt_type": prompt_type,
        "render_v3": render_v3,
        "agreement": agreement,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "counts": {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "total": total},
        "details": results
    }

    with open(out_dir / args.output, "w") as f:
        json.dump(final_output, f, indent=2)
    
    print("\n" + "="*40)
    print(f"RESULTS: {args.exp}")
    print("="*40)
    print(f"Agreement: {agreement:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1:        {f1:.4f}")
    print(f"Output saved to {out_dir / args.output}")

if __name__ == "__main__":
    main()
