# DEC-20260208-human-label-medium-v1-workflow

## Status
Completed (2026-02-08)

## Context
`research/ab-eval/data/labels.complex.v1.json` became a practical scoring SSoT for complex benchmark runs, but it is acknowledged as provisional and not sufficiently human-reviewed for subjective style/vibe relevance. The team needs a higher-confidence label source with limited reviewer bandwidth and a non-expert-friendly interaction model.

## Decision
Adopt a **medium-first, blind-first visual human-labeling workflow** as the next canonicalization track:

- Create a medium-complexity query set (`queries.medium.human.v1`, target 20 queries, allowed 16–24).
- Use card-based reviewer UI with binary relevance (`0/1`), optional top-pick flags, and per-query confidence.
- Enforce anti-bias controls (hidden legacy labels, deterministic per-reviewer randomization, capped legacy-seed contribution to candidate pools).
- Convert raw judgments deterministically to `labels.medium.human.v1.json` (current scorer-compatible shape) with provenance metadata and adjudication logs.
- Promote labelset to canonical SSoT only after explicit agreement and adjudication gates are met.
- Use medium-v1 outputs and lessons to migrate to `labels.complex.v2.human-reviewed.json`.

## Rationale
- Improves trustworthiness of relevance labels before score-driven architecture decisions.
- Binary grading (0/1) optimizes for reviewer throughput and direct compatibility with current scoring metrics.
- Fits small-team reviewer capacity better than immediate full complex relabeling.
- Reduces anchoring risk and preserves reproducibility through deterministic conversion and metadata lineage.

## Alternatives Considered
- Full immediate relabel of all 40 complex queries — rejected due to reviewer fatigue and quality risk.
- Continue using proxy/legacy labels only — rejected because it does not satisfy human-review quality goals.
- Open-ended annotation without fixed rubric — rejected due to low consistency and weak reproducibility.

## Consequences
- Positive: Creates a practical path to high-confidence human-reviewed labels and clearer promotion gates.
- Positive: Enables iterative refinement (medium first, then complex v2) with measurable quality criteria.
- Tradeoff: Adds process overhead (adjudication, provenance tracking) before final canonicalization.
- Tradeoff: Complex-v2 migration remains a follow-on phase rather than immediate completion.

## Related Specs
- [font-search-rag](../font-search-rag.md)

## Related R&D
- [Human labeling workflow plan](../../research/ab-eval/HUMAN_LABELING_WORKFLOW_MEDIUM_V1.md)
- [Offline A/B decision log](../../research/ab-eval/DECISIONS.md)
- [Offline A/B runbook](../../research/ab-eval/RUNBOOK.md)

## Supersedes
- N/A

## Superseded By
- N/A

## Results (2026-02-08)
- **Labelset Produced:** `labels.medium.human.v1.json` (140 relevant pairs across 20 queries).
- **Run ID:** `medium-human-v1`
- **Governance:** Gate waiver for single-reviewer pass accepted for medium-v1 to accelerate calibration; full adjudication requirements deferred to complex-v2.
- **Key Outcome:** Variant B2 (VL) achieved **Recall@10 of 0.35** and **MRR of 0.64**, more than doubling the performance of the text baseline (Variant A).
- **Conclusion:** Medium-v1 human labels confirmed B2 as the superior retrieval path. The workflow is validated and ready for full-scale complex-v2 labeling.

