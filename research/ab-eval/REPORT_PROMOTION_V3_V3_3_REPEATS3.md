# Promotion Report — Paired Rerun (`v3` control vs `v3_3` treatment, `n=3`)

## Execution Mode Decision
- Status: `CONTINUE_SAFE`
- Rationale:
  - No critical runtime blocker prevented paired reruns.
  - All 3 paired repeats completed for both arms.
  - Coverage remained stable and non-zero across all repeats.
  - Governance result is still **NO-GO** based on gate outcomes (not a runtime blocker).

## Capability Check (`run_production_trial.py`)
- Checked CLI help:
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --help`
- Result:
  - `--repeats` is **not supported**.
  - Manual paired reruns were executed (`r1`, `r2`, `r3`) per arm.

## Commands Executed
- Capability check:
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --help`

- Control arm (`v3`) fresh reruns:
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --spec-dir specimens_v3 --keys-file key.md --output promo_v3_control_r1_results.json --cache-output promo_v3_control_r1_raw.json`
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --spec-dir specimens_v3 --keys-file key.md --output promo_v3_control_r2_results.json --cache-output promo_v3_control_r2_raw.json`
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --spec-dir specimens_v3 --keys-file key.md --output promo_v3_control_r3_results.json --cache-output promo_v3_control_r3_raw.json`

- Treatment arm (`v3_3`) fresh reruns:
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_3 --gate 0.9 --spec-dir specimens_v3 --keys-file key.md --output promo_v3_3_treatment_r1_results.json --cache-output promo_v3_3_treatment_r1_raw.json`
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_3 --gate 0.9 --spec-dir specimens_v3 --keys-file key.md --output promo_v3_3_treatment_r2_results.json --cache-output promo_v3_3_treatment_r2_raw.json`
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_3 --gate 0.9 --spec-dir specimens_v3 --keys-file key.md --output promo_v3_3_treatment_r3_results.json --cache-output promo_v3_3_treatment_r3_raw.json`

- Per-repeat comparisons:
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/promo_v3_control_r1_results.json --treatment research/ab-eval/out/promo_v3_3_treatment_r1_results.json --output research/ab-eval/out/promo_v3_vs_v3_3_r1_comparison.json`
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/promo_v3_control_r2_results.json --treatment research/ab-eval/out/promo_v3_3_treatment_r2_results.json --output research/ab-eval/out/promo_v3_vs_v3_3_r2_comparison.json`
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/promo_v3_control_r3_results.json --treatment research/ab-eval/out/promo_v3_3_treatment_r3_results.json --output research/ab-eval/out/promo_v3_vs_v3_3_r3_comparison.json`

- Gate validation:
  - `\.venv-ab-eval\Scripts\python research/ab-eval/py/validate_gates.py research/ab-eval/out/promo_v3_vs_v3_3_comparison_repeats3.json --out research/ab-eval/out/promo_v3_vs_v3_3_gate_results_repeats3.json`

## Per-Repeat Coverage + Metrics
- Repeat 1:
  - Coverage: `247` common pairs
  - Control (`v3`): agreement `0.8583`, precision `0.5962`, recall `0.6889`, f1 `0.6392`
  - Treatment (`v3_3`): agreement `0.8583`, precision `0.5962`, recall `0.6889`, f1 `0.6392`
  - Helps/Hurts/Net: `7 / 7 / 0`

- Repeat 2:
  - Coverage: `247` common pairs
  - Control (`v3`): agreement `0.8704`, precision `0.6275`, recall `0.7111`, f1 `0.6667`
  - Treatment (`v3_3`): agreement `0.8988`, precision `0.7174`, recall `0.7333`, f1 `0.7253`
  - Helps/Hurts/Net: `10 / 3 / 7`

- Repeat 3:
  - Coverage: `247` common pairs
  - Control (`v3`): agreement `0.8745`, precision `0.6522`, recall `0.6667`, f1 `0.6593`
  - Treatment (`v3_3`): agreement `0.8583`, precision `0.6000`, recall `0.6667`, f1 `0.6316`
  - Helps/Hurts/Net: `6 / 10 / -4`

## Coverage Guardrail Check
- Near-zero coverage observed: **No**
- Valid repeats retained: **3 / 3**
- Fewer-than-2-valid-repeats condition: **Not triggered**

## Aggregated Promotion Artifact
- Artifact:
  - `research/ab-eval/out/promo_v3_vs_v3_3_comparison_repeats3.json`

- Averaged variants (across 3 repeats):
  - `A` (control):
    - agreement: `0.8677`
    - precision: `0.6253`
    - recall: `0.6889`
    - f1: `0.6551`
  - `B` (treatment):
    - agreement: `0.8718`
    - precision: `0.6379`
    - recall: `0.6963`
    - f1: `0.6654`

- Aggregated deltas (`B - A`):
  - agreement: `+0.0041`
  - precision: `+0.0126`
  - recall: `+0.0074`
  - f1: `+0.0103`

- Helps/Hurts aggregate:
  - helps: `23`
  - hurts: `20`
  - net: `+3`

## Manual G4 Evidence Handling
- Manual source referenced:
  - `research/ab-eval/QA_SPECIMEN_V3_1.md`
- Strict context assessment:
  - Current paired rerun used `specimens_v3`.
  - QA source is explicitly for Specimen `V3.1`.
  - Therefore this source does **not clearly establish PASS** for the exact rerun context.
- Governance input status set to:
  - `visual_qa.status = FAIL`

## Gate Validation Results (Strict Governance)
- Gate output artifact:
  - `research/ab-eval/out/promo_v3_vs_v3_3_gate_results_repeats3.json`

- Outcome:
  - G1 (Agreement Delta): **FAIL** (`+0.0041`, threshold `>= +0.0100`)
  - G2 (Precision Delta): **PASS** (`+0.0126`, threshold `>= -0.0200`)
  - G3 (Helps/Hurts Net): **PASS** (`+3`, threshold `> 0`)
  - G4 (Visual QA): **FAIL** (manual evidence not context-matched for `specimens_v3` run)

## Final Promotion Decision
- Decision: **NO-GO**
- Reason:
  - Required gate set did not fully pass (`G1` and `G4` failed).

## Artifacts Produced/Updated (This Task)
- Feedback:
  - `.temp/instruction-feedback/exec-promotion-rerun-v3-v3_3-repeats.md`

- Per-arm rerun artifacts:
  - `research/ab-eval/out/promo_v3_control_r1_raw.json`
  - `research/ab-eval/out/promo_v3_control_r1_results.json`
  - `research/ab-eval/out/promo_v3_control_r2_raw.json`
  - `research/ab-eval/out/promo_v3_control_r2_results.json`
  - `research/ab-eval/out/promo_v3_control_r3_raw.json`
  - `research/ab-eval/out/promo_v3_control_r3_results.json`
  - `research/ab-eval/out/promo_v3_3_treatment_r1_raw.json`
  - `research/ab-eval/out/promo_v3_3_treatment_r1_results.json`
  - `research/ab-eval/out/promo_v3_3_treatment_r2_raw.json`
  - `research/ab-eval/out/promo_v3_3_treatment_r2_results.json`
  - `research/ab-eval/out/promo_v3_3_treatment_r3_raw.json`
  - `research/ab-eval/out/promo_v3_3_treatment_r3_results.json`

- Per-repeat comparison artifacts:
  - `research/ab-eval/out/promo_v3_vs_v3_3_r1_comparison.json`
  - `research/ab-eval/out/promo_v3_vs_v3_3_r2_comparison.json`
  - `research/ab-eval/out/promo_v3_vs_v3_3_r3_comparison.json`

- Aggregate + gate artifacts:
  - `research/ab-eval/out/promo_v3_vs_v3_3_comparison_repeats3.json`
  - `research/ab-eval/out/promo_v3_vs_v3_3_gate_results_repeats3.json`

- Promotion report:
  - `research/ab-eval/REPORT_PROMOTION_V3_V3_3_REPEATS3.md`
