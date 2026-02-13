# DEC-20260213-02-v5-1-oem-slice-go-fullset-no-go

## Status
Accepted

## Context
Week 4 introduced `v5_1` (Diagnostic Neutrality) as a single-variable prompt intervention. Results diverged by evaluation scope:

- OEM-targeted slice (`week4_p2`) passed gates (targeted GO).
- Full-set validation (`week4_p3`) did not meet promotion threshold on G1 (Agreement Delta `+0.40%`, threshold `>= +1.0%`).

This created a governance decision point: whether a targeted-slice GO can justify global production-default promotion.

## Decision
- Keep `v3` as global champion.
- Do **not** promote `v5_1` to production default.
- Treat targeted slice GO as directional evidence only.
- Require canonical full-set gate pass for any global promotion decision.
- Pause further prompt-only `v5_x` single-variable iteration unless a dominant actionable motif concentration emerges from root-cause analysis.

## Rationale
- Promotion criteria are global and contract-bound; targeted slices are not representative enough for global default changes.
- Full-set `v5_1` outcome failed G1 under the locked governance contract.
- Post-run hurts analysis did not yield a dominant (>50%) single actionable motif, reducing confidence in immediate prompt-only follow-ups.

## Alternatives Considered
- Promote `v5_1` immediately based on OEM slice GO.
  - Rejected: insufficient representativeness for global default.
- Continue rapid `v5_x` prompt-only iterations.
  - Rejected: no dominant motif concentration; increased churn risk.

## Consequences
- `v3` remains champion/default for now.
- OEM slice results remain useful as targeted signal for future scoped strategies.
- Next optimization cycles should prioritize non-prompt-only lanes (data coverage, reranking, query-class handling) or await stronger motif concentration.

## Related Specs
- [font-search-rag](../font-search-rag.md)

## Related R&D
- [REPORT_WEEK4_P2_OEM_GATING](../../research/ab-eval/REPORT_WEEK4_P2_OEM_GATING.md)
- [REPORT_WEEK4_P3_V5_1_FULLSET](../../research/ab-eval/REPORT_WEEK4_P3_V5_1_FULLSET.md)
- [REPORT_WEEK4_P3_HURTS_ROOTCAUSE](../../research/ab-eval/REPORT_WEEK4_P3_HURTS_ROOTCAUSE.md)

## Supersedes
- [DEC-20260213-01-p1-orthogonal-pivot](./DEC-20260213-01-p1-orthogonal-pivot.md)

## Superseded By
- N/A
