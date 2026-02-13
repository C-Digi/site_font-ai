# DEC-20260213-01-p1-orthogonal-pivot

## Status
Rejected / Iterate (Feb 13 directional run showed zero delta)

## Context
Following the Week 1-3 optimization cycles, we have established a solid baseline with Prompt V3 and Specimen V3.1. However, "Bucket 1" errors (Diagnostic Neutrality) remain a primary source of misalignment where the LLM over-relies on its own internal "Critical Distinction" blocks rather than the provided specimen evidence.

Prior attempts at multi-variable prompts (V4) led to regression. This decision pivots to a single-variable, orthogonal intervention strategy.

## Decision
We will implement and evaluate `v5_1` as a P1 directional cycle.

### Intervention Definition (`v5_1`)
- **Base:** Prompt `v3`
- **Delta:** Add a specific "Diagnostic Neutrality" guardrail.
- **Guardrail Text:** "Critical Distinction block is diagnostic-only; do not treat it as category proof by itself; verify category/technical classification primarily from body/alphabet evidence."
- **Constraint:** No other changes (geometric, luxury, category-consistency) are to be bundled.

### Execution Strategy
- **Stage:** Directional only.
- **Sample Size:** `n=20`, paired (Control: `v3`, Treatment: `v5_1`).
- **Metric Gates:** Strict all-gates-pass policy per `EVALUATION_CONTRACT.md`.
- **Label Remap:** `2 -> 0` (non-binary labels remapped to mismatch for primary metrics).

## Consequences
- If directional gates pass (G1-G3 positive, no fragile signal), we will escalate to P3 promotion-grade runs (`n=100`, `repeats=3`).
- If gates fail, we iterate on the guardrail text or re-evaluate the hypothesis.
- No changes will be made to the production runtime during this cycle.
