# Week 1 Smoke A/B Report: Prompt v3 vs v3_2

## Run Summary
- Objective: low-cost smoke A/B to validate end-to-end prompt path for `v3` (control) vs `v3_2` (treatment) and get early directional read for G1/G3 risk.
- Scope: smoke-only, no full-set reruns, no governance edits, no production code changes.
- Sample target: `--max-fonts 8` per arm.

## Commands Run
- Control arm:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --max-fonts 8 --output week1_smoke_v3_control_results.json --cache-output week1_smoke_v3_control_raw.json`
- Treatment arm:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_2 --gate 0.9 --max-fonts 8 --output week1_smoke_v3_2_treatment_results.json --cache-output week1_smoke_v3_2_treatment_raw.json`
- Comparison:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/week1_smoke_v3_control_results.json --treatment research/ab-eval/out/week1_smoke_v3_2_treatment_results.json --output research/ab-eval/out/week1_smoke_v3_vs_v3_2_comparison.json`

## Coverage / Execution Notes
- Control (`v3`): partial success with retries; 7 scored items.
  - Aggregates: agreement `85.71%`, precision `100%`, recall `100%`, F1 `100%`, total `7`.
  - Several later items hit `429 RESOURCE_EXHAUSTED`, but run produced non-empty results.
- Treatment (`v3_2`): all attempts hit `429 RESOURCE_EXHAUSTED`; no scored items.
  - Aggregates: agreement `0%`, precision `0%`, recall `0%`, F1 `0%`, total `0`.
- Comparison artifact generated successfully.
  - Common coverage: `0`.
  - Helps/Hurts/Net: `0/0/0`.

## Metrics Delta (Treatment - Control)
- Agreement: `0.0` (on common set; common coverage is zero)
- Precision: `0.0` (on common set; common coverage is zero)
- Recall: `0.0` (on common set; common coverage is zero)
- F1: `0.0` (on common set; common coverage is zero)
- G3 directional read: not measurable from this smoke due to zero common coverage.

## Caveats
- This is a small-sample smoke and is non-promotional by design.
- Quota/rate-limit failures (`429 RESOURCE_EXHAUSTED`) dominated treatment, invalidating directional interpretation.
- With zero common coverage, delta metrics are non-informative placeholders.

## Smoke Significance Decision
- **NO-GO (for significance inference)**: smoke is **informational only** and does not support any promotion or risk conclusion for G1/G3.

## Immediate Next Action
- Re-run the same smoke A/B after quota recovery (or key rotation per reproducibility process), keeping all settings fixed and targeting non-zero common coverage before interpreting any G1/G3 direction.
