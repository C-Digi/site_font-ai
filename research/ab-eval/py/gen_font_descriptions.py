import argparse
import base64
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv


DEFAULT_CORPUS = "research/ab-eval/data/corpus.200.json"
DEFAULT_GLYPH_DIR = "research/ab-eval/out/glyphs"
DEFAULT_OUT = "research/ab-eval/out/descriptions_bakeoff.jsonl"

REQUIRED_MODEL_SLATE = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite-preview-09-2025",
    "Qwen/Qwen3-VL-8B-Instruct",
    "qwen/qwen3-vl-8b-instruct",
    "openai/gpt-5.2", # Track A directive
]

OPTIONAL_MODEL_SLATE = [
    "google/gemini-2.5-flash-image",
]

DEFAULT_PROMPT_TEMPLATE = """You are a typography expert.
Analyze the provided glyph-sheet image only.

Important constraints:
- Do not guess or mention any font family name.
- Focus on visual typographic attributes from the image.

Return STRICT JSON only (no markdown, no prose outside JSON) using this exact structure:
{
  "shape": "short description of overall letterform geometry",
  "contrast": "stroke contrast characterization",
  "terminals": "terminal/ending style characterization",
  "x_height": "x-height impression",
  "width": "relative width/fit characterization",
  "mood": ["3-6 concise mood/style terms"],
  "use_cases": ["3-6 likely design/application use-cases"],
  "summary": "2-4 sentence integrated description"
}

Use only what is visible in the glyph sheet.
"""


def _project_root() -> Path:
    # .../research/ab-eval/py/gen_font_descriptions.py -> project root is parents[3]
    return Path(__file__).resolve().parents[3]


def load_environment() -> None:
    root = _project_root()
    load_dotenv(root / ".env", override=False)
    load_dotenv(root / ".env.local", override=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate vision-grounded font descriptions from glyph-sheet PNGs across multiple model providers."
    )
    parser.add_argument("--corpus", default=DEFAULT_CORPUS)
    parser.add_argument("--glyph-dir", default=DEFAULT_GLYPH_DIR)
    parser.add_argument(
        "--models",
        default=",".join(REQUIRED_MODEL_SLATE),
        help="Comma-separated model IDs.",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--prompt-template",
        default="default_v1",
        help="Either 'default_v1' or a path to a custom template file.",
    )
    parser.add_argument("--schema-version", type=int, default=1, help="1 (legacy) or 2 (quality-first).")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--include-optional-fallback",
        action="store_true",
        help="Append optional fallback model IDs to --models if not already present.",
    )
    return parser.parse_args()


def parse_models(models_arg: str, include_optional_fallback: bool) -> List[str]:
    models = [m.strip() for m in models_arg.split(",") if m.strip()]
    if include_optional_fallback:
        for m in OPTIONAL_MODEL_SLATE:
            if m not in models:
                models.append(m)
    return models


def provider_for_model(model: str) -> str:
    if model.startswith("gemini-"):
        return "gemini"
    if model.startswith("Qwen/"):
        return "local_qwen"
    if model.startswith("qwen/") or model.startswith("google/") or model.startswith("openai/"):
        return "openrouter"
    # default to OpenRouter for unknown slash-style models
    if "/" in model:
        return "openrouter"
    return "unknown"


def load_prompt_template(arg: str) -> Tuple[str, str]:
    if arg == "default_v1":
        return "default_v1", DEFAULT_PROMPT_TEMPLATE

    p = Path(arg)
    if not p.exists():
        raise FileNotFoundError(f"Prompt template not found: {arg}")
    content = p.read_text(encoding="utf-8")
    return str(p), content


def safe_font_name(name: str) -> str:
    safe = name.replace("/", "_").replace("\\", "_").replace(" ", "_")
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", safe)
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe


def build_glyph_index(glyph_dir: Path) -> Dict[str, Path]:
    idx: Dict[str, Path] = {}
    if not glyph_dir.exists():
        return idx
    for p in glyph_dir.glob("*.png"):
        idx[p.stem.lower()] = p
    return idx


def find_glyph(font_name: str, glyph_dir: Path, glyph_index: Dict[str, Path]) -> Optional[Path]:
    candidate_stems = [
        safe_font_name(font_name),
        font_name.replace(" ", "_"),
        font_name,
    ]
    for stem in candidate_stems:
        p = glyph_dir / f"{stem}.png"
        if p.exists():
            return p

    return glyph_index.get(safe_font_name(font_name).lower())


def read_corpus(path: Path, limit: Optional[int]) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Corpus must be a JSON array: {path}")
    if limit is not None:
        return data[: max(0, limit)]
    return data


def load_existing_keys_for_resume(out_path: Path) -> set:
    keys = set()
    if not out_path.exists():
        return keys

    with out_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (
                str(row.get("font_name", "")),
                str(row.get("model", "")),
                str(row.get("prompt_template", "")),
            )
            keys.add(key)
    return keys


def image_to_data_url(image_path: Path) -> str:
    b = image_path.read_bytes()
    b64 = base64.b64encode(b).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _extract_text_from_openrouter_choice(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out_parts = []
        for part in content:
            if isinstance(part, dict):
                txt = part.get("text")
                if isinstance(txt, str):
                    out_parts.append(txt)
        return "\n".join(out_parts).strip()
    return ""


def call_gemini(model: str, prompt: str, image_path: Path, timeout_s: int = 180) -> Tuple[str, Dict[str, Any]]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": b64}},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }

    t0 = time.time()
    resp = requests.post(url, json=payload, timeout=timeout_s)
    latency = time.time() - t0

    if not resp.ok:
        msg = resp.text
        if len(msg) > 800:
            msg = msg[:800] + "..."
        raise RuntimeError(f"Gemini HTTP {resp.status_code}: {msg}")

    body = resp.json()
    text_out = ""
    for cand in body.get("candidates", []):
        content = cand.get("content", {})
        for part in content.get("parts", []):
            txt = part.get("text")
            if isinstance(txt, str) and txt.strip():
                text_out = txt
                break
        if text_out:
            break

    if not text_out:
        raise RuntimeError("Gemini returned no text candidate")

    metadata = {
        "latency_sec": round(latency, 3),
        "usage": body.get("usageMetadata"),
        "response_model_version": body.get("modelVersion"),
    }
    return text_out, metadata


def call_openrouter(model: str, prompt: str, image_path: Path, timeout_s: int = 180) -> Tuple[str, Dict[str, Any]]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data_url = image_to_data_url(image_path)
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": "Return strict JSON only following the user-provided schema.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
    }

    # High-reasoning / thinking mode directive for openai/gpt-5.2
    if model == "openai/gpt-5.2":
        payload["include_reasoning"] = True
        # Documentation: gpt-5.2 uses high reasoning levels by default when this flag is set.
        # Fallback is standard generation if not supported.

    t0 = time.time()
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    latency = time.time() - t0

    if not resp.ok:
        msg = resp.text
        if len(msg) > 800:
            msg = msg[:800] + "..."
        raise RuntimeError(f"OpenRouter HTTP {resp.status_code}: {msg}")

    body = resp.json()
    choices = body.get("choices", [])
    if not choices:
        raise RuntimeError("OpenRouter returned no choices")
    text_out = _extract_text_from_openrouter_choice(choices[0].get("message", {}).get("content"))
    if not text_out:
        raise RuntimeError("OpenRouter returned empty message content")

    metadata = {
        "latency_sec": round(latency, 3),
        "usage": body.get("usage"),
        "provider": body.get("provider"),
        "id": body.get("id"),
    }
    return text_out, metadata


class LocalQwenRouter:
    def __init__(self) -> None:
        self._loaded: Dict[str, Dict[str, Any]] = {}

    def _load_model(self, model: str) -> Dict[str, Any]:
        if model in self._loaded:
            return self._loaded[model]

        try:
            import torch  # type: ignore
            from qwen_vl_utils import process_vision_info  # type: ignore
            from transformers import AutoModelForImageTextToText, AutoProcessor  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Local Qwen dependencies unavailable: {e}")

        cuda = torch.cuda.is_available()
        dtype = torch.bfloat16 if cuda else torch.float32
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

        bundle = {
            "model": model_obj,
            "processor": processor,
            "process_vision_info": process_vision_info,
            "cuda": cuda,
            "load_latency_sec": round(load_latency, 3),
        }
        self._loaded[model] = bundle
        return bundle

    def generate(self, model: str, prompt: str, image_path: Path) -> Tuple[str, Dict[str, Any]]:
        bundle = self._load_model(model)
        model_obj = bundle["model"]
        processor = bundle["processor"]
        process_vision_info = bundle["process_vision_info"]

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
        out_ids = model_obj.generate(
            **inputs,
            max_new_tokens=400,
            do_sample=False,
            temperature=0.0,
        )
        latency = time.time() - t0

        trimmed = [
            out[len(inp) :]
            for inp, out in zip(inputs.input_ids, out_ids)
        ]
        text_out = processor.batch_decode(
            trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]

        metadata = {
            "latency_sec": round(latency, 3),
            "local_cuda": bundle["cuda"],
            "model_load_latency_sec": bundle["load_latency_sec"],
        }
        return text_out, metadata

def _coerce_list_str(v: Any) -> List[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str):
        # allow comma-separated fallback
        parts = [p.strip() for p in v.split(",")]
        return [p for p in parts if p]
    return []


def _coerce_score_dict(v: Any) -> Dict[str, float]:
    out = {}
    if isinstance(v, dict):
        for k, val in v.items():
            try:
                out[str(k)] = float(val)
            except:
                continue
    return out


def normalize_description_v1_json(obj: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {
        "shape": str(obj.get("shape", "")).strip(),
        "contrast": str(obj.get("contrast", "")).strip(),
        "terminals": str(obj.get("terminals", "")).strip(),
        "x_height": str(obj.get("x_height", "")).strip(),
        "width": str(obj.get("width", "")).strip(),
        "mood": _coerce_list_str(obj.get("mood", [])),
        "use_cases": _coerce_list_str(obj.get("use_cases", [])),
        "summary": str(obj.get("summary", "")).strip(),
    }
    return normalized


def normalize_description_v2_json(obj: Dict[str, Any]) -> Dict[str, Any]:
    # Schema V2 with uncertainty and scored blocks
    vis = obj.get("visual_analysis", {})
    if not isinstance(vis, dict):
        vis = {}

    def norm_attr(d):
        if not isinstance(d, dict):
            return {"value": str(d), "certainty": 0.5}
        return {
            "value": str(d.get("value", "")),
            "certainty": float(d.get("certainty", 0.5))
        }

    normalized = {
        "visual_analysis": {
            "shape": norm_attr(vis.get("shape")),
            "contrast": norm_attr(vis.get("contrast")),
            "terminals": norm_attr(vis.get("terminals")),
            "x_height": norm_attr(vis.get("x_height")),
        },
        "mood_scores": _coerce_score_dict(obj.get("mood_scores")),
        "use_case_scores": _coerce_score_dict(obj.get("use_case_scores")),
        "uncertainty_discipline": {
            "low_evidence_attributes": _coerce_list_str(obj.get("uncertainty_discipline", {}).get("low_evidence_attributes")),
            "reasoning": str(obj.get("uncertainty_discipline", {}).get("reasoning", ""))
        },
        "summary": str(obj.get("summary", "")).strip(),
    }
    return normalized


def try_parse_strict_json(raw_text: str, schema_version: int = 1) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    t = (raw_text or "").strip()
    parse_meta: Dict[str, Any] = {"parse_path": None}

    if not t:
        parse_meta["parse_path"] = "empty"
        return None, parse_meta

    # 1) direct JSON parse
    try:
        parsed = json.loads(t)
        if isinstance(parsed, dict):
            parse_meta["parse_path"] = "direct"
            if schema_version == 2:
                return normalize_description_v2_json(parsed), parse_meta
            return normalize_description_v1_json(parsed), parse_meta
    except json.JSONDecodeError:
        pass

    # 2) markdown fenced JSON
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, flags=re.DOTALL | re.IGNORECASE)
    if m:
        inner = m.group(1)
        try:
            parsed = json.loads(inner)
            if isinstance(parsed, dict):
                parse_meta["parse_path"] = "fenced"
                if schema_version == 2:
                    return normalize_description_v2_json(parsed), parse_meta
                return normalize_description_v1_json(parsed), parse_meta
        except json.JSONDecodeError:
            pass

    # 3) first JSON object substring
    m2 = re.search(r"\{[\s\S]*\}", t)
    if m2:
        candidate = m2.group(0)
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                parse_meta["parse_path"] = "substring"
                if schema_version == 2:
                    return normalize_description_v2_json(parsed), parse_meta
                return normalize_description_v1_json(parsed), parse_meta
        except json.JSONDecodeError:
            pass

    parse_meta["parse_path"] = "failed"
    return None, parse_meta


def description_from_structured(d: Dict[str, Any]) -> str:
    if "visual_analysis" in d:
        # V2 path
        vis = d["visual_analysis"]
        moods = [f"{k}({v})" for k, v in d.get("mood_scores", {}).items() if v > 0.3]
        use_cases = [f"{k}({v})" for k, v in d.get("use_case_scores", {}).items() if v > 0.3]
        
        parts = [
            f"Shape: {vis.get('shape', {}).get('value')} (c={vis.get('shape', {}).get('certainty')})",
            f"Contrast: {vis.get('contrast', {}).get('value')} (c={vis.get('contrast', {}).get('certainty')})",
            f"Terminals: {vis.get('terminals', {}).get('value')} (c={vis.get('terminals', {}).get('certainty')})",
            f"Moods: {', '.join(moods)}",
            f"Use-cases: {', '.join(use_cases)}",
            f"Summary: {d.get('summary', '')}",
        ]
        return " | ".join(parts)

    # V1 path
    mood = ", ".join(d.get("mood", []))
    use_cases = ", ".join(d.get("use_cases", []))
    parts = [
        f"Shape: {d.get('shape', '')}",
        f"Contrast: {d.get('contrast', '')}",
        f"Terminals: {d.get('terminals', '')}",
        f"x-height: {d.get('x_height', '')}",
        f"Width: {d.get('width', '')}",
        f"Mood: {mood}",
        f"Use-cases: {use_cases}",
        f"Summary: {d.get('summary', '')}",
    ]
    return " | ".join(parts)


def fallback_description(raw_text: str) -> str:
    compact = re.sub(r"\s+", " ", raw_text).strip()
    if len(compact) > 1200:
        compact = compact[:1200] + "..."
    return compact


def invoke_model(
    provider: str,
    model: str,
    prompt: str,
    glyph_path: Path,
    local_router: LocalQwenRouter,
) -> Tuple[str, Dict[str, Any]]:
    if provider == "gemini":
        return call_gemini(model=model, prompt=prompt, image_path=glyph_path)
    if provider == "openrouter":
        return call_openrouter(model=model, prompt=prompt, image_path=glyph_path)
    if provider == "local_qwen":
        return local_router.generate(model=model, prompt=prompt, image_path=glyph_path)
    raise RuntimeError(f"Unsupported provider routing for model '{model}' (provider='{provider}')")


def write_summary_md(out_path: Path, attempted: int, ok: int, err: int, skipped: int) -> Path:
    summary_path = out_path.with_suffix(".summary.md")
    
    rows: List[Dict[str, Any]] = []
    with out_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except:
                continue

    by_model: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        m = r["model"]
        if m not in by_model:
            by_model[m] = {"ok": 0, "err": 0, "latencies": [], "errors": []}
        if r["status"] == "ok":
            by_model[m]["ok"] += 1
            by_model[m]["latencies"].append(r["metadata"].get("elapsed_sec", 0))
        else:
            by_model[m]["err"] += 1
            by_model[m]["errors"].append(r.get("error"))

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# Font Description Bakeoff Summary\n\n")
        f.write(f"- **Run Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Input Artifact:** `{out_path.name}`\n")
        f.write(f"- **Total Rows Attempted:** {attempted}\n")
        f.write(f"- **Total Success:** {ok}\n")
        f.write(f"- **Total Failures:** {err}\n")
        f.write(f"- **Total Resumed/Skipped:** {skipped}\n\n")

        f.write("## Model Performance & Availability\n\n")
        f.write("| Model | Provider | Status | Success | Failure | Avg Latency (s) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        for model_id, stats in by_model.items():
            avg_lat = round(sum(stats["latencies"]) / len(stats["latencies"]), 2) if stats["latencies"] else "N/A"
            provider = provider_for_model(model_id)
            status = "🟢" if stats["ok"] > 0 and stats["err"] == 0 else "🟡" if stats["ok"] > 0 else "🔴"
            f.write(f"| {model_id} | {provider} | {status} | {stats['ok']} | {stats['err']} | {avg_lat} |\n")

    return summary_path


def main() -> None:
    args = parse_args()
    load_environment()

    corpus_path = Path(args.corpus)
    glyph_dir = Path(args.glyph_dir)
    out_path = Path(args.out)

    models = parse_models(args.models, args.include_optional_fallback)
    prompt_template_id, prompt_template_text = load_prompt_template(args.prompt_template)

    # Auto-detect schema v2 from prompt template path if not explicitly set
    schema_version = args.schema_version
    if schema_version == 1 and "prompt_v2" in str(prompt_template_id):
        schema_version = 2

    corpus = read_corpus(corpus_path, args.limit)
    glyph_index = build_glyph_index(glyph_dir)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing_keys = load_existing_keys_for_resume(out_path) if args.resume else set()

    local_router = LocalQwenRouter()

    total = 0
    skipped_resume = 0
    ok = 0
    err = 0

    mode = "a" if out_path.exists() else "w"
    with out_path.open(mode, encoding="utf-8") as out_f:
        for i, font in enumerate(corpus, start=1):
            font_name = str(font.get("name", "")).strip()
            if not font_name:
                continue

            glyph_path = find_glyph(font_name, glyph_dir, glyph_index)

            for model in models:
                total += 1
                provider = provider_for_model(model)
                key = (font_name, model, prompt_template_id)

                if key in existing_keys:
                    skipped_resume += 1
                    continue

                row: Dict[str, Any] = {
                    "font_name": font_name,
                    "model": model,
                    "provider": provider,
                    "prompt_template": prompt_template_id,
                    "schema_version": schema_version,
                    "description": "",
                    "metadata": {
                        "font_index": i,
                        "glyph_dir": str(glyph_dir),
                    },
                    "status": "error",
                    "error": None,
                }

                t0 = time.time()

                if glyph_path is None:
                    row["error"] = f"Glyph PNG not found for font '{font_name}' in {glyph_dir}"
                    row["metadata"]["elapsed_sec"] = round(time.time() - t0, 3)
                    out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    out_f.flush()
                    err += 1
                    print(f"[error] {font_name} :: {model} :: missing glyph")
                    continue

                row["metadata"]["glyph_path"] = str(glyph_path)

                if args.dry_run:
                    row["status"] = "dry_run"
                    row["metadata"]["elapsed_sec"] = round(time.time() - t0, 3)
                    out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    out_f.flush()
                    print(f"[dry-run] {font_name} :: {model}")
                    continue

                try:
                    raw_text, provider_meta = invoke_model(
                        provider=provider,
                        model=model,
                        prompt=prompt_template_text,
                        glyph_path=glyph_path,
                        local_router=local_router,
                    )
                    parsed_json, parse_meta = try_parse_strict_json(raw_text, schema_version=schema_version)

                    if parsed_json is not None:
                        desc = description_from_structured(parsed_json)
                        row["metadata"]["parsed_json"] = parsed_json
                    else:
                        desc = fallback_description(raw_text)
                        row["metadata"]["raw_response_excerpt"] = fallback_description(raw_text)

                    row["description"] = desc
                    row["metadata"]["provider"] = provider_meta
                    row["metadata"]["parse"] = parse_meta
                    row["metadata"]["elapsed_sec"] = round(time.time() - t0, 3)
                    row["status"] = "ok"
                    ok += 1
                    print(f"[ok] {font_name} :: {model}")
                except Exception as e:
                    row["error"] = str(e)
                    row["metadata"]["elapsed_sec"] = round(time.time() - t0, 3)
                    err += 1
                    print(f"[error] {font_name} :: {model} :: {e}")

                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                out_f.flush()

    print("\nDone.")
    print(f"  Rows attempted (font x model): {total}")
    print(f"  Success rows: {ok}")
    print(f"  Error rows: {err}")
    print(f"  Resume-skipped rows: {skipped_resume}")
    print(f"  Output: {out_path}")

    if ok + err > 0:
        sum_path = write_summary_md(out_path, total, ok, err, skipped_resume)
        print(f"  Summary: {sum_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.")
        sys.exit(130)
