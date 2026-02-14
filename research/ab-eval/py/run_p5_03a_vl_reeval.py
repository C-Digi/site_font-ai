"""
P5-03A: B2 vs VL-enriched text-only baseline (offline, bounded)

Compares two embedding-path arms on the medium human SSoT pair set:
- Arm 1 (treatment): B2 production path (VL query + B2 doc embeddings)
- Arm 2 (baseline): text-only path using VL-enriched descriptions (no image input)

Outputs:
- research/ab-eval/out/p5_03a_b2_vs_text_comparison.json
- research/ab-eval/out/p5_03a_b2_vs_text_gates.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import requests


def remap_label(label: Any) -> int:
    """Governance policy: non-binary label 2 is treated as 0 for primary metrics."""
    if label == 2:
        return 0
    return 1 if label == 1 else 0


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def cosine_similarity_matrix(queries: np.ndarray, docs: np.ndarray) -> np.ndarray:
    queries_norm = queries / (np.linalg.norm(queries, axis=1, keepdims=True) + 1e-9)
    docs_norm = docs / (np.linalg.norm(docs, axis=1, keepdims=True) + 1e-9)
    return np.dot(queries_norm, docs_norm.T)


def build_topk_map(
    score_matrix: np.ndarray,
    doc_names: List[str],
    query_ids: List[str],
    k: int,
) -> Dict[str, List[Tuple[str, float]]]:
    out: Dict[str, List[Tuple[str, float]]] = {}
    for i, qid in enumerate(query_ids):
        idx = np.argsort(score_matrix[i])[::-1][:k]
        out[qid] = [(doc_names[j], float(score_matrix[i][j])) for j in idx]
    return out


def compute_retrieval_metrics(
    score_matrix: np.ndarray,
    doc_names: List[str],
    query_ids: List[str],
    labels: Dict[str, List[str]],
) -> Dict[str, float]:
    recall10_sum = 0.0
    recall20_sum = 0.0
    mrr10_sum = 0.0
    n = 0

    for i, qid in enumerate(query_ids):
        if qid not in labels:
            continue
        gt = set(labels[qid])
        if not gt:
            continue

        n += 1
        ranked_idx = np.argsort(score_matrix[i])[::-1]
        ranked_docs = [doc_names[j] for j in ranked_idx]

        top10 = ranked_docs[:10]
        top20 = ranked_docs[:20]

        hits10 = len(set(top10) & gt)
        hits20 = len(set(top20) & gt)
        recall10_sum += hits10 / len(gt)
        recall20_sum += hits20 / len(gt)

        rr = 0.0
        for rank, d in enumerate(top10, start=1):
            if d in gt:
                rr = 1.0 / rank
                break
        mrr10_sum += rr

    if n == 0:
        return {"Recall@10": 0.0, "Recall@20": 0.0, "MRR@10": 0.0}

    return {
        "Recall@10": round(recall10_sum / n, 6),
        "Recall@20": round(recall20_sum / n, 6),
        "MRR@10": round(mrr10_sum / n, 6),
    }


def compute_pair_metrics(pairs: List[Dict[str, Any]], pred_key: str) -> Dict[str, Any]:
    tp = fp = fn = tn = 0
    for p in pairs:
        h = p["human"]
        a = p[pred_key]
        if h == 1 and a == 1:
            tp += 1
        elif h == 0 and a == 1:
            fp += 1
        elif h == 1 and a == 0:
            fn += 1
        else:
            tn += 1

    total = len(pairs)
    agreement = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "agreement": round(agreement, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "counts": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "total": total,
        },
    }


def call_openrouter_embedding(text: str, api_key: str, model: str, retries: int = 5) -> List[float]:
    url = "https://openrouter.ai/api/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "input": text}

    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 429:
                time.sleep(min(30, 3 * (attempt + 1)))
                continue
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(min(30, 2 * (attempt + 1)))

    raise RuntimeError("Embedding request failed after retries")


def pick_vl_description(
    rows: List[Dict[str, Any]],
    preferred_model: str,
) -> Dict[str, str]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        name = r.get("font_name")
        if not name:
            continue
        grouped.setdefault(name, []).append(r)

    out: Dict[str, str] = {}
    for font_name, candidates in grouped.items():
        preferred = [
            c for c in candidates
            if c.get("model") == preferred_model and (c.get("status") in (None, "ok"))
        ]
        if preferred:
            out[font_name] = preferred[0].get("description", "")
            continue

        ok_any = [c for c in candidates if c.get("status") in (None, "ok") and c.get("description")]
        if ok_any:
            out[font_name] = ok_any[0].get("description", "")

    return out


def build_doc_context(font: Dict[str, Any], vl_desc: str) -> str:
    tags = font.get("tags", [])
    if isinstance(tags, list):
        tags_text = ", ".join(str(t) for t in tags)
    else:
        tags_text = str(tags)

    return (
        f"Name: {font.get('name', '')}. "
        f"Category: {font.get('category', '')}. "
        f"Tags: {tags_text}. "
        f"Description: {vl_desc or font.get('description', '')}"
    )


def load_or_build_text_doc_embeddings(
    doc_names: List[str],
    corpus_map: Dict[str, Dict[str, Any]],
    desc_map: Dict[str, str],
    out_path: Path,
    embed_model: str,
    sleep_sec: float,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    existing: Dict[str, List[float]] = {}

    if out_path.exists():
        for row in load_jsonl(out_path):
            name = row.get("name")
            emb = row.get("embedding")
            if name and isinstance(emb, list):
                existing[name] = emb

    missing = [n for n in doc_names if n not in existing]

    if missing:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY missing and enriched text-doc embedding cache is incomplete."
            )

        for i, name in enumerate(missing, start=1):
            font = corpus_map[name]
            text = build_doc_context(font, desc_map.get(name, ""))
            emb = call_openrouter_embedding(text, api_key, embed_model)
            existing[name] = emb
            print(f"Embedded VL-enriched text doc {i}/{len(missing)}: {name}")
            if sleep_sec > 0:
                time.sleep(sleep_sec)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for name in doc_names:
                f.write(json.dumps({"name": name, "embedding": existing[name]}) + "\n")

    matrix = np.stack([np.array(existing[n], dtype=np.float32) for n in doc_names])
    meta = {
        "cache_path": out_path.as_posix(),
        "cache_hit_count": len(doc_names) - len(missing),
        "cache_miss_count": len(missing),
    }
    return matrix, meta


def load_text_query_embeddings(path: Path, query_ids: List[str]) -> np.ndarray:
    rows = load_jsonl(path)
    qmap = {r.get("id"): r.get("embedding") for r in rows}
    missing = [qid for qid in query_ids if qid not in qmap]
    if missing:
        raise RuntimeError(f"Missing query embeddings for IDs: {missing}")
    return np.stack([np.array(qmap[qid], dtype=np.float32) for qid in query_ids])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P5-03A B2 vs VL-enriched text-only re-evaluation")
    parser.add_argument("--b2-docs", default="research/ab-eval/out/embeddings_vl_docs_b2.npy")
    parser.add_argument("--b2-queries", default="research/ab-eval/out/embeddings_vl_queries.npy")
    parser.add_argument("--text-queries", default="research/ab-eval/out/embeddings_text_queries.jsonl")
    parser.add_argument("--docs-meta", default="research/ab-eval/out/metadata_docs.json")
    parser.add_argument("--queries-meta", default="research/ab-eval/out/metadata_queries.json")
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.200.json")
    parser.add_argument("--labels", default="research/ab-eval/data/labels.medium.human.v1.json")
    parser.add_argument("--ssot", default="research/ab-eval/out/full_set_review_export_1770612809775.json")
    parser.add_argument(
        "--descriptions",
        default="research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl",
    )
    parser.add_argument(
        "--preferred-description-model",
        default="qwen/qwen3-vl-235b-a22b-instruct",
    )
    parser.add_argument("--text-embed-model", default="qwen/qwen3-embedding-8b")
    parser.add_argument(
        "--text-doc-embeddings-out",
        default="research/ab-eval/out/embeddings_text_docs_vl_enriched_p5_03a.jsonl",
    )
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--sleep-sec", type=float, default=0.0)
    parser.add_argument(
        "--comparison-out",
        default="research/ab-eval/out/p5_03a_b2_vs_text_comparison.json",
    )
    parser.add_argument(
        "--gates-out",
        default="research/ab-eval/out/p5_03a_b2_vs_text_gates.json",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    docs_meta = load_json(Path(args.docs_meta))
    queries_meta = load_json(Path(args.queries_meta))
    corpus = load_json(Path(args.corpus))
    labels = load_json(Path(args.labels))
    ssot = load_json(Path(args.ssot))
    desc_rows = load_jsonl(Path(args.descriptions))

    doc_names = [d["name"] for d in docs_meta]
    query_ids = [q["id"] for q in queries_meta]
    corpus_map = {f["name"]: f for f in corpus}

    missing_fonts = [n for n in doc_names if n not in corpus_map]
    if missing_fonts:
        raise RuntimeError(f"Docs meta contains names missing in corpus: {missing_fonts}")

    desc_map = pick_vl_description(desc_rows, args.preferred_description_model)

    # Arm 1: B2 production path
    b2_docs = np.load(args.b2_docs)
    b2_queries = np.load(args.b2_queries)
    if b2_docs.shape[0] != len(doc_names):
        raise RuntimeError(f"B2 docs rows {b2_docs.shape[0]} != doc_names {len(doc_names)}")
    if b2_queries.shape[0] != len(query_ids):
        raise RuntimeError(f"B2 queries rows {b2_queries.shape[0]} != query_ids {len(query_ids)}")

    # Arm 2: text-only with VL-enriched descriptions (no image input)
    text_queries = load_text_query_embeddings(Path(args.text_queries), query_ids)
    text_docs, text_cache_meta = load_or_build_text_doc_embeddings(
        doc_names=doc_names,
        corpus_map=corpus_map,
        desc_map=desc_map,
        out_path=Path(args.text_doc_embeddings_out),
        embed_model=args.text_embed_model,
        sleep_sec=args.sleep_sec,
    )

    b2_scores = cosine_similarity_matrix(b2_queries, b2_docs)
    text_scores = cosine_similarity_matrix(text_queries, text_docs)

    b2_topk = build_topk_map(b2_scores, doc_names, query_ids, args.top_k)
    text_topk = build_topk_map(text_scores, doc_names, query_ids, args.top_k)

    b2_topk_sets = {qid: {n for n, _ in rows} for qid, rows in b2_topk.items()}
    text_topk_sets = {qid: {n for n, _ in rows} for qid, rows in text_topk.items()}

    # Build pair set from amended SSoT (same denominator used in prior gated evaluations)
    pairs: List[Dict[str, Any]] = []
    skipped_pairs = 0
    for d in ssot.get("decisions", []):
        qid = d.get("query_id")
        fname = d.get("font_name")
        if qid not in b2_topk_sets or fname not in corpus_map:
            skipped_pairs += 1
            continue

        human = remap_label(d.get("casey_label", 0))
        pairs.append(
            {
                "query_id": qid,
                "font_name": fname,
                "human": human,
                "text_vl_enriched_pred": 1 if fname in text_topk_sets.get(qid, set()) else 0,
                "b2_production_pred": 1 if fname in b2_topk_sets.get(qid, set()) else 0,
            }
        )

    if not pairs:
        raise RuntimeError("No evaluable SSoT pairs available.")

    baseline_metrics = compute_pair_metrics(pairs, "text_vl_enriched_pred")
    treatment_metrics = compute_pair_metrics(pairs, "b2_production_pred")

    helps: List[Dict[str, Any]] = []
    hurts: List[Dict[str, Any]] = []
    for p in pairs:
        h = p["human"]
        base_ok = p["text_vl_enriched_pred"] == h
        trt_ok = p["b2_production_pred"] == h

        if (not base_ok) and trt_ok:
            helps.append(
                {
                    "query_id": p["query_id"],
                    "font_name": p["font_name"],
                    "human": h,
                    "baseline_pred": p["text_vl_enriched_pred"],
                    "treatment_pred": p["b2_production_pred"],
                }
            )
        elif base_ok and (not trt_ok):
            hurts.append(
                {
                    "query_id": p["query_id"],
                    "font_name": p["font_name"],
                    "human": h,
                    "baseline_pred": p["text_vl_enriched_pred"],
                    "treatment_pred": p["b2_production_pred"],
                }
            )

    delta = {
        "agreement": round(treatment_metrics["agreement"] - baseline_metrics["agreement"], 4),
        "precision": round(treatment_metrics["precision"] - baseline_metrics["precision"], 4),
        "recall": round(treatment_metrics["recall"] - baseline_metrics["recall"], 4),
        "f1": round(treatment_metrics["f1"] - baseline_metrics["f1"], 4),
    }

    retrieval = {
        "text_vl_enriched": compute_retrieval_metrics(text_scores, doc_names, query_ids, labels),
        "b2_production": compute_retrieval_metrics(b2_scores, doc_names, query_ids, labels),
    }

    comparison = {
        "metadata": {
            "run_id": "p5_03a_b2_vs_text",
            "variant_id": "p5_03a_vl_reeval",
            "baseline": "text_vl_enriched",
            "treatment": "b2_production",
            "seed": args.seed,
            "repeats": args.repeats,
            "top_k": args.top_k,
            "label_policy": "2->0",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "description_artifact": args.descriptions,
            "preferred_description_model": args.preferred_description_model,
            "text_embedding_model": args.text_embed_model,
            "text_doc_embedding_cache": text_cache_meta,
            "pair_set": "full_set_review_export_1770612809775.json decisions",
            "pair_count": len(pairs),
            "skipped_pairs": skipped_pairs,
            "governance_semantics_changed": False,
        },
        "variants": {
            # Canonical names used in this P5-03A run.
            "text_vl_enriched": baseline_metrics,
            "b2_production": treatment_metrics,
            # Compatibility aliases for existing gate-validation flow.
            "A": baseline_metrics,
            "B2": treatment_metrics,
        },
        "delta_treatment_minus_baseline": delta,
        "retrieval_metrics": retrieval,
        "helps_hurts": {
            "helps_count": len(helps),
            "hurts_count": len(hurts),
            "net": len(helps) - len(hurts),
        },
        "helps": helps,
        "hurts": hurts,
    }

    gates = {
        "G1 (Agreement Delta)": {
            "status": "PASS" if delta["agreement"] >= 0.01 else "FAIL",
            "value": delta["agreement"],
            "threshold": ">= 0.01",
        },
        "G2 (Precision Delta)": {
            "status": "PASS" if delta["precision"] >= -0.02 else "FAIL",
            "value": delta["precision"],
            "threshold": ">= -0.02",
        },
        "G3 (Helps/Hurts Net)": {
            "status": "PASS" if (len(helps) - len(hurts)) > 0 else "FAIL",
            "value": len(helps) - len(hurts),
            "threshold": "> 0",
        },
        "G4 (Visual QA)": {
            "status": "PENDING",
            "value": "Manual",
            "threshold": "Zero clipping/overlap",
        },
    }

    success = all(g["status"] == "PASS" for g in gates.values())
    gates_out = {
        "success": success,
        "summary": "GO" if success else "NO-GO",
        "gates": gates,
        "metadata": {
            "run_id": comparison["metadata"]["run_id"],
            "variant_id": comparison["metadata"]["variant_id"],
            "baseline": comparison["metadata"]["baseline"],
            "treatment": comparison["metadata"]["treatment"],
            "seed": comparison["metadata"]["seed"],
            "repeats": comparison["metadata"]["repeats"],
            "governance_semantics_changed": False,
        },
    }

    comparison_path = Path(args.comparison_out)
    gates_path = Path(args.gates_out)
    comparison_path.parent.mkdir(parents=True, exist_ok=True)
    gates_path.parent.mkdir(parents=True, exist_ok=True)

    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)

    with open(gates_path, "w", encoding="utf-8") as f:
        json.dump(gates_out, f, indent=2)

    print("P5-03A run complete")
    print(f"Saved comparison: {comparison_path}")
    print(f"Saved gates: {gates_path}")
    print(f"Pair count: {len(pairs)} (skipped: {skipped_pairs})")
    print(f"Deltas: agreement={delta['agreement']:+.4f}, precision={delta['precision']:+.4f}")
    print(f"Helps/Hurts/Net: {len(helps)}/{len(hurts)}/{len(helps)-len(hurts)}")
    print(f"Summary: {'GO' if success else 'NO-GO'}")


if __name__ == "__main__":
    main()
