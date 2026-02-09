# Comprehensive Model Comparison Report (Updated SSoT)

Generated on: 2026-02-09T04:53:29.774Z

## Overview
This report compares multiple vision models on the font discovery task using the amended human Source of Truth (SSoT) labels from `full_set_review_export_1770612809775.json`.

## Batching Implementation Summary
- Upgraded `run_full_comparison.py` to support batched requests (up to 10 queries per specimen).
- Ported logic from `run_spot_check_alignment_models.py`.
- Ensured deterministic behavior and bias prevention (no font names in prompt).

## Amended SSoT Parsing Assumptions
- Used `casey_label` from the review export JSON as the canonical ground truth.
- Mapping is performed using `(query_id, font_name)` pairs.
- Only pairs present in the review export are included in the recomputed metrics.

## Updated Metrics Table

| Model | Agreement | Precision | Recall | F1 | TP | FP | FN | TN | Total |
|-------|-----------|-----------|--------|----|----|----|----|----|-------|
| Qwen 235B | 0.4939 | 0.3158 | 0.4000 | 0.3529 | 18 | 39 | 27 | 104 | 247 |
| VL-Plus | 0.2024 | 0.1921 | 0.6444 | 0.2959 | 29 | 122 | 16 | 21 | 247 |
| Gemini 2.5 Flash Lite | 0.6032 | 0.5714 | 0.5333 | 0.5517 | 24 | 18 | 21 | 125 | 247 |
| Gemini 3 Flash Preview | 0.6397 | 0.6415 | 0.7556 | 0.6939 | 34 | 19 | 11 | 124 | 247 |
| Kimi K2.5 | 0.6235 | 0.5932 | 0.7778 | 0.6731 | 35 | 24 | 10 | 119 | 247 |

## Artifact Paths
- Amended SSoT: `research/ab-eval/out/full_set_review_export_1770612809775.json`
- Qwen 235B Results: `research/ab-eval/out/full_set_no_bias_qwen235b_updated_ssot.json`
- VL-Plus Results: `research/ab-eval/out/full_set_no_bias_vl_plus_updated_ssot.json`
- Gemini 2.5 Results: `research/ab-eval/out/full_set_no_bias_gemini25_updated_ssot.json`
- Gemini 3 Results: `research/ab-eval/out/full_set_no_bias_gemini3flashpreview_updated_ssot.json`
- Kimi K2.5 Results: `research/ab-eval/out/full_set_no_bias_kimi_k2_5_updated_ssot.json`

## Execution Log (Kimi K2.5)
```powershell
# 1. Execute full comprehensive run (570 pairs, no-bias pipeline)
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_full_comparison.py --model moonshotai/kimi-k2.5 --output full_set_no_bias_kimi_k2_5.json

# 2. Recompute metrics against amended SSoT
.\.venv-ab-eval\Scripts\python research/ab-eval/py/recompute_all_metrics.py
```

## Relative Comparison Note (Kimi K2.5)
Kimi K2.5 demonstrates strong performance, achieving the highest recall (0.7778) among all tested models, slightly edging out Gemini 3 Flash Preview (0.7556). While its precision (0.5932) is lower than Gemini 3 (0.6415), its F1 score (0.6731) is very competitive, making it a top-tier contender for the font discovery task.
