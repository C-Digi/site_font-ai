"""
P5-05A: Deterministic pre-trial coverage-sufficiency audit.

Purpose:
- Gate directional slice trials before intervention execution.
- Provide a signal-quality readiness decision for curated hard-negative slices.

Required outputs:
- research/ab-eval/out/p5_05a_coverage_audit.json
- research/ab-eval/REPORT_P5_05A_COVERAGE_AUDIT.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


VINTAGE_TERMS = ["vintage", "retro", "classic", "old-school", "art deco", "70s", "80s"]
STRICT_TERMS = ["exact", "literally", "strictly", "must", "only", "precise"]
DEFAULT_TARGETED_MOTIFS = ("over_strict_semantic", "vintage_era")

# Deterministic embedded stopword set (matches prior directional tooling behavior)
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
    # Governance alignment: label 2 -> 0 in promotion-metric paths.
    if label == 2:
        return 0
    return 1 if label == 1 else 0


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", (text or "").lower())


def contains_any_term(text: str, terms: List[str]) -> bool:
    lowered = (text or "").lower()
    return any(term in lowered for term in terms)


def assign_motif(query_text: str) -> Optional[str]:
    q = (query_text or "").lower()
    if contains_any_term(q, VINTAGE_TERMS):
        return "vintage_era"
    if contains_any_term(q, STRICT_TERMS):
        return "over_strict_semantic"
    return None


def non_stopword_query_tokens(query_text: str) -> List[str]:
    return [t for t in tokenize(query_text) if t not in STOPWORDS]


def build_font_text(font: Dict[str, Any]) -> str:
    tags = font.get("tags", [])
    tags_text = " ".join(str(t) for t in tags) if isinstance(tags, list) else str(tags)
    return " ".join(
        [
            str(font.get("name", "")),
            str(font.get("category", "")),
            tags_text,
            str(font.get("description", "")),
        ]
    ).strip()


def preflight_check(paths: List[Path]) -> Tuple[bool, List[str]]:
    blockers: List[str] = []
    for p in paths:
        if not p.exists():
            blockers.append(f"Missing required input: {p.as_posix()}")
            continue
        try:
            load_json(p)
        except Exception as e:  # pragma: no cover - defensive parse guard
            blockers.append(f"Unreadable JSON input: {p.as_posix()} ({e})")
    return len(blockers) == 0, blockers


def deterministic_pair_key(row: Dict[str, Any]) -> Tuple[str, str]:
    return (str(row.get("query_id", "")), str(row.get("font_name", "")))


def should_penalty_apply(motif: str, query_text: str, font_text: str) -> Tuple[bool, float, str]:
    if motif == "vintage_era":
        applies = not contains_any_term(font_text, VINTAGE_TERMS)
        return applies, 0.12 if applies else 0.0, "vintage_term_absent" if applies else "none"

    if motif == "over_strict_semantic":
        q_tokens = set(non_stopword_query_tokens(query_text))
        c_tokens = set(tokenize(font_text))
        applies = bool(q_tokens) and len(q_tokens & c_tokens) == 0
        return applies, 0.10 if applies else 0.0, "strict_query_token_miss" if applies else "none"

    return False, 0.0, "unmapped_motif"


def write_report(path: Path, report_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P5-05A pre-trial coverage-sufficiency audit")
    parser.add_argument("--candidate", default="research/ab-eval/out/p5_04a_hardneg_candidate.json")
    parser.add_argument("--v3-results", default="research/ab-eval/out/g3_v3_gated_results.json")
    parser.add_argument("--ssot", default="research/ab-eval/out/full_set_review_export_1770612809775.json")
    parser.add_argument("--queries", default="research/ab-eval/data/queries.medium.human.v1.json")
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.200.json")
    parser.add_argument("--motif-min", type=int, default=3)
    parser.add_argument("--sample-floor", type=int, default=10)
    parser.add_argument("--min-penalty-applicability-share", type=float, default=0.10)
    parser.add_argument("--min-rank-shift-opportunities", type=int, default=1)
    parser.add_argument("--out", default="research/ab-eval/out/p5_05a_coverage_audit.json")
    parser.add_argument("--report-out", default="research/ab-eval/REPORT_P5_05A_COVERAGE_AUDIT.md")
    args = parser.parse_args()

    candidate_path = Path(args.candidate)
    v3_path = Path(args.v3_results)
    ssot_path = Path(args.ssot)
    queries_path = Path(args.queries)
    corpus_path = Path(args.corpus)
    out_path = Path(args.out)
    report_path = Path(args.report_out)

    required_inputs = [candidate_path, v3_path, ssot_path, queries_path, corpus_path]
    preflight_ok, blockers = preflight_check(required_inputs)

    if not preflight_ok:
        print("RETURN_RETRY")
        print("Critical blocker(s) detected during preflight:")
        for b in blockers:
            print(f"- {b}")
        print("Remediation:")
        print("- Restore missing input files and/or repair malformed JSON artifacts.")
        print("- Re-run this audit after preflight reads succeed for all required inputs.")
        sys.exit(2)

    candidate = load_json(candidate_path)
    v3 = load_json(v3_path)
    ssot = load_json(ssot_path)
    queries = load_json(queries_path)
    corpus = load_json(corpus_path)

    query_text_map = {q.get("id", ""): q.get("text", "") for q in queries}
    corpus_map = {f.get("name", ""): f for f in corpus}

    ssot_map: Dict[Tuple[str, str], int] = {}
    for d in ssot.get("decisions", []):
        qid = d.get("query_id", "")
        fname = d.get("font_name", "")
        if qid and fname:
            ssot_map[(qid, fname)] = remap_label(d.get("casey_label", 0))

    details_by_query: Dict[str, List[Dict[str, Any]]] = {}
    confidence_by_key: Dict[Tuple[str, str], float] = {}
    rank_by_key: Dict[Tuple[str, str], int] = {}

    for row in v3.get("details", []):
        qid = row.get("query_id", "")
        fname = row.get("font_name", "")
        if not qid or not fname:
            continue
        details_by_query.setdefault(qid, []).append(row)

    for qid, rows in details_by_query.items():
        ranked = sorted(rows, key=lambda x: (-float(x.get("confidence", 0.0)), str(x.get("font_name", ""))))
        for idx, row in enumerate(ranked, start=1):
            fname = str(row.get("font_name", ""))
            key = (qid, fname)
            confidence_by_key[key] = float(row.get("confidence", 0.0))
            rank_by_key[key] = idx

    targeted_motifs_raw = candidate.get("selection", {}).get("motifs")
    if isinstance(targeted_motifs_raw, list) and targeted_motifs_raw:
        targeted_motifs = sorted(str(m) for m in targeted_motifs_raw)
    else:
        targeted_motifs = sorted(DEFAULT_TARGETED_MOTIFS)

    curated_pairs_raw = candidate.get("selected_pairs", [])
    curated_pairs: List[Dict[str, Any]] = []
    for r in curated_pairs_raw:
        qid = str(r.get("query_id", ""))
        fname = str(r.get("font_name", ""))
        if not qid or not fname:
            continue

        key = (qid, fname)
        query_text = str(r.get("query_text", query_text_map.get(qid, "")))
        motif = str(r.get("motif", assign_motif(query_text) or "unmapped"))

        baseline_conf = float(r.get("baseline_confidence", confidence_by_key.get(key, 0.0)))
        baseline_rank = int(r.get("baseline_rank", rank_by_key.get(key, 10_000)))

        if "human" in r:
            human = remap_label(r.get("human"))
        else:
            human = ssot_map.get(key, 0)

        curated_pairs.append(
            {
                "query_id": qid,
                "font_name": fname,
                "query_text": query_text,
                "motif": motif,
                "human": human,
                "baseline_confidence": baseline_conf,
                "baseline_rank": baseline_rank,
            }
        )

    curated_pairs = sorted(curated_pairs, key=deterministic_pair_key)

    if not curated_pairs:
        print("RETURN_RETRY")
        print("Critical blocker(s) detected during audit setup:")
        print("- No curated pairs found in candidate artifact selected_pairs.")
        print("Remediation:")
        print("- Regenerate candidate curation artifact and ensure selected_pairs is populated.")
        sys.exit(2)

    # Check 1: motif_coverage
    motif_counts = {m: 0 for m in targeted_motifs}
    for row in curated_pairs:
        if row["motif"] in motif_counts:
            motif_counts[row["motif"]] += 1

    motif_deficits = [
        {"motif": m, "required_min": args.motif_min, "actual": motif_counts.get(m, 0)}
        for m in targeted_motifs
        if motif_counts.get(m, 0) < args.motif_min
    ]
    motif_coverage_pass = len(motif_deficits) == 0

    # Check 2: sample_floor
    total_pairs = len(curated_pairs)
    sample_floor_pass = total_pairs >= args.sample_floor

    # Check 3: penalty_applicability
    applicability_rows: List[Dict[str, Any]] = []
    applicable_count = 0
    applicable_by_motif: Dict[str, int] = {m: 0 for m in targeted_motifs}

    for row in curated_pairs:
        qid = row["query_id"]
        fname = row["font_name"]
        motif = row["motif"]
        query_text = row["query_text"]

        font_text = build_font_text(corpus_map.get(fname, {"name": fname}))
        applies, penalty, reason = should_penalty_apply(motif, query_text, font_text)
        if applies:
            applicable_count += 1
            if motif in applicable_by_motif:
                applicable_by_motif[motif] += 1

        applicability_rows.append(
            {
                "query_id": qid,
                "font_name": fname,
                "motif": motif,
                "penalty_can_trigger": applies,
                "penalty_amount": round(penalty, 6),
                "penalty_reason": reason,
            }
        )

    applicability_rows = sorted(applicability_rows, key=deterministic_pair_key)
    penalty_applicability_share = (applicable_count / total_pairs) if total_pairs else 0.0
    penalty_applicability_pass = penalty_applicability_share >= args.min_penalty_applicability_share

    # Check 4: rank_shift_opportunity (analyze ranks 8-12 where available)
    selected_query_ids = sorted({r["query_id"] for r in curated_pairs})
    boundary_windows_analyzed = 0
    estimated_flip_opportunities = 0
    query_opportunity_rows: List[Dict[str, Any]] = []
    margins: List[float] = []

    for qid in selected_query_ids:
        rows = sorted(
            details_by_query.get(qid, []),
            key=lambda x: (-float(x.get("confidence", 0.0)), str(x.get("font_name", ""))),
        )
        if len(rows) < 10:
            query_opportunity_rows.append(
                {
                    "query_id": qid,
                    "window_available": False,
                    "reason": "fewer_than_10_baseline_rows",
                    "window_ranks_8_12": [],
                    "boundary_margin_rank10_minus_rank11": None,
                    "estimated_boundary_flip_count": 0,
                }
            )
            continue

        window_rows = rows[7:12]  # ranks 8..12 (1-indexed)
        window_available = len(window_rows) > 0
        if window_available:
            boundary_windows_analyzed += 1

        s10 = float(rows[9].get("confidence", 0.0)) if len(rows) >= 10 else None
        s11 = float(rows[10].get("confidence", 0.0)) if len(rows) >= 11 else None
        boundary_margin = (s10 - s11) if (s10 is not None and s11 is not None) else None
        if boundary_margin is not None:
            margins.append(boundary_margin)

        query_text = query_text_map.get(qid, "")
        motif = assign_motif(query_text) or "unmapped"

        query_flip_count = 0
        window_debug: List[Dict[str, Any]] = []
        for idx, w in enumerate(window_rows, start=8):
            fname = str(w.get("font_name", ""))
            score = float(w.get("confidence", 0.0))
            font_text = build_font_text(corpus_map.get(fname, {"name": fname}))
            applies, penalty, reason = should_penalty_apply(motif, query_text, font_text)

            margin_to_rank11 = None
            potential_flip = False
            if idx <= 10 and s11 is not None:
                margin_to_rank11 = max(0.0, score - s11)
                potential_flip = applies and (penalty >= margin_to_rank11)
                if potential_flip:
                    query_flip_count += 1

            window_debug.append(
                {
                    "rank": idx,
                    "font_name": fname,
                    "baseline_score": round(score, 6),
                    "motif": motif,
                    "penalty_can_trigger": applies,
                    "penalty_amount": round(penalty, 6),
                    "penalty_reason": reason,
                    "margin_to_rank11": round(margin_to_rank11, 6) if margin_to_rank11 is not None else None,
                    "potential_boundary_flip": potential_flip,
                }
            )

        estimated_flip_opportunities += query_flip_count
        query_opportunity_rows.append(
            {
                "query_id": qid,
                "window_available": window_available,
                "reason": "ok",
                "window_ranks_8_12": window_debug,
                "boundary_margin_rank10_minus_rank11": round(boundary_margin, 6) if boundary_margin is not None else None,
                "estimated_boundary_flip_count": query_flip_count,
            }
        )

    query_opportunity_rows = sorted(query_opportunity_rows, key=lambda x: str(x.get("query_id", "")))
    rank_shift_opportunity_pass = estimated_flip_opportunities >= args.min_rank_shift_opportunities

    checks = {
        "motif_coverage": {
            "status": "PASS" if motif_coverage_pass else "FAIL",
            "required_min_pairs_per_targeted_motif": args.motif_min,
            "targeted_motifs": targeted_motifs,
            "counts": motif_counts,
            "deficits": motif_deficits,
        },
        "sample_floor": {
            "status": "PASS" if sample_floor_pass else "FAIL",
            "required_min_total_pairs": args.sample_floor,
            "total_pairs": total_pairs,
            "shortfall": max(0, args.sample_floor - total_pairs),
        },
        "penalty_applicability": {
            "status": "PASS" if penalty_applicability_pass else "FAIL",
            "min_share": round(args.min_penalty_applicability_share, 6),
            "applicable_pairs": applicable_count,
            "total_pairs": total_pairs,
            "share": round(penalty_applicability_share, 6),
            "applicable_by_motif": applicable_by_motif,
            "pair_level": applicability_rows,
        },
        "rank_shift_opportunity": {
            "status": "PASS" if rank_shift_opportunity_pass else "FAIL",
            "min_estimated_boundary_flip_count": args.min_rank_shift_opportunities,
            "estimated_boundary_flip_count": estimated_flip_opportunities,
            "selected_queries_analyzed": len(selected_query_ids),
            "boundary_windows_analyzed": boundary_windows_analyzed,
            "boundary_margin_stats": {
                "count": len(margins),
                "min": round(min(margins), 6) if margins else None,
                "max": round(max(margins), 6) if margins else None,
                "avg": round((sum(margins) / len(margins)), 6) if margins else None,
            },
            "per_query": query_opportunity_rows,
        },
    }

    coverage_sufficient = all(c["status"] == "PASS" for c in checks.values())
    coverage_decision = "SUFFICIENT" if coverage_sufficient else "INSUFFICIENT"

    remediation_guidance: List[str] = []
    if not motif_coverage_pass:
        remediation_guidance.append(
            "Increase curated pairs for under-covered targeted motifs until each motif reaches the configured minimum."
        )
    if not sample_floor_pass:
        remediation_guidance.append(
            "Expand curated slice size to satisfy the configured total sample floor before directional intervention."
        )
    if not penalty_applicability_pass:
        remediation_guidance.append(
            "Refresh curation with pairs where intervention penalty predicates are triggerable to improve directional signal relevance."
        )
    if not rank_shift_opportunity_pass:
        remediation_guidance.append(
            "Prioritize additional near-boundary (ranks 8-12) pairs with tighter score margins to increase flip-opportunity sensitivity."
        )

    audit_json = {
        "metadata": {
            "run_id": "p5_05a_coverage_audit",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "status": "READY" if coverage_sufficient else "RETURN_RETRY",
            "continue_mode": "CONTINUE_SAFE" if coverage_sufficient else "RETURN_RETRY",
            "deterministic": True,
            "seed": 42,
            "scope": "offline_research_only",
            "pretrial_gate_only": True,
            "promotion_gate_changed": False,
            "governance_semantics_note": "This audit is a pre-trial signal-quality gate only. G1/G2/G3/G4 promotion gate semantics remain unchanged.",
            "label_policy_alignment": "2->0 applied where labels are consumed in promotion-metric-adjacent paths.",
        },
        "preflight": {
            "inputs_checked": [p.as_posix() for p in required_inputs],
            "blockers": blockers,
            "assumptions_applied": [
                "Motif minimum default is 3 pairs per targeted motif (configurable).",
                "Sample floor default is 10 total pairs (configurable).",
                "Rank-shift opportunity uses baseline score margins around the top-10 boundary (ranks 8-12 when available).",
                "Audit is executed after curation and before intervention execution.",
            ],
        },
        "parameters": {
            "motif_min": args.motif_min,
            "sample_floor": args.sample_floor,
            "min_penalty_applicability_share": round(args.min_penalty_applicability_share, 6),
            "min_rank_shift_opportunities": args.min_rank_shift_opportunities,
        },
        "checks": checks,
        "coverage_decision": coverage_decision,
        "delegate_guidance": {
            "future_intervention_delegate_action": "CONTINUE_SAFE" if coverage_sufficient else "RETURN_RETRY",
            "remediation_guidance": remediation_guidance,
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit_json, f, indent=2)

    check_rows = [
        ("motif_coverage", checks["motif_coverage"]["status"]),
        ("sample_floor", checks["sample_floor"]["status"]),
        ("penalty_applicability", checks["penalty_applicability"]["status"]),
        ("rank_shift_opportunity", checks["rank_shift_opportunity"]["status"]),
    ]

    remediation_md = ""
    if coverage_decision == "INSUFFICIENT":
        remediation_bullets = "\n".join(f"- {item}" for item in remediation_guidance)
        remediation_md = (
            "\n## Remediation (Required Before Intervention)\n\n"
            f"{remediation_bullets}\n\n"
            "Future intervention delegates should **RETURN_RETRY** until this audit reaches `coverage_decision=SUFFICIENT`.\n"
        )

    checks_md = "\n".join(f"| `{name}` | **{status}** |" for name, status in check_rows)

    report_text = f"""# P5-05A Coverage Sufficiency Audit Report

- **Run ID:** `p5_05a_coverage_audit`
- **Date (UTC):** {audit_json['metadata']['timestamp_utc']}
- **Coverage Decision:** **{coverage_decision}**

## Scope and Policy Note

This artifact is a **pre-trial signal-quality gate** for directional slices. It is **not** a promotion gate, and G1/G2/G3/G4 semantics are unchanged.

## Readiness Inputs

- `research/ab-eval/out/p5_04a_hardneg_candidate.json`
- `research/ab-eval/out/g3_v3_gated_results.json`
- `research/ab-eval/out/full_set_review_export_1770612809775.json`
- `research/ab-eval/data/queries.medium.human.v1.json`
- `research/ab-eval/data/corpus.200.json`

## Check Summary

| Check | Status |
|---|---|
{checks_md}

## Metrics Snapshot

- Motif minimum per targeted motif: `{args.motif_min}`
- Targeted motifs: `{', '.join(targeted_motifs)}`
- Motif counts: `{json.dumps(motif_counts, sort_keys=True)}`
- Sample floor: `{args.sample_floor}`
- Total curated pairs: `{total_pairs}`
- Penalty applicability share: `{penalty_applicability_share:.4f}` (min `{args.min_penalty_applicability_share:.4f}`)
- Estimated boundary flip opportunities: `{estimated_flip_opportunities}` (min `{args.min_rank_shift_opportunities}`)

## Decision

- `coverage_decision`: **{coverage_decision}**
- Delegate action: **{audit_json['delegate_guidance']['future_intervention_delegate_action']}**
{remediation_md}
---
Generated by `research/ab-eval/py/run_p5_05a_coverage_audit.py`.
"""
    write_report(report_path, report_text)

    print(f"P5-05A coverage audit complete: {coverage_decision}")
    print(f"Saved audit JSON: {out_path.as_posix()}")
    print(f"Saved report: {report_path.as_posix()}")


if __name__ == "__main__":
    main()

