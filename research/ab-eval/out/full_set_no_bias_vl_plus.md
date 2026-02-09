# Evaluation Report: qwen/qwen-vl-plus
Generated on: 2026-02-08 19:07:31

## Run Configuration
- **Model:** `qwen/qwen-vl-plus`
- **Source:** OpenRouter
- **Bias Prevention:** Font name removed from prompt and specimen image.
- **Population:** `candidate_pool.medium.v1.json` (Full set)
- **Ground Truth:** `labels.medium.human.v1.json` (Human labeling)

## Aggregate Metrics
- **Agreement:** 66.49%
- **Precision:** 40.23%
- **Recall:** 75.00%
- **F1 Score:** 52.37%

### Confusion Matrix
| | AI Match=1 | AI Match=0 |
|---|---|---|
| **Human Match=1** | 105 (TP) | 35 (FN) |
| **Human Match=0** | 156 (FP) | 274 (TN) |
| **Total** | | 570 |

## Notable Disagreement Patterns
Total disagreements: 191 out of 570 pairs.
