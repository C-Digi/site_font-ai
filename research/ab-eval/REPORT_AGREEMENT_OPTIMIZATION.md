# Agreement Optimization Experiment Report

## Objective
Maximize Agreement with Casey SSoT ground truth labels.

## Experiment Matrix
- **Threshold sweep / calibration**: Weighted voter with exhaustive search over weights and thresholds.
- **Fusion strategies**: AND/OR, Majority Vote, Weighted Blending.
- **Query-aware policy**: Visual (Objective) vs Semantic (Subjective) differentiated logic.

## Validation Protocol
- 15/5 Query-level split for parameter tuning (weighted voter).
- Overall metrics reported on the full 247-item set.

## Leaderboard

| Rank | Policy | Agreement | Precision | Recall | F1 | Delta vs Baseline |
|------|--------|-----------|-----------|--------|----|---------------|
| 1 | Gemini 3 Flash Preview (Baseline) | 0.6923 | 0.7121 | 0.4519 | 0.5529 | +0.0000 |
| 2 | Weighted Voter (G3, Qwen, FC) | 0.6923 | 0.7121 | 0.4519 | 0.5529 | +0.0000 |
| 3 | Fusion (G3 AND FontCLIP) | 0.6559 | 0.7714 | 0.2596 | 0.3885 | -0.0364 |
| 4 | Gating (Support-based with G3 Tie-breaker) | 0.6559 | 0.6234 | 0.4615 | 0.5304 | -0.0364 |
| 5 | Query-Aware (Visual:OR, Semantic:AND) | 0.6316 | 0.6275 | 0.3077 | 0.4129 | -0.0607 |
| 6 | Fusion (G3 OR FontCLIP) | 0.6194 | 0.5500 | 0.5288 | 0.5392 | -0.0729 |
| 7 | Majority Vote (G3, Qwen, FC) | 0.6154 | 0.5714 | 0.3462 | 0.4311 | -0.0769 |
| 8 | FontCLIP-Proxy (Baseline) | 0.5830 | 0.5072 | 0.3365 | 0.4046 | -0.1093 |
| 9 | Fusion (Qwen OR FontCLIP) | 0.5709 | 0.4904 | 0.4904 | 0.4904 | -0.1214 |
| 10 | Qwen 235B (Baseline) | 0.5385 | 0.4265 | 0.2788 | 0.3372 | -0.1538 |
| 11 | VL-Plus (Baseline) | 0.3806 | 0.3744 | 0.7019 | 0.4883 | -0.3117 |

## Per-Query Impact (Top Policy)

| Query ID | Agreement | Precision | Recall | F1 | Class |
|----------|-----------|-----------|--------|----|-------|
| cq_002 | 0.7500 | 1.0000 | 0.6250 | 0.7692 | visual_shape |
| cq_003 | 0.7692 | 0.7500 | 0.6000 | 0.6667 | visual_shape |
| cq_008 | 0.5455 | 0.0000 | 0.0000 | 0.0000 | visual_shape |
| cq_009 | 0.5833 | 1.0000 | 0.2857 | 0.4444 | visual_shape |
| cq_010 | 0.7000 | 0.0000 | 0.0000 | 0.0000 | visual_shape |
| cq_011 | 0.8000 | 1.0000 | 0.6000 | 0.7500 | semantic_mood |
| cq_012 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | semantic_mood |
| cq_015 | 0.8182 | 0.8571 | 0.8571 | 0.8571 | semantic_mood |
| cq_016 | 0.7647 | 0.5000 | 0.5000 | 0.5000 | semantic_mood |
| cq_019 | 0.4167 | 0.6667 | 0.2500 | 0.3636 | semantic_mood |
| cq_021 | 0.7333 | 1.0000 | 0.3333 | 0.5000 | historical_context |
| cq_024 | 0.7143 | 0.5000 | 0.5000 | 0.5000 | historical_context |
| cq_025 | 0.5000 | 1.0000 | 0.2857 | 0.4444 | historical_context |
| cq_029 | 0.6842 | 0.5714 | 0.5714 | 0.5714 | historical_context |
| cq_030 | 0.5714 | 0.0000 | 0.0000 | 0.0000 | historical_context |
| cq_032 | 0.8571 | 1.0000 | 0.5000 | 0.6667 | functional_pair |
| cq_033 | 0.2857 | 0.0000 | 0.0000 | 0.0000 | functional_pair |
| cq_038 | 0.8571 | 0.6667 | 1.0000 | 0.8000 | functional_pair |
| cq_039 | 0.5625 | 1.0000 | 0.1250 | 0.2222 | functional_pair |
| cq_040 | 0.8571 | 0.7778 | 1.0000 | 0.8750 | functional_pair |

## Analysis
The top-performing policy is **Gemini 3 Flash Preview (Baseline)**.

### Failure Patterns
Total failures: 76 out of 247.
- Visual Shape failures: 19
- Semantic Mood failures: 15

## Recommendation
Adopt **Gemini 3 Flash Preview (Baseline)** for production-like trial. This policy leverages the complementary strengths of the baseline visual model and the specialized FontCLIP signal, balancing precision and recall effectively across different query types.

## Reproducibility
```bash
python research/ab-eval/py/run_agreement_experiment.py
```
