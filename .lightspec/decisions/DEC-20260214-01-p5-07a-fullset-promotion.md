# DEC-20260214-01-p5-07a-fullset-promotion

## Status
Accepted

## Context
Phase 5 introduced a rank-boundary-aware intervention strategy (P5-06B-R2) that demonstrated directional promise on a curated slice. P5-07A extended this strategy to the full SSoT dataset (247 pairs) to validate representativeness before production-default consideration.

The full-set validation produced the following gate results:
- **G1 (Agreement Delta):** +3.24% (threshold: >= +1.0%) — **PASS**
- **G2 (Precision Delta):** +2.09% (threshold: >= -2.0%) — **PASS**
- **G3 (Helps/Hurts Net):** +8 (threshold: > 0) — **PASS**
- **G4 (Visual QA):** Zero clipping/overlap verified — **PASS**

All four canonical gates passed, confirming the intervention strategy is ready for production-default consideration.

## Decision
- Accept P5-07A full-set validation as sufficient evidence for production-default promotion.
- The rank-boundary-aware scaling mechanism (P5-06B-R2 strategy) is approved for staged rollout.
- **Gate semantics remain unchanged.** This decision follows the canonical EVALUATION_CONTRACT.md gates without modification.
- Staged rollout is required before production-default activation.

## Rationale
- Full-set validation (247 pairs) passed all four canonical gates with significant margins.
- Agreement delta (+3.24%) exceeds threshold by >3x, indicating robust improvement.
- Precision improved (+2.09%) rather than regressing, demonstrating the intervention does not trade precision for recall.
- Net helps (+8) confirms positive impact outweighs regressions.
- G4 visual QA verified zero clipping/overlap across required regression specimens and edge-case families.
- The strategy generalizes beyond the curated directional slice, confirming representativeness.

## Evidence Links
- [REPORT_P5_07A_FULLSET_VALIDATION](../../research/ab-eval/REPORT_P5_07A_FULLSET_VALIDATION.md)
- [QA_P5_07A_G4_VISUAL](../../research/ab-eval/QA_P5_07A_G4_VISUAL.md)
- [p5_07a_v3_vs_fullset_gates.json](../../research/ab-eval/out/p5_07a_v3_vs_fullset_gates.json)
- [p5_07a_v3_vs_fullset_comparison.json](../../research/ab-eval/out/p5_07a_v3_vs_fullset_comparison.json)

## Gate Results Summary

| Gate | Metric | Value | Threshold | Status |
| :--- | :--- | :--- | :--- | :--- |
| **G1** | Agreement Delta | +3.24% | >= +1.0% | **PASS** |
| **G2** | Precision Delta | +2.09% | >= -2.0% | **PASS** |
| **G3** | Helps/Hurts Net | +8 | > 0 | **PASS** |
| **G4** | Visual QA | Verified | Zero clipping/overlap | **PASS** |

## Alternatives Considered
- **Immediate production-default activation without staged rollout.**
  - Rejected: Staged rollout is required to monitor real-world impact and enable rapid rollback if unexpected issues emerge.
- **Additional validation cycles before acceptance.**
  - Rejected: All canonical gates passed with significant margins; further validation would delay improvement without substantive risk mitigation.

## Consequences
- P5-07A strategy is approved for staged rollout to production.
- Rollout must follow staged exposure tiers with monitoring and rollback criteria (see RUNBOOK.md).
- Production-default activation occurs after successful staged rollout completion.
- This decision supersedes prior NO-GO decisions for P5-01 through P5-06A, which explored alternative strategies that did not pass gates.

## Related Specs
- [font-search-rag](../font-search-rag.md)
- [EVALUATION_CONTRACT](../../research/ab-eval/EVALUATION_CONTRACT.md)

## Related R&D
- [REPORT_P5_06B_DIRECTIONAL](../../research/ab-eval/REPORT_P5_06B_DIRECTIONAL.md)
- [REPORT_P5_07A_FULLSET_VALIDATION](../../research/ab-eval/REPORT_P5_07A_FULLSET_VALIDATION.md)

## Supersedes
- N/A (new decision)

## Superseded By
- N/A
