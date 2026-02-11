# Corrective Smoke A/B Task Feedback — v3 vs v3_3 with specimens_v3_1

## Readiness Self-Check (Source of Truth)
- status: READY
- confidence: 0.9
- risk_level: low
- assumption under test: prior NO-GO likely included specimen-context mismatch (`specimens_v3` used while `v3_3` guardrails expect V3.1 cues)

## Critical-Assumption Check
- No contradiction was found in provided task context.
- No blocker identified at pre-execution stage.
- Initial execution state: `CONTINUE_SAFE` (subject to runtime failures/quota).

## Ambiguities
- "Prior promotion run" baseline artifact is not explicitly pinned in task text.
  - Resolution: use `research/ab-eval/out/promo_v3_vs_v3_3_comparison_repeats3.json` as prior reference if needed for directional comparison.
- Report append placement/heading not specified.
  - Resolution: append short corrective-smoke section at end of `research/ab-eval/REPORT_PROMOTION_V3_V3_3_REPEATS3.md`.

## Missing Inputs
- None explicit in task text.
- Runtime prerequisites assumed present: `.venv-ab-eval`, `key.md`, and `specimens_v3_1`.

## Conflicts + Resolution Choices
- Must not invent unsupported CLI flags for validator.
  - Resolution: inspect `validate_gates.py` help/support first, then use only supported parameters.
- Scope-limited output files only.
  - Resolution: write only to the allowed artifact/report/feedback paths.
- Insufficient-signal stop condition.
  - Resolution: mark insufficient if either arm has near-zero scored coverage or `common_coverage < 20`.

## Planned Execution
- Run control (`v3`) and treatment (`v3_3`) with identical settings and `specimens_v3_1`.
- Compare via `compare_week1_prompt_ab.py`.
- Validate gates via `validate_gates.py` on comparison output.
- Preserve partial artifacts and return `RETURN_RETRY` on one-arm quota failure.

## Commit Strategy
- Atomic checkpoint 1: smoke artifacts + comparison + gate results.
- Atomic checkpoint 2: report append + this feedback file.
