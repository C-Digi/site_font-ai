# Evaluation Report: qwen/qwen3-vl-235b-a22b-instruct
Generated on: 2026-02-08 18:40:01

## Run Configuration
- **Model:** `qwen/qwen3-vl-235b-a22b-instruct`
- **Source:** OpenRouter
- **Bias Prevention:** Font name removed from prompt and specimen image.
- **Population:** `candidate_pool.medium.v1.json` (Full set)
- **Ground Truth:** `labels.medium.human.v1.json` (Human labeling)

## Aggregate Metrics
- **Agreement:** 79.30%
- **Precision:** 58.21%
- **Recall:** 55.71%
- **F1 Score:** 56.93%

### Confusion Matrix
| | AI Match=1 | AI Match=0 |
|---|---|---|
| **Human Match=1** | 78 (TP) | 62 (FN) |
| **Human Match=0** | 56 (FP) | 374 (TN) |
| **Total** | | 570 |

## Notable Disagreement Patterns
Total disagreements: 118 out of 570 pairs.
