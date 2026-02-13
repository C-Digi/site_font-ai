# Directional Evaluation Report: Week 4 V5.1 (Diagnostic Neutrality)

- **Date:** 2026-02-13
- **Variant:** `v5_1` (Diagnostic Neutrality Guardrail)
- **Control:** `v3` (Champion)
- **Sample Size:** `n=20` (Paired)
- **Specimen Version:** `v3.1`
- **Model:** `google/gemini-2.0-flash-lite-001` (OpenRouter)

## Executive Summary
The `v5_1` intervention, which targeted "Bucket 1" diagnostic neutrality by adding a specific guardrail against over-reliance on the "Critical Distinction" block, resulted in **zero delta** compared to the `v3` control on the directional `n=20` sample.

**Decision:** `NO-GO / ITERATE`. Escalation to P3 is not justified as no signal (improvement or regression) was observed in the target metrics.

## Metric Summary

| Metric | Control (v3) | Treatment (v5_1) | Delta | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Agreement** | 0.9500 | 0.9500 | 0.0000 | FAIL (G1) |
| **Precision** | 0.8750 | 0.8750 | 0.0000 | PASS (G2) |
| **Recall** | 1.0000 | 1.0000 | 0.0000 | - |
| **F1 Score** | 0.9333 | 0.9333 | 0.0000 | - |

## Governance Gates (EVALUATION_CONTRACT.md)

- **G1 (Agreement Delta >= +1.0%):** FAIL (0.0%)
- **G2 (Precision Regression <= -2.0%):** PASS (0.0%)
- **G3 (Helps/Hurts Net > 0):** FAIL (Net 0)
- **G4 (Visual QA):** PASS (Consistent `v3.1` context)

**Overall Status:** FAIL (NO-GO)

## Observed Patterns
- **Neutrality:** Both models correctly identified matches in 19/20 cases and failed in the same 1/20 case.
- **Hypothesis Check:** The "Diagnostic Neutrality" guardrail did not trigger any changes in judgment for the sampled fonts. This may indicate that the `n=20` sample did not contain enough "edge cases" where the Critical Distinction block was misleading, or the base `v3` model was already sufficiently neutral for these specific fonts.
- **Stability:** The signal is non-fragile but null.

## Escalation Decision
**NO-GO / ITERATE**
- **Rationale:** No positive signal observed to justify the cost of a full P3 run (`n=100`, `repeats=3`).
- **Next Step:** Identify specific "Bucket 1" failure cases from the full SSoT and run a targeted probe on those specific fonts to see if the guardrail has the intended effect when the distraction is present.
