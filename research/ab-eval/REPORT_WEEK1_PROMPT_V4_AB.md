# Week 1 Evaluation Report — Gemini 3 Pro + Prompt V3 vs Prompt V4

## Scope Executed

- Champion model path promoted to Gemini 3 Pro trial path (`google/gemini-3-pro-preview`).
- Prompt V4 (Intent-Aware Auditor) implemented and wired for A/B through runtime flag.
- Full-set A/B executed against amended SSoT: `research/ab-eval/out/full_set_review_export_1770612809775.json`.
- Gating policy held constant at confidence gate `0.9` (same production-like policy).

## Configuration

- Dataset / SSoT: `research/ab-eval/out/full_set_review_export_1770612809775.json`
- Specimen: V3 split-view (`research/ab-eval/out/specimens_v3/`)
- Model: `gemini-3-pro-preview`
- Control: Prompt V3
- Treatment: Prompt V4 (Intent-Aware Auditor)
- Gate: `0.9` (unchanged)
- Key strategy: multi-key cycling via `--keys-file key.md` to avoid single-key quota exhaustion.

## Commands Run

```powershell
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v4 --output week1_smoke_g3pro_v4_keys.json --max-fonts 2 --keys-file key.md

.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --keys-file key.md --cache-output week1_g3pro_promptv3_control_raw.json --output week1_g3pro_promptv3_control_results.json

.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v4 --keys-file key.md --cache-output week1_g3pro_promptv4_treatment_raw.json --output week1_g3pro_promptv4_treatment_results.json

.\.venv-ab-eval\Scripts\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/week1_g3pro_promptv3_control_results.json --treatment research/ab-eval/out/week1_g3pro_promptv4_treatment_results.json --output research/ab-eval/out/week1_prompt_v3_vs_v4_comparison.json
```

## Coverage

- Common evaluation coverage: **247 / 247** pairs
- Binary-labeled pairs considered in confusion accounting: **188**
- Unknown/other labels retained in denominator for agreement parity with existing scorer

## Metrics (Primary = Agreement)

| Arm | Agreement | Precision | Recall | F1 | TP | FP | FN | TN | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Control (G3 Pro + Prompt V3) | 0.6761 | 0.8333 | 0.6667 | 0.7407 | 30 | 6 | 15 | 137 | 247 |
| Treatment (G3 Pro + Prompt V4) | 0.6640 | 0.7561 | 0.6889 | 0.7209 | 31 | 10 | 14 | 133 | 247 |
| Delta (V4 - V3) | -0.0121 | -0.0772 | +0.0222 | -0.0198 | +1 | +4 | -1 | -4 | 0 |

## Per-query Helps / Hurts

- Helps: **5**
- Hurts: **8**
- Net: **-3**

### Helps by query_id

- `cq_003`: 1
- `cq_015`: 1
- `cq_016`: 1
- `cq_025`: 1
- `cq_039`: 1

### Hurts by query_id

- `cq_002`: 1
- `cq_010`: 1
- `cq_011`: 2
- `cq_015`: 1
- `cq_016`: 1
- `cq_029`: 1
- `cq_040`: 1

## Recommendation

Do **not** replace Prompt V3 with Prompt V4 in Week 1.

Rationale:

- Primary metric regressed (Agreement: `-1.21` pts).
- Precision regressed materially (`-7.72` pts), which conflicts with current strict-gated production-like objective.
- Recall improved slightly (`+2.22` pts) but not enough to offset precision/agreement losses.
- Net helps/hurts is negative (`-3`).

## Artifacts Produced

- `research/ab-eval/out/week1_smoke_g3pro_v4_keys.json`
- `research/ab-eval/out/week1_g3pro_promptv3_control_raw.json`
- `research/ab-eval/out/week1_g3pro_promptv3_control_results.json`
- `research/ab-eval/out/week1_g3pro_promptv4_treatment_raw.json`
- `research/ab-eval/out/week1_g3pro_promptv4_treatment_results.json`
- `research/ab-eval/out/week1_prompt_v3_vs_v4_comparison.json`

