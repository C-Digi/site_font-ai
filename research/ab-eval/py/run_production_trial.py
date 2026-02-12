import os
import json
import base64
import time
import argparse
import re
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


def remap_casey_label(label: Any) -> int:
    """
    Governance policy: non-binary label 2 is treated as 0 for primary metrics.
    """
    if label == 2:
        return 0
    return 1 if label == 1 else 0

def load_api_keys(keys_file: str = "") -> List[str]:
    keys: List[str] = []

    if GEMINI_API_KEY:
        keys.append(GEMINI_API_KEY)

    if keys_file:
        p = Path(keys_file)
        if p.exists():
            raw = p.read_text(encoding="utf-8")
            for line in raw.splitlines():
                # Support markdown/backtick-wrapped keys and plain text keys
                m = re.search(r"AIza[0-9A-Za-z_\-]{30,}", line)
                if m:
                    keys.append(m.group(0))

    # de-duplicate while preserving order
    unique: List[str] = []
    seen = set()
    for k in keys:
        if k not in seen:
            unique.append(k)
            seen.add(k)

    return unique

def image_to_base64(image_path: Path) -> str:
    if not image_path.exists():
        return ""
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")

def call_gemini_v3(
    queries: List[str],
    images: List[Path],
    model: str,
    prompt_type: str = "v3",
    api_keys: List[str] = None,
) -> Dict[str, Any]:
    if api_keys is None:
        api_keys = []
    if not api_keys:
        raise RuntimeError("No GEMINI_API_KEY available (env or keys file)")

    headers = {
        "Content-Type": "application/json",
    }
    
    queries_formatted = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(queries)])
    
    if prompt_type == "v4":
        prompt = f"""You are a master typography auditor (V4 - Intent Aware). Your task is to perform a rigorous evaluation of a font's relevance to specific user queries.

### DECISION RUBRIC
1. **Technical Alignment**: If a query uses definitive technical terms (e.g., 'Monospace', 'Serif', 'Geometric', 'Condensed'), the font MUST strictly adhere to these.
2. **Intent & Mood**: For descriptive queries (e.g., 'friendly', 'futuristic', 'professional', 'warm'), evaluate the holistic 'intent'. Do not be over-pedantic with minor technicalities if the font clearly serves the intended use case and vibe.
3. **Match (1)**: Satisfies all strict technical constraints AND aligns with the core intent/vibe.
4. **No Match (0)**: Fails a technical constraint OR lacks the required mood/intent.

### EVIDENCE REQUIREMENT
For EACH query, you must provide a short specific visual evidence snippet from the specimen justifying your decision.

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
For EACH query, provide a short specific visual evidence snippet from the specimen.

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
For EACH query, provide a short specific visual evidence snippet from the specimen.

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
For EACH query, provide a short specific visual evidence snippet from the specimen.

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
    
    t0 = time.time()
    last_error = ""
    max_attempts = max(5, len(api_keys) * 2)
    for attempt in range(max_attempts):
        active_key = api_keys[attempt % len(api_keys)]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={active_key}"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 429:
                last_error = f"429 RESOURCE_EXHAUSTED: {resp.text[:300]}"
                time.sleep(1)
                continue
            if resp.status_code == 503:
                last_error = f"503 UNAVAILABLE: {resp.text[:300]}"
                time.sleep(5)
                continue
            if not resp.ok:
                last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
                time.sleep(1)
                continue
            break
        except Exception as e:
            last_error = f"Exception: {str(e)}"
            time.sleep(1)
    else:
        return {"error": f"Failed after {max_attempts} attempts ({last_error})"}
        
    latency = time.time() - t0
    try:
        res = resp.json()
        content_str = res['candidates'][0]['content']['parts'][0]['text'].strip()
        data = json.loads(content_str)
        data['latency_sec'] = round(latency, 2)
        return data
    except Exception as e:
        return {"error": f"Parse error: {str(e)}", "raw": content_str if 'content_str' in locals() else ""}

def calculate_metrics(results: List[Dict[str, Any]], ssot_map: Dict[Tuple[str, str], int], confidence_gate: float = 0.9) -> Dict[str, Any]:
    tp = fp = fn = tn = 0
    gated_results = []
    
    for r in results:
        key = (r["query_id"], r["font_name"])
        if key not in ssot_map:
            continue
            
        h = remap_casey_label(ssot_map[key])
        
        # Apply confidence gating
        raw_match = r.get("ai_match", 0)
        confidence = r.get("confidence", 1.0)
        
        # Policy: 0.9 confidence gating for strict decision
        # Matches with confidence < gate are treated as 0
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
    parser.add_argument("--model", default="gemini-3-pro-preview")
    parser.add_argument("--prompt", choices=["v3", "v3_2", "v3_3", "v3_4", "v4"], default="v3")
    parser.add_argument("--gate", type=float, default=0.9)
    parser.add_argument("--spec-dir", default="specimens_v3", help="Subdirectory in out/ containing specimens")
    parser.add_argument("--output", help="Optional custom output filename")
    parser.add_argument("--cache-output", default="", help="Optional cache filename for resumable raw rows")
    parser.add_argument("--max-fonts", type=int, default=0, help="Limit number of fonts to process for smoke tests")
    parser.add_argument("--keys-file", default="", help="Optional file containing multiple Gemini API keys to cycle")
    args = parser.parse_args()

    api_keys = load_api_keys(args.keys_file)
    if not api_keys:
        raise RuntimeError("No API keys found. Set GEMINI_API_KEY or pass --keys-file")

    print(f"Loaded {len(api_keys)} Gemini API key(s)")

    out_dir = Path("research/ab-eval/out")
    data_dir = Path("research/ab-eval/data")
    
    # 1. Load SSoT
    ssot_path = out_dir / "full_set_review_export_1770612809775.json"
    with open(ssot_path, 'r') as f:
        ssot_data = json.load(f)
    
    ssot_map = {}
    for d in ssot_data['decisions']:
        ssot_map[(d['query_id'], d['font_name'])] = remap_casey_label(d.get('casey_label', 0))
        
    # 2. Get Population from SSoT
    font_to_queries = {}
    for d in ssot_data['decisions']:
        fname = d['font_name']
        if fname not in font_to_queries:
            font_to_queries[fname] = []
        font_to_queries[fname].append(d)

    # 3. Load Queries for text
    queries_path = data_dir / "queries.medium.human.v1.json"
    with open(queries_path, 'r') as f:
        queries_json = json.load(f)
    query_text_map = {q['id']: q['text'] for q in queries_json}

    results = []
    spec_v3_dir = out_dir / args.spec_dir
    
    print(f"Executing Production Trial: Model={args.model} | Specimen={args.spec_dir} | Prompt={args.prompt} | Gate={args.gate}")
    
    processed_count = 0
    font_names = sorted(list(font_to_queries.keys()))

    if args.max_fonts and args.max_fonts > 0:
        font_names = font_names[:args.max_fonts]
    
    # Check for existing cache to resume
    if args.cache_output:
        cache_name = args.cache_output
    elif args.output:
        cache_name = f"{Path(args.output).stem}_raw.json"
    else:
        cache_name = f"g3_pro_{args.prompt}_gated_raw.json"

    cache_path = out_dir / cache_name
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            results = json.load(f)
        processed_fonts = set(r['font_name'] for r in results)
        font_names = [f for f in font_names if f not in processed_fonts]
        print(f"Resuming from cache, {len(processed_fonts)} fonts already processed.")

    try:
        for fname in font_names:
            font_pairs = font_to_queries[fname]
            safe_fname = fname.replace(" ", "_")
            images = [
                spec_v3_dir / f"{safe_fname}_top.png",
                spec_v3_dir / f"{safe_fname}_bottom.png"
            ]
            
            # Verify images exist
            if not images[0].exists() or not images[1].exists():
                print(f"  WARNING: Missing specimens for {fname}")
                continue

            q_ids = [p['query_id'] for p in font_pairs]
            q_texts = [query_text_map[qid] for qid in q_ids]
            
            print(f"[{processed_count}/{len(font_names)}] {fname} ({len(q_texts)} pairs)...", end="", flush=True)
            
            # Batch call (max 10 at a time for safety/context)
            for i in range(0, len(q_texts), 10):
                batch_texts = q_texts[i:i+10]
                batch_ids = q_ids[i:i+10]
                
                resp = call_gemini_v3(batch_texts, images, args.model, args.prompt, api_keys)
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
            processed_count += 1
            
            # Save intermediate
            with open(cache_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopped.")

    # 4. Final Metric Computation
    metrics = calculate_metrics(results, ssot_map, args.gate)
    
    # Save final results
    final_path = out_dir / (args.output if args.output else f"g3_pro_{args.prompt}_gated_results.json")
    with open(final_path, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print("\n" + "="*40)
    print("FINAL METRICS")
    print("="*40)
    print(f"Agreement: {metrics['agreement']*100:.2f}%")
    print(f"Precision: {metrics['precision']*100:.2f}%")
    print(f"Recall:    {metrics['recall']*100:.2f}%")
    print(f"F1 Score:  {metrics['f1']*100:.2f}%")
    print(f"Counts:    {metrics['counts']}")
    print(f"Saved to {final_path}")

if __name__ == "__main__":
    main()
