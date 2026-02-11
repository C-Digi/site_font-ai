# Week 1 Smoke A/B Report: Prompt v3 vs v3_2

## Run Summary
- Objective: quota-aware smoke A/B rerun to recover blocked directional read for `v3` (control) vs `v3_2` (treatment).
- Scope: smoke-only, no full-set reruns, no governance edits, no production code changes.
- Sample executed: `--max-fonts 6` per arm (within required 4-8 range).

## Commands Run
- Control arm:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --spec-dir specimens_v3 --max-fonts 6 --keys-file key.md --output week1_smoke_v3_control_results_rerun.json --cache-output week1_smoke_v3_control_raw_rerun.json`
- Treatment arm:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_2 --gate 0.9 --spec-dir specimens_v3 --max-fonts 6 --keys-file key.md --output week1_smoke_v3_2_treatment_results_rerun.json --cache-output week1_smoke_v3_2_treatment_raw_rerun.json`
- Comparison:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/week1_smoke_v3_control_results_rerun.json --treatment research/ab-eval/out/week1_smoke_v3_2_treatment_results_rerun.json --output research/ab-eval/out/week1_smoke_v3_vs_v3_2_comparison.json`

## Quota Strategy
- `--keys-file key.md` was used for both arms.
- Loaded API keys per run: `5`.
- Rerun completed without `429 RESOURCE_EXHAUSTED` interruption on this smoke sample.

## Coverage / Execution Notes
- Control (`v3`) rerun: completed with non-empty coverage.
  - Aggregates: agreement `80.00%`, precision `100.00%`, recall `100.00%`, F1 `100.00%`, total `10`.
- Treatment (`v3_2`) rerun: completed with non-empty coverage.
  - Aggregates: agreement `80.00%`, precision `100.00%`, recall `100.00%`, F1 `100.00%`, total `10`.
- Comparison artifact updated successfully.
  - Coverage: control `10`, treatment `10`.
  - Common coverage: `10`.
  - Helps/Hurts/Net: `0/0/0`.

## Metrics Delta (Treatment - Control)
- Agreement: `0.0`
- Precision: `0.0`
- Recall: `0.0`
- F1: `0.0`
- G3 directional read: no observed directional difference on this smoke sample (`net_help = 0`).

## Caveats
- This is a small-sample smoke and is non-promotional by design.
- Equal metrics on a tiny sample are only a directional signal; they are not evidence for promotion.
- Denominator behavior includes non-binary labels in total counts while confusion terms use binary labels only (per current script parity).

## Smoke Significance Decision
- **NO-GO (for significance inference)**: smoke is **informational only** and does not support any promotion or governance conclusion.

## Immediate Next Action
- Keep this result as a recovered directional checkpoint, then proceed to the next planned week1/week2 sequence only under governance and quota windows (no promotion claim from smoke alone).
