# Production-Like Trial Report: G3 + V3 Policy + 0.9 Gating

## Overview
This report documents the results of the recommended next production-like trial policy, utilizing the strongest model (Gemini 3 Flash Preview via Gemini API), Specimen V3 (Split View), Prompt V3 (Master Auditor Rubric), and a 0.9 confidence gating policy.

## Command Run
```bash
python research/ab-eval/py/run_production_trial.py --model gemini-3-flash-preview --gate 0.9
```

## Metrics Comparison
Comparing the new trial results against the recomputed baseline (G3 V2) on the same 247 pairs from the amended SSoT (`full_set_review_export_1770612809775.json`).

| Metric | Baseline (G3 V2) | **Trial (G3 V3 Gated)** | Delta |
| :--- | :--- | :--- | :--- |
| **Agreement** | 0.6397 | **0.6721** | **+3.24%** |
| **Precision** | 0.6415 | **0.7805** | **+13.90%** |
| **Recall** | **0.7556** | 0.7111 | -4.45% |
| **F1 Score** | 0.6939 | **0.7442** | **+5.03%** |

### Confusion Matrix (G3 V3 Gated)
| | AI Match=1 | AI Match=0 |
|---|---|---|
| **Human Match=1** | 32 (TP) | 13 (FN) |
| **Human Match=0** | 9 (FP) | 134 (TN) |
| **Total** | | 247 |

## Impact Analysis
- **Total pairs evaluated:** 247
- **Helped:** 15 pairs corrected (Baseline was wrong, Trial is correct).
- **Hurt:** 7 pairs regressed (Baseline was correct, Trial is wrong).
- **Net Gain:** +8 correct decisions.

### Per-Query Impact (Top Gains)
- `cq_033` (Geometric sans): +3 gain. The Specimen V3 and Prompt V3 rubric better handle technical geometric requirements.
- `cq_009` (Luxury/High-end): +3 gain. Improved visual density helps distinguish "luxury" from generic "elegant".
- `cq_016` (Historical context): +2 gain.

## Recommendation
**GO FOR PROMOTION.**
The 13.9% boost in Precision is decisive for production quality, as it significantly reduces the rate of false positives (irrelevant font recommendations). While there is a slight drop in Recall due to the 0.9 gating, the overall Agreement and F1 score are substantially higher. The Specimen V3 + Prompt V3 combination on Gemini 3 successfully pushes the performance closer to the 70% Agreement barrier.

## Artifacts
- Results: `research/ab-eval/out/g3_v3_gated_results.json`
- Impact Summary: `research/ab-eval/out/g3_v3_gated_impact_summary.md`
- Execution Script: `research/ab-eval/py/run_production_trial.py`
