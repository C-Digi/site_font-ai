# Comprehensive 235B Evaluation Report
Generated on: 2026-02-08 17:31:59

## Run Configuration
- **Model:** `qwen/qwen3-vl-235b-a22b-instruct`
- **Source:** OpenRouter
- **Population:** `candidate_pool.medium.v1.json` (ALL pairs)
- **Ground Truth:** `labels.medium.human.v1.json` (Human labeling)

## Aggregate Metrics
- **Agreement:** 82.28%
- **Precision:** 71.43%
- **Recall:** 46.43%
- **F1 Score:** 56.28%

### Confusion Matrix
| | AI Match=1 | AI Match=0 |
|---|---|---|
| **Human Match=1** | 65 (TP) | 75 (FN) |
| **Human Match=0** | 26 (FP) | 404 (TN) |
| **Total** | | 570 |

## Notable Disagreement Patterns
Total disagreements: 101 out of 570 pairs.

### Highest Disagreement Queries
- **cq_016**: 9 disagreements
- **cq_002**: 8 disagreements
- **cq_003**: 8 disagreements
- **cq_009**: 8 disagreements
- **cq_012**: 8 disagreements
