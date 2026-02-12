# Report: v4_1 Segmented Gating Experiment

## Executive Summary
- **Outcome:** NO-GO
- **Status:** Terminated at Stage 1
- **Reason:** Material regression in precision and agreement across formal categories.

## Experiment Configuration
- **Model:** `google/gemini-2.0-flash-001`
- **Specimens:** `specimens_v3_1`
- **Sample Size:** $n=20$ fonts (51 query-font pairs)
- **Routing:**
  - `v3_4` (Strict) -> `monospace`, `sans-serif`, `serif`
  - `v3` (Relaxed) -> `display`, `handwriting`, `unknown`

## Governance Gate Results (Stage 1)

| Gate | Status | Value | Threshold |
|------|--------|-------|-----------|
| **G1 (Agreement Delta)** | **FAIL** | -0.1176 | >= 0.01 |
| **G2 (Precision Delta)** | **FAIL** | -0.2454 | >= -0.02 |
| **G3 (Helps/Hurts Net)** | **FAIL** | -6 | > 0 |
| **G4 (Visual QA)** | **PASS** | specimens_v3_1 matched | Zero clipping |

## Comparison Metrics

| Variant | Agreement | Precision | Recall | F1 | Helps | Hurts |
|---------|-----------|-----------|--------|----|-------|-------|
| `v3` (A) | 0.8235 | 0.7692 | 0.6250 | 0.6897 | - | - |
| `v4_1` | 0.7059 | 0.5238 | 0.6875 | 0.5946 | 1 | 7 |

## Detailed Analysis

### False Positive Surge
The primary failure mode for `v4_1` was a surge in False Positives (10 vs 3 in baseline). 

Routing details:
- Most formal categories were routed to `v3_4`.
- `v3_4` includes the "Category/Architecture Consistency" guardrail.
- Paradoxically, this guardrail appears to have weakened the model's ability to reject fonts that are technically in the right category but fail the specific vibe or secondary technical constraint of the query.

### Examples of Hurts
- **Font:** `Alata` (sans-serif)
- **Query:** "tech-focused condensed"
- **Result:** `v4_1` matched (FP), `v3` rejected (TN). `Alata` is not condensed. `v3_4` likely prioritized "sans-serif" consistency over the specific "condensed" constraint.

## Conclusion
Segmented routing as implemented in `v4_1` is counter-productive. Stricter architectural prompts for formal categories inadvertently lower the threshold for vibe/detail rejection. 

**Recommendation:** Retain `v3` or `v3_4` as a global prompt if they prove stable individually, but do not use this category-based routing logic for production auditing.
