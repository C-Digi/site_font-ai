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

## Expanded Probe (Quota-Aware) — Prompt `v3` vs `v3_2`

### Commands Run
- Control arm:
  - `\.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --spec-dir specimens_v3 --max-fonts 40 --keys-file key.md --output week1_expanded_v3_control_results.json --cache-output week1_expanded_v3_control_raw.json`
- Treatment arm:
  - `\.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_2 --gate 0.9 --spec-dir specimens_v3 --max-fonts 40 --keys-file key.md --output week1_expanded_v3_2_treatment_results.json --cache-output week1_expanded_v3_2_treatment_raw.json`
- Comparison:
  - `\.\.venv-ab-eval\Scripts\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/week1_expanded_v3_control_results.json --treatment research/ab-eval/out/week1_expanded_v3_2_treatment_results.json --output research/ab-eval/out/week1_expanded_v3_vs_v3_2_comparison.json`

### Keys / Quota Notes
- `--keys-file key.md` was used on both arms.
- Runtime confirmed `Loaded 5 Gemini API key(s)` on both runs.
- No blocking quota error interrupted this expanded probe.

### Per-Arm Metrics (Expanded, `--max-fonts 40`)
- Control (`v3`):
  - Agreement: `60.29%` (`0.6029`)
  - Precision: `66.67%` (`0.6667`)
  - Recall: `66.67%` (`0.6667`)
  - F1: `66.67%` (`0.6667`)
  - Counts: `tp=6, fp=3, fn=3, tn=35, total=68`
- Treatment (`v3_2`):
  - Agreement: `60.29%` (`0.6029`)
  - Precision: `63.64%` (`0.6364`)
  - Recall: `77.78%` (`0.7778`)
  - F1: `70.00%` (`0.7000`)
  - Counts: `tp=7, fp=4, fn=2, tn=34, total=68`

### Comparison (Treatment - Control)
- Common coverage: `68`
- Deltas:
  - Agreement: `+0.0000`
  - Precision: `-0.0303`
  - Recall: `+0.1111`
  - F1: `+0.0333`
- Helps / Hurts / Net: `1 / 1 / 0`

### Signal Quality / Interpretation
- Coverage guardrail status: **PASS** (`common_coverage=68`, threshold is `<20` for insufficient signal).
- Near-zero coverage condition: **not observed**.
- Interpretation: **informational / non-promotional**. This expanded probe improves directional confidence versus smoke, but with `net_help=0` and mixed precision/recall movement, it does not establish a promotion case.

### Immediate Next Step Recommendation
- Keep `v3` as control default for now.
- Run the next governance-scoped decision step under quota window (promotion-grade evaluation policy), using this expanded probe only as directional evidence.

### Expanded Artifacts Produced
- `research/ab-eval/out/week1_expanded_v3_control_raw.json`
- `research/ab-eval/out/week1_expanded_v3_control_results.json`
- `research/ab-eval/out/week1_expanded_v3_2_treatment_raw.json`
- `research/ab-eval/out/week1_expanded_v3_2_treatment_results.json`
- `research/ab-eval/out/week1_expanded_v3_vs_v3_2_comparison.json`

## Expanded Probe (Quota-Aware) — Prompt `v3` vs `v3_3`

### Commands Run
- Optional parser check:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --help`
- Control arm:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --spec-dir specimens_v3 --max-fonts 40 --keys-file key.md --output week1_expanded_v3_control_results.json --cache-output week1_expanded_v3_control_raw.json`
  - Reused existing comparable control artifact (no unnecessary control rerun).
- Treatment arm:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_3 --gate 0.9 --spec-dir specimens_v3 --max-fonts 40 --keys-file key.md --output week1_expanded_v3_3_treatment_results.json --cache-output week1_expanded_v3_3_treatment_raw.json`
- Comparison:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/week1_expanded_v3_control_results.json --treatment research/ab-eval/out/week1_expanded_v3_3_treatment_results.json --output research/ab-eval/out/week1_expanded_v3_vs_v3_3_comparison.json`

### Keys / Quota Notes
- `--keys-file key.md` used for treatment run.
- Runtime confirmed `Loaded 5 Gemini API key(s)`.
- No blocking quota error observed on the treatment run.

### Per-Arm Metrics (Expanded, `--max-fonts 40`)
- Control (`v3`, common slice):
  - Agreement: `60.29%` (`0.6029`)
  - Precision: `66.67%` (`0.6667`)
  - Recall: `66.67%` (`0.6667`)
  - F1: `66.67%` (`0.6667`)
  - Counts: `tp=6, fp=3, fn=3, tn=35, total=68`
- Treatment (`v3_3`, common slice):
  - Agreement: `61.76%` (`0.6176`)
  - Precision: `75.00%` (`0.7500`)
  - Recall: `66.67%` (`0.6667`)
  - F1: `70.59%` (`0.7059`)
  - Counts: `tp=6, fp=2, fn=3, tn=36, total=68`

### Comparison (Treatment - Control)
- Common coverage: `68`
- Deltas:
  - Agreement: `+0.0147`
  - Precision: `+0.0833`
  - Recall: `+0.0000`
  - F1: `+0.0392`
- Helps / Hurts / Net: `1 / 0 / +1`

### Signal Quality / Interpretation
- Coverage guardrail status: **PASS** (`common_coverage=68`, insufficient signal threshold is `<20`).
- Near-zero coverage condition: **not observed**.
- Interpretation: **informational / non-promotional**. `v3_3` improves precision and agreement on this expanded probe, with positive net helps, but this remains a quota-aware directional checkpoint rather than a promotion decision.

### Expanded Artifacts Produced (`v3` vs `v3_3`)
- `research/ab-eval/out/week1_expanded_v3_control_results.json` (reused control)
- `research/ab-eval/out/week1_expanded_v3_3_treatment_raw.json`
- `research/ab-eval/out/week1_expanded_v3_3_treatment_results.json`
- `research/ab-eval/out/week1_expanded_v3_vs_v3_3_comparison.json`
