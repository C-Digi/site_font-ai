# Comprehensive Model Comparison Report (Updated SSoT)

Generated on: 2026-02-09T04:53:29.774Z

## Overview
This report compares multiple vision models on the font discovery task using the amended human Source of Truth (SSoT) labels from `full_set_review_export_1770612809775.json`.

## Batching Implementation Summary
- Upgraded `run_full_comparison.py` to support batched requests (up to 10 queries per specimen).
- Ported logic from `run_spot_check_alignment_models.py`.
- Ensured deterministic behavior and bias prevention (no font names in prompt).

## Commands Executed
1. **Evaluation Run:**
   ```powershell
   .\.venv-ab-eval\Scripts\python research/ab-eval/py/run_full_comparison.py --model gemini-3-flash-preview --output full_set_no_bias_gemini3flashpreview.json
   ```
2. **Metrics Recomputation:**
   ```powershell
   .\.venv-ab-eval\Scripts\python research/ab-eval/py/recompute_all_metrics.py
   ```

## Coverage & Totals
- **Total Candidate Pairs (Full Set):** 570 pairs across 189 fonts.
- **SSoT Coverage (Amended):** 247 pairs across the same font/query space.
- **Gemini-3 Run Coverage:** 100% of candidate pool (570/570).

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

## Comparison Notes
- **Gemini 3 Flash Preview** demonstrates a significant leap in performance over Gemini 2.5 and previous models.
- **Recall (0.7556)** is particularly strong, capturing more true positive matches than any other model tested.
- **Precision (0.6415)** is also the highest among the group, indicating fewer false positives despite the high recall.
- **VL-Plus** (Qwen 8B) shows high recall but extremely low precision, leading to a poor overall F1.
- **Qwen 235B** (via OpenRouter) performed surprisingly worse than the Gemini family in this specific typography visual judging task.

## Artifact Paths
- Amended SSoT: `research/ab-eval/out/full_set_review_export_1770612809775.json`
- Qwen 235B Results: `research/ab-eval/out/full_set_no_bias_qwen235b_updated_ssot.json`
- VL-Plus Results: `research/ab-eval/out/full_set_no_bias_vl_plus_updated_ssot.json`
- Gemini 2.5 Results: `research/ab-eval/out/full_set_no_bias_gemini25_updated_ssot.json`
- Gemini 3 Results: `research/ab-eval/out/full_set_no_bias_gemini3flashpreview_updated_ssot.json`
