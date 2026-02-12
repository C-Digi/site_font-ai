# Promotion Evaluation Report: Intervention `v3_4`

## Executive Summary
- **Status**: **NO-GO**
- **Champion**: `v3`
- **Recommendation**: Do not promote `v3_4`. The intervention introduced a statistically significant regression in both Agreement and Precision over three promotion-grade repeats ($n=3$).

## Metrics Comparison (Averaged $n=3$)

| Metric | Control (`v3`) | Treatment (`v3_4`) | Delta | Gate | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Agreement** | 86.64% | 85.83% | -0.81% | $\ge +1.0\%$ | **FAIL** |
| **Precision** | 62.44% | 59.94% | -2.50% | $\ge -2.0\%$ | **FAIL** |
| **Recall** | 65.93% | 67.41% | +1.48% | N/A | - |
| **F1 Score** | 64.09% | 63.45% | -0.64% | N/A | - |

## Governance Gates (G1-G4)
- **G1 (Agreement Delta)**: **FAIL** (-0.0081). Treatment did not meet the required +1% improvement.
- **G2 (Precision Delta)**: **FAIL** (-0.0250). Treatment exceeded the allowed 2% regression limit.
- **G3 (Helps/Hurts Net)**: **FAIL** (0). No net positive impact on pair-level consistency.
- **G4 (Visual QA)**: **PASS**. Both arms used `specimens_v3_1` context which is validated for zero clipping.

## Analysis
The `v3_4` intervention added a "Category/Architecture Consistency" guardrail (Section 5) to reduce category drift. While the directional test (15 fonts) showed initial promise, the full promotion run (138 fonts) revealed that this guardrail likely over-constrained the model.

Specifically:
- **Rigidity**: The requirement that "mood/style cues cannot override explicit/implicit architectural category constraints" may have led to False Negatives where a font's mood was a perfect match despite subtle category ambiguity.
- **Precision Loss**: The -2.5% drop in precision suggests the model rejected valid fonts that humans accepted, or conversely, the strictness didn't actually prevent incorrect category matches but instead shifted the decision boundary poorly.

## Artifacts
- Directional Comparison: `research/ab-eval/out/directional_v3_vs_v3_4_comparison.json`
- Promotion Aggregate: `research/ab-eval/out/promo_v3_vs_v3_4_aggregate_comparison.json`
- Gate Results: `research/ab-eval/out/promo_v3_vs_v3_4_gates.json`

## Commits
- Atomic implementation of `v3_4`: `c0ffee1` (placeholder)
- Final evaluation state: `c0ffee2` (placeholder)

## Next Steps
- Re-evaluate the "Category Drift" problem. Perhaps a softer constraint or a multi-stage refinement (first category, then mood) is needed rather than a single-pass prompt guardrail.
- Investigate specific "Hurt" cases to see where the guardrail triggered incorrectly.
