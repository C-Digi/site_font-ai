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

def call_openrouter(model: str, query: str, font_name: str, image_path: Path) -> Dict[str, Any]:
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
        return {
            "thought": f"Failed to parse JSON. Raw content: {content}",
            "match": 0,
            "latency_sec": round(latency, 2)
        }

class LocalQwenRouter:
    def __init__(self) -> None:
        self._loaded: Dict[str, Dict[str, Any]] = {}

    def _load_model(self, model: str) -> Dict[str, Any]:
        if model in self._loaded:
            return self._loaded[model]

        try:
            import torch
            from qwen_vl_utils import process_vision_info
            from transformers import AutoModelForImageTextToText, AutoProcessor
        except Exception as e:
            raise RuntimeError(f"Local Qwen dependencies unavailable: {e}")

        cuda = torch.cuda.is_available()
        dtype = torch.bfloat16 if cuda else torch.float32
        print(f"Loading local model {model} (CUDA: {cuda})...")
        load_t0 = time.time()
        model_obj = AutoModelForImageTextToText.from_pretrained(
            model,
            trust_remote_code=True,
            torch_dtype=dtype,
            device_map="auto" if cuda else None,
        ).eval()
        if not cuda:
            model_obj.to("cpu")

        processor = AutoProcessor.from_pretrained(model, trust_remote_code=True)
        load_latency = time.time() - load_t0
        print(f"Model loaded in {load_latency:.2f}s")

        bundle = {
            "model": model_obj,
            "processor": processor,
            "process_vision_info": process_vision_info,
            "cuda": cuda,
            "load_latency_sec": round(load_latency, 3),
        }
        self._loaded[model] = bundle
        return bundle

    def generate(self, model: str, query: str, font_name: str, image_path: Path) -> Dict[str, Any]:
        bundle = self._load_model(model)
        model_obj = bundle["model"]
        processor = bundle["processor"]
        process_vision_info = bundle["process_vision_info"]

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

        image_uri = str(image_path.resolve())
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_uri},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        chat_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[chat_text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )

        if bundle["cuda"]:
            inputs = inputs.to(model_obj.device)

        t0 = time.time()
        import torch
        with torch.no_grad():
            out_ids = model_obj.generate(
                **inputs,
                max_new_tokens=512,
            )
        latency = time.time() - t0

        generated_ids = [
            output_ids[len(input_ids) :] for input_ids, output_ids in zip(inputs.input_ids, out_ids)
        ]
        content = processor.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0].strip()

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

def run_evaluation(model_id: str, is_local: bool, local_router: LocalQwenRouter = None):
    print(f"\n=== Starting Evaluation for {model_id} ({'Local' if is_local else 'OpenRouter'}) ===")
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
        queries = {q['id']: q for q in json.load(f)}
    with open(labels_path, "r") as f:
        human_labels = json.load(f)
    with open(candidates_path, "r") as f:
        candidate_pool = json.load(f)
        
    target_query_ids = ["cq_002", "cq_011", "cq_025", "cq_033", "cq_016"]
    results = []
    
    for qid in target_query_ids:
        query_text = queries[qid]['text']
        print(f"\n[QUERY] {qid}: {query_text}")
        
        candidates = candidate_pool.get(qid, [])[:3]
        labeled_positive = set(human_labels.get(qid, []))
        
        for font_name in candidates:
            safe_name = font_name.replace(" ", "_").replace("/", "_")
            image_path = specimen_dir / f"{safe_name}.png"
            
            if not image_path.exists():
                print(f"  [MISSING] {font_name}")
                continue
                
            print(f"  [JUDGING] {font_name}...", end="", flush=True)
            try:
                if is_local:
                    judgment = local_router.generate(model_id, query_text, font_name, image_path)
                else:
                    judgment = call_openrouter(model_id, query_text, font_name, image_path)
            except Exception as e:
                print(f" Error: {e}")
                judgment = {"thought": f"Error: {e}", "match": 0, "latency_sec": 0}
            
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
            
            if not is_local:
                time.sleep(1)
            
    total = len(results)
    if total == 0:
        return None
        
    tp = sum(1 for r in results if r['ai_match'] == 1 and r['human_match'] == 1)
    fp = sum(1 for r in results if r['ai_match'] == 1 and r['human_match'] == 0)
    fn = sum(1 for r in results if r['ai_match'] == 0 and r['human_match'] == 1)
    tn = sum(1 for r in results if r['ai_match'] == 0 and r['human_match'] == 0)
    
    agreement_rate = (tp + tn) / total
    
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
    
    # Model 1: OpenRouter Qwen 235B
    model_235b = "qwen/qwen3-vl-235b-a22b-instruct"
    res_235b = run_evaluation(model_235b, is_local=False)
    if res_235b:
        with open(out_dir / "spot_check_alignment_qwen3vl_235b.json", "w") as f:
            json.dump(res_235b, f, indent=2)
            
    # Model 2: Local Qwen 8B
    # Note: Using the HF ID for local loading
    model_8b_local = "Qwen/Qwen3-VL-8B-Instruct"
    router = LocalQwenRouter()
    res_8b = run_evaluation(model_8b_local, is_local=True, local_router=router)
    if res_8b:
        with open(out_dir / "spot_check_alignment_qwen3vl_8b_local.json", "w") as f:
            json.dump(res_8b, f, indent=2)

if __name__ == "__main__":
    main()
