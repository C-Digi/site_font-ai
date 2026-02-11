# DEC-20260211-01: Evaluation Governance & Gating Lock

## Context
As the project moves toward production, we need to transition from exploratory experiments to a rigorous, repeatable evaluation process. This requires locking down the evaluation contract, defining hard promotion gates, and standardizing reproducibility.

## Decision
We are implementing three end-to-end governance upgrades:

1.  **Locked Evaluation Contract**: Created `research/ab-eval/EVALUATION_CONTRACT.md` as the canonical source of truth for metric priorities, label handling (2-policy), and artifact naming.
2.  **Hard Acceptance Gates**: Encoded explicit pass/fail gates (G1-G4) for model promotion, supported by a new validation script `research/ab-eval/py/validate_gates.py`.
3.  **Reproducibility Standard**: Standardized on a default seed of `42` and implemented quota management/reproducibility guidelines in `research/ab-eval/REPRODUCIBILITY.md`.

## Non-Binary Label Handling ("2" Policy)
We have decided on an **Explicit Remap to 0** policy for labels marked as `2` (Uncertain/Partial). This ensures that only high-confidence matches contribute to positive Recall, maintaining a high precision bar for production.

## Consequences
- All future model/retrieval changes MUST pass the G1-G4 gates before being promoted.
- Any run with `repeats > 1` must be aggregated as specified in `REPRODUCIBILITY.md`.
- Evaluation artifacts must strictly follow the `weekN_` naming convention.

## Status
**Approved & Implemented.**
