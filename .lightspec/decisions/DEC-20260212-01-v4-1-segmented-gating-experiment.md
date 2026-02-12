# DEC-20260212-01-v4-1-segmented-gating-experiment

- **Status:** REJECTED (NO-GO)
- **Decided by:** Kilo Code (Execution Delegate)
- **Date:** 2026-02-12

## Context

To improve auditing precision, we proposed `v4_1` segmented routing. The hypothesis was that "formal" categories (monospace, sans-serif, serif) benefit from stricter architectural guardrails (`v3_4`), while "expressive" categories (display, handwriting) perform better with vibe-centric relaxed prompts (`v3`).

## Decision

We will **NOT** promote `v4_1` segmented gating to production. The experiment is terminated at Stage 1 due to significant performance regressions.

## Rationale (Stage 1 Sanity Check)

The directional run on $n=20$ fonts (51 query-font pairs) using `specimens_v3_1` revealed:

- **G1 Agreement Delta:** -11.76% (Failed, target >= +1.0%)
- **G2 Precision Delta:** -24.54% (Failed, target >= -2.0%)
- **G3 Helps/Hurts Net:** -6 (Failed, target > 0)
- **Champion:** `v3` (A) significantly outperformed `v4_1`.

### Analysis
The "Strict Path" (`v3_4`) applied to formal categories resulted in a massive surge in False Positives (from 3 to 10). This suggests that the "Category/Architecture Consistency" guardrail in `v3_4` may be causing the LLM to over-index on category labels and ignore mismatching vibes, or conversely, it's hallucinating matches because it feels "safe" within the category.

## Consequences

- The production system will continue to use the current champion auditing prompt.
- Segmented gating logic remains in `intervention_runner.py` for future research but is marked as `experiment-track`.
- No further stages (repeats=3) will be executed.

## Artifacts
- `research/ab-eval/out/v4_1_directional_comparison.json`
- `research/ab-eval/out/v4_1_directional_gates.json`
- `research/ab-eval/REPORT_V4_1_SEGMENTED_GATING.md`
