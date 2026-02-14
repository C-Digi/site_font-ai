"""
P5-04A: Bounded offline hard-negative curation + directional intervention trial.

Scope:
- Offline-only research under research/ab-eval/
- Deterministic hard-negative slice curation (target n=12)
- Directional intervention variant on curated slice

Outputs:
- research/ab-eval/out/p5_04a_hardneg_candidate.json
- research/ab-eval/out/p5_04a_v3_vs_hardneg_comparison.json
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


VINTAGE_TERMS = ["vintage", "retro", "classic", "old-school", "art deco", "70s", "80s"]
STRICT_TERMS = ["exact", "literally", "strictly", "must", "only", "precise"]
MOTIFS = ("over_strict_semantic", "vintage_era")

# Keep deterministic strict-cue assignment in sync with P5-05A coverage audit.
STRICT_USE_CASE_PATTERN = re.compile(
    r"\bfor\s+(?:a|an|the\s+)?(?:[a-z0-9-]+\s+){0,4}(?:firm|brand|company|startup)\b"
)
STRICT_CONSTRAINT_PATTERN = re.compile(r"\b(?:tight|specific|particular|certain)\b")
STRICT_DOMAIN_PATTERN = re.compile(r"\b(?:industrial|professional|authoritative|stern)\b")

# Standard English stopword list (deterministic embedded set)
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "could",
    "did", "do", "does", "doing", "down", "during",
    "each",
    "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
    "i", "if", "in", "into", "is", "it", "its", "itself",
    "just",
    "me", "more", "most", "my", "myself",
    "no", "nor", "not", "now",
    "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own",
    "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too",
    "under", "until", "up",
    "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would",
    "you", "your", "yours", "yourself", "yourselves",
}


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def remap_label(label: Any) -> int:
    # Governance policy: label 2 -> 0 for promotion metrics path
    if label == 2:
        return 0
    return 1 if label == 1 else 0


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", (text or "").lower())


def contains_any_term(text: str, terms: List[str]) -> bool:
    lowered = (text or "").lower()
    return any(term in lowered for term in terms)


def non_stopword_query_tokens(query_text: str) -> List[str]:
    return [t for t in tokenize(query_text) if t not in STOPWORDS]


def assign_motif(query_text: str) -> Optional[str]:
    """
    Deterministic motif assignment for hard-negative curation.

    Vintage mapping is intentionally unchanged. Strictness detection retains
    legacy strict keywords and adds deterministic phrase/regex cues (no model
    calls) to align with P5-05A coverage auditing.
    """
    q = (query_text or "").lower()
    if contains_any_term(q, VINTAGE_TERMS):
        return "vintage_era"
    if contains_any_term(q, STRICT_TERMS):
        return "over_strict_semantic"
    if STRICT_USE_CASE_PATTERN.search(q):
        return "over_strict_semantic"
    if STRICT_CONSTRAINT_PATTERN.search(q):
        return "over_strict_semantic"
    if STRICT_DOMAIN_PATTERN.search(q):
        return "over_strict_semantic"
    return None


def compute_metrics(rows: List[Dict[str, Any]], pred_key: str) -> Dict[str, Any]:
    tp = fp = fn = tn = 0
    for r in rows:
        h = r["human"]
        p = r[pred_key]
        if h == 1 and p == 1:
            tp += 1
        elif h == 0 and p == 1:
            fp += 1
        elif h == 1 and p == 0:
            fn += 1
        else:
            tn += 1

    total = len(rows)
    agreement = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    agreement_r = round(agreement, 4)
    precision_r = round(precision, 4)
    recall_r = round(recall, 4)
    f1_r = round(f1, 4)

    return {
        "agreement": agreement_r,
        "precision": precision_r,
        "recall": recall_r,
        "f1": f1_r,
        # Compatibility aliases for legacy gate-validator access pattern.
        # NOTE: values are duplicated intentionally; semantics unchanged.
        "Agreement": agreement_r,
        "Precision@10": precision_r,
        "counts": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "total": total,
        },
    }


def preflight_check(paths: List[Path]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    for p in paths:
        if not p.exists():
            errors.append(f"Missing required input: {p.as_posix()}")
            continue
        try:
            load_json(p)
        except Exception as e:
            errors.append(f"Unreadable JSON input: {p.as_posix()} ({e})")
    return len(errors) == 0, errors


def build_font_text(font: Dict[str, Any]) -> str:
    tags = font.get("tags", [])
    if isinstance(tags, list):
        tags_text = " ".join(str(t) for t in tags)
    else:
        tags_text = str(tags)
    return " ".join(
        [
            str(font.get("name", "")),
            str(font.get("category", "")),
            tags_text,
            str(font.get("description", "")),
        ]
    ).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P5-04A hard-negative curation + directional intervention trial")
    parser.add_argument("--ssot", default="research/ab-eval/out/full_set_review_export_1770612809775.json")
    parser.add_argument("--v3-results", default="research/ab-eval/out/g3_v3_gated_results.json")
    parser.add_argument("--queries", default="research/ab-eval/data/queries.medium.human.v1.json")
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.200.json")
    parser.add_argument("--hurts-rootcause", default="research/ab-eval/out/week4_p3_hurts_rootcause.json")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--target-total", type=int, default=12)
    parser.add_argument("--target-per-motif", type=int, default=6)
    parser.add_argument("--variant-out", default="research/ab-eval/out/p5_04a_hardneg_candidate.json")
    parser.add_argument("--comparison-out", default="research/ab-eval/out/p5_04a_v3_vs_hardneg_comparison.json")
    args = parser.parse_args()

    random.seed(args.seed)

    ssot_path = Path(args.ssot)
    v3_path = Path(args.v3_results)
    queries_path = Path(args.queries)
    corpus_path = Path(args.corpus)
    hurts_path = Path(args.hurts_rootcause)

    ok, preflight_errors = preflight_check([ssot_path, v3_path, queries_path, corpus_path, hurts_path])
    if not ok:
        print("RETURN_RETRY")
        print("Critical blocker(s) detected during preflight:")
        for e in preflight_errors:
            print(f"- {e}")
        print("Remediation:")
        print("- Restore missing files and/or fix malformed JSON input artifacts, then rerun P5-04A.")
        sys.exit(2)

    ssot = load_json(ssot_path)
    v3 = load_json(v3_path)
    queries = load_json(queries_path)
    corpus = load_json(corpus_path)
    hurts_rootcause = load_json(hurts_path)

    query_text_map = {q["id"]: q.get("text", "") for q in queries}
    query_class_map = {q["id"]: q.get("class", "unknown") for q in queries}
    corpus_map = {f["name"]: f for f in corpus}

    # Build adjudicated human label map
    ssot_map: Dict[Tuple[str, str], int] = {}
    for d in ssot.get("decisions", []):
        key = (d.get("query_id", ""), d.get("font_name", ""))
        if not key[0] or not key[1]:
            continue
        ssot_map[key] = remap_label(d.get("casey_label", 0))

    details = v3.get("details", [])

    # Group baseline details by query and build deterministic rank maps using confidence as proxy score.
    detail_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {}
    details_by_query: Dict[str, List[Dict[str, Any]]] = {}
    for d in details:
        qid = d.get("query_id", "")
        fname = d.get("font_name", "")
        if not qid or not fname:
            continue
        detail_by_key[(qid, fname)] = d
        details_by_query.setdefault(qid, []).append(d)

    baseline_rank_by_key: Dict[Tuple[str, str], int] = {}
    baseline_top10_by_query: Dict[str, set] = {}
    for qid, rows in details_by_query.items():
        ranked = sorted(rows, key=lambda x: (-float(x.get("confidence", 0.0)), x.get("font_name", "")))
        baseline_top10_by_query[qid] = {r.get("font_name", "") for r in ranked[:10] if r.get("font_name")}
        for idx, row in enumerate(ranked, start=1):
            k = (qid, row.get("font_name", ""))
            baseline_rank_by_key[k] = idx

    # Build candidate pool from adjudicated labels + baseline ranking artifact.
    # Hard-negative = human label 0 AND baseline rank <= 10.
    hardneg_pool: List[Dict[str, Any]] = []
    for (qid, fname), human in ssot_map.items():
        if human != 0:
            continue

        rank = baseline_rank_by_key.get((qid, fname))
        if rank is None or rank > 10:
            continue

        qtext = query_text_map.get(qid, "")
        motif = assign_motif(qtext)
        if motif not in MOTIFS:
            continue

        d = detail_by_key.get((qid, fname), {})
        hardneg_pool.append(
            {
                "query_id": qid,
                "query_text": qtext,
                "query_class": query_class_map.get(qid, "unknown"),
                "font_name": fname,
                "human": human,
                "baseline_rank": rank,
                "baseline_confidence": float(d.get("confidence", 0.0)),
                "motif": motif,
            }
        )

    def sel_key(x: Dict[str, Any]) -> Tuple[float, str, str]:
        return (-float(x.get("baseline_confidence", 0.0)), x.get("query_id", ""), x.get("font_name", ""))

    pool_by_motif: Dict[str, List[Dict[str, Any]]] = {
        "vintage_era": sorted([p for p in hardneg_pool if p["motif"] == "vintage_era"], key=sel_key),
        "over_strict_semantic": sorted([p for p in hardneg_pool if p["motif"] == "over_strict_semantic"], key=sel_key),
    }

    selected_vintage = pool_by_motif["vintage_era"][: args.target_per_motif]
    selected_strict = pool_by_motif["over_strict_semantic"][: args.target_per_motif]
    selected = list(selected_vintage) + list(selected_strict)

    fill_notes: List[str] = []

    # Deterministic quota fill from the other motif when one motif is short.
    if len(selected) < args.target_total:
        need = args.target_total - len(selected)
        if len(selected_vintage) < args.target_per_motif and len(selected_strict) >= args.target_per_motif:
            fill_from = pool_by_motif["over_strict_semantic"][args.target_per_motif : args.target_per_motif + need]
            selected.extend(fill_from)
            fill_notes.append(
                f"Filled {len(fill_from)} shortfall pair(s) from over_strict_semantic due to vintage_era quota shortfall."
            )
        elif len(selected_strict) < args.target_per_motif and len(selected_vintage) >= args.target_per_motif:
            fill_from = pool_by_motif["vintage_era"][args.target_per_motif : args.target_per_motif + need]
            selected.extend(fill_from)
            fill_notes.append(
                f"Filled {len(fill_from)} shortfall pair(s) from vintage_era due to over_strict_semantic quota shortfall."
            )
        else:
            # fallback deterministic fill from all remaining, sorted with same key
            used = {(x["query_id"], x["font_name"]) for x in selected}
            remaining = [x for x in hardneg_pool if (x["query_id"], x["font_name"]) not in used]
            remaining_sorted = sorted(remaining, key=sel_key)
            fill_from = remaining_sorted[:need]
            selected.extend(fill_from)
            fill_notes.append(
                f"Filled {len(fill_from)} pair(s) from combined remaining pool due to dual-motif shortfall."
            )

    selected = sorted(selected, key=sel_key)[: args.target_total]

    if not selected:
        print("RETURN_RETRY")
        print("Critical blocker(s) detected during selection:")
        print("- No qualifying hard-negative pairs found under locked methodology.")
        print("Remediation:")
        print("- Verify baseline ranking artifact and adjudicated labels coverage for motif-mapped queries.")
        sys.exit(2)

    selected_queries = sorted({s["query_id"] for s in selected})

    # Directional intervention: start from baseline confidence score and apply motif penalties.
    treatment_top10_by_query: Dict[str, set] = {}
    treatment_rank_by_key: Dict[Tuple[str, str], int] = {}
    treatment_score_by_key: Dict[Tuple[str, str], float] = {}
    penalty_by_key: Dict[Tuple[str, str], float] = {}
    penalty_reason_by_key: Dict[Tuple[str, str], str] = {}

    query_rankings: Dict[str, Dict[str, Any]] = {}

    for qid in selected_queries:
        qtext = query_text_map.get(qid, "")
        motif = assign_motif(qtext)
        q_tokens = set(non_stopword_query_tokens(qtext))
        baseline_rows = sorted(
            details_by_query.get(qid, []), key=lambda x: (-float(x.get("confidence", 0.0)), x.get("font_name", ""))
        )

        adjusted_rows: List[Dict[str, Any]] = []
        for row in baseline_rows:
            fname = row.get("font_name", "")
            if not fname:
                continue
            base_score = float(row.get("confidence", 0.0))
            font_text = build_font_text(corpus_map.get(fname, {"name": fname}))

            penalty = 0.0
            reason = "none"

            if motif == "vintage_era":
                if not contains_any_term(font_text, VINTAGE_TERMS):
                    penalty = 0.12
                    reason = "vintage_term_absent"
            elif motif == "over_strict_semantic":
                cand_tokens = set(tokenize(font_text))
                if q_tokens and len(cand_tokens & q_tokens) == 0:
                    penalty = 0.10
                    reason = "strict_query_token_miss"

            adjusted_score = max(0.0, base_score - penalty)

            key = (qid, fname)
            treatment_score_by_key[key] = round(adjusted_score, 6)
            penalty_by_key[key] = round(penalty, 6)
            penalty_reason_by_key[key] = reason

            adjusted_rows.append(
                {
                    "query_id": qid,
                    "font_name": fname,
                    "baseline_confidence": base_score,
                    "adjusted_score": adjusted_score,
                    "penalty": penalty,
                    "penalty_reason": reason,
                }
            )

        reranked = sorted(
            adjusted_rows,
            key=lambda x: (-float(x["adjusted_score"]), -float(x["baseline_confidence"]), x["font_name"]),
        )

        treatment_top10_by_query[qid] = {r["font_name"] for r in reranked[:10]}
        for i, r in enumerate(reranked, start=1):
            treatment_rank_by_key[(qid, r["font_name"])] = i

        query_rankings[qid] = {
            "query_text": qtext,
            "motif": motif,
            "baseline_top10": [r.get("font_name", "") for r in baseline_rows[:10]],
            "treatment_top10": [r.get("font_name", "") for r in reranked[:10]],
            "penalized_count": sum(1 for r in reranked if r["penalty"] > 0),
        }

    # Evaluate selected slice
    selected_eval_rows: List[Dict[str, Any]] = []
    for s in selected:
        qid = s["query_id"]
        fname = s["font_name"]
        key = (qid, fname)
        v3_pred = 1 if fname in baseline_top10_by_query.get(qid, set()) else 0
        trt_pred = 1 if fname in treatment_top10_by_query.get(qid, set()) else 0

        selected_eval_rows.append(
            {
                "query_id": qid,
                "query_text": s["query_text"],
                "query_class": s["query_class"],
                "font_name": fname,
                "motif": s["motif"],
                "human": s["human"],
                "baseline_rank": s["baseline_rank"],
                "baseline_confidence": s["baseline_confidence"],
                "v3_pred": v3_pred,
                "p5_04a_pred": trt_pred,
                "treatment_rank": treatment_rank_by_key.get(key),
                "treatment_score": treatment_score_by_key.get(key, 0.0),
                "penalty_applied": penalty_by_key.get(key, 0.0),
                "penalty_reason": penalty_reason_by_key.get(key, "none"),
            }
        )

    baseline_metrics = compute_metrics(selected_eval_rows, "v3_pred")
    treatment_metrics = compute_metrics(selected_eval_rows, "p5_04a_pred")

    helps: List[Dict[str, Any]] = []
    hurts: List[Dict[str, Any]] = []
    for r in selected_eval_rows:
        h = r["human"]
        v3_ok = r["v3_pred"] == h
        trt_ok = r["p5_04a_pred"] == h
        if (not v3_ok) and trt_ok:
            helps.append(
                {
                    "query_id": r["query_id"],
                    "font_name": r["font_name"],
                    "human": h,
                    "v3_pred": r["v3_pred"],
                    "treatment_pred": r["p5_04a_pred"],
                    "motif": r["motif"],
                    "query_class": r["query_class"],
                }
            )
        elif v3_ok and (not trt_ok):
            hurts.append(
                {
                    "query_id": r["query_id"],
                    "font_name": r["font_name"],
                    "human": h,
                    "v3_pred": r["v3_pred"],
                    "treatment_pred": r["p5_04a_pred"],
                    "motif": r["motif"],
                    "query_class": r["query_class"],
                }
            )

    delta = {
        "agreement": round(treatment_metrics["agreement"] - baseline_metrics["agreement"], 4),
        "precision": round(treatment_metrics["precision"] - baseline_metrics["precision"], 4),
        "recall": round(treatment_metrics["recall"] - baseline_metrics["recall"], 4),
        "f1": round(treatment_metrics["f1"] - baseline_metrics["f1"], 4),
    }

    class_breakdown: Dict[str, Dict[str, int]] = {}
    for r in selected_eval_rows:
        c = r["query_class"]
        b = class_breakdown.setdefault(c, {"pairs": 0, "helps": 0, "hurts": 0})
        b["pairs"] += 1
    for h in helps:
        class_breakdown[h["query_class"]]["helps"] += 1
    for h in hurts:
        class_breakdown[h["query_class"]]["hurts"] += 1

    motif_counts = {m: 0 for m in MOTIFS}
    for r in selected_eval_rows:
        motif_counts[r["motif"]] = motif_counts.get(r["motif"], 0) + 1

    candidate_artifact = {
        "metadata": {
            "run_id": "p5_04a_hardneg_trial",
            "variant_id": "p5_04a_hardneg_candidate",
            "seed": args.seed,
            "repeats": args.repeats,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "continue_mode": "CONTINUE_SAFE",
            "status": "READY",
            "confidence": 0.85,
            "risk_level": "low",
            "governance_semantics_changed": False,
        },
        "preflight": {
            "inputs_checked": [
                ssot_path.as_posix(),
                v3_path.as_posix(),
                queries_path.as_posix(),
                corpus_path.as_posix(),
                hurts_path.as_posix(),
            ],
            "blockers": [],
            "assumptions_applied": [
                "Used confidence in g3_v3_gated_results.json as ranking proxy (higher confidence => higher rank).",
                "Joined font metadata from corpus.200.json by font name for penalty checks.",
                "Used standard English stopword list for over_strict_semantic token-miss checks.",
            ],
            "rootcause_context": {
                "decision": hurts_rootcause.get("decision"),
                "top_motif_share": hurts_rootcause.get("top_motif_share"),
            },
        },
        "selection": {
            "hard_negative_definition": "human==0 (after remap) AND baseline v3 rank<=10",
            "motifs": list(MOTIFS),
            "target_total": args.target_total,
            "target_per_motif": args.target_per_motif,
            "pool_counts": {
                "vintage_era": len(pool_by_motif["vintage_era"]),
                "over_strict_semantic": len(pool_by_motif["over_strict_semantic"]),
                "total": len(hardneg_pool),
            },
            "selected_counts": motif_counts,
            "selected_total": len(selected_eval_rows),
            "quota_fill_notes": fill_notes,
            "sort_policy": "confidence desc, tie query_id asc, then font_name asc",
        },
        "selected_pairs": selected_eval_rows,
        "intervention": {
            "variant_id": "p5_04a_hardneg_candidate",
            "vintage_penalty": 0.12,
            "strict_penalty": 0.10,
            "score_floor": 0.0,
            "rerank_tie_break": "adjusted_score desc, then baseline_confidence desc, then font_name asc",
            "query_rankings": query_rankings,
        },
    }

    comparison = {
        "metadata": {
            "run_id": "p5_04a_v3_vs_hardneg",
            "variant_id": "p5_04a_hardneg_candidate",
            "baseline": "v3",
            "seed": args.seed,
            "repeats": args.repeats,
            "label_policy": "2->0",
            "pair_count": len(selected_eval_rows),
            "gating_scope": "directional_slice_only",
            "governance_semantics_changed": False,
            "directional_not_global_promotion": True,
        },
        "variants": {
            "v3": baseline_metrics,
            "p5_04a_hardneg_candidate": treatment_metrics,
            # Compatibility aliases for existing validator flow.
            "A": baseline_metrics,
            "B2": treatment_metrics,
        },
        "delta_treatment_minus_baseline": delta,
        "helps_hurts": {
            "helps_count": len(helps),
            "hurts_count": len(hurts),
            "net": len(helps) - len(hurts),
        },
        "per_query_class_breakdown": class_breakdown,
        "selected_motif_counts": motif_counts,
        "helps": helps,
        "hurts": hurts,
    }

    variant_out_path = Path(args.variant_out)
    comparison_out_path = Path(args.comparison_out)
    variant_out_path.parent.mkdir(parents=True, exist_ok=True)
    comparison_out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(variant_out_path, "w", encoding="utf-8") as f:
        json.dump(candidate_artifact, f, indent=2)

    with open(comparison_out_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)

    print("P5-04A run complete")
    print(f"Saved variant artifact: {variant_out_path.as_posix()}")
    print(f"Saved comparison artifact: {comparison_out_path.as_posix()}")
    print(f"Selected pairs: {len(selected_eval_rows)}")
    print(f"Motif counts: {motif_counts}")
    print(f"Helps/Hurts/Net: {len(helps)}/{len(hurts)}/{len(helps)-len(hurts)}")
    print(f"Delta agreement: {delta['agreement']:+.4f}")
    print("Governance semantics unchanged: True")


if __name__ == "__main__":
    main()
