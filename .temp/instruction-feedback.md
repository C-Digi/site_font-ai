# Instruction Feedback - Governance Upgrades Task

## Ambiguities & Missing Information

1.  **Metric Promotion Thresholds**: The task asks for "metric promotion thresholds (Agreement delta minimum, Precision regression cap)". While `RUNBOOK.md` suggests a +10% Recall@10 improvement for visual queries, explicit thresholds for Agreement and Precision are not yet defined.
    - *Plan*: Define these in `research/ab-eval/EVALUATION_CONTRACT.md` as:
        - Agreement delta minimum: +1.0%
        - Precision regression cap: -2.0%
        - Helps/Hurts net threshold: > 0

2.  **Visual QA Acceptance Thresholds**: "Zero clipping/overlap" is requested but no automated check exists.
    - *Plan*: Define as manual verification requirement in the contract, or attempt a basic pixel-based check if specimen generation scripts can be extended.

3.  **Non-binary Label Handling (2 Policy)**: Instructions mention "2 policy: explicit exclude/remap with rationale".
    - *Plan*: The contract will specify that labels marked as `2` (uncertain/partial) must be remapped to `0` (negative) for strict evaluation or `1` (positive) for lenient, with a default of `0` to avoid false positives.

4.  **Canonical Baseline Artifact Path(s)**: Multiple "canonical" reports exist (Medium Human v1, Complex v1).
    - *Plan*: Pin `research/ab-eval/out/report_medium_human_v1.json` as the primary baseline for retrieval quality.

5.  **Reproducibility Standards**: "Fixed seed + repeat count options" need a default.
    - *Plan*: Use `seed=42` and `repeats=1` (default) for deterministic runs, with `repeats=3` for stochastic model probes.

6.  **Quota/Key Strategy**:
    - *Plan*: Document the use of `GEMINI_API_KEY` with standard rate limiting handling in scripts.

## Conflicts Discovery

- `RUNBOOK.md` mentions "SSoT MIGRATED" to LightSpec, but the task asks to create a canonical contract in `research/ab-eval/EVALUATION_CONTRACT.md`.
- *Resolution*: The contract will live in `research/ab-eval/` as requested but will be linked from LightSpec.
