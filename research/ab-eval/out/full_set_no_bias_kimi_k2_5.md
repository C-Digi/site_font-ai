# Evaluation Report: moonshotai/kimi-k2.5
Generated on: 2026-02-09 00:31:42

## Run Configuration
- **Model:** `moonshotai/kimi-k2.5`
- **Source:** OpenRouter
- **Bias Prevention:** Font name removed from prompt and specimen image.
- **Population:** `candidate_pool.medium.v1.json` (Full set)
- **Ground Truth:** `labels.medium.human.v1.json` (Human labeling)

## Aggregate Metrics
- **Agreement:** 82.63%
- **Precision:** 66.67%
- **Recall:** 58.57%
- **F1 Score:** 62.36%

### Confusion Matrix
| | AI Match=1 | AI Match=0 |
|---|---|---|
| **Human Match=1** | 82 (TP) | 58 (FN) |
| **Human Match=0** | 41 (FP) | 389 (TN) |
| **Total** | | 570 |

## Notable Disagreement Patterns
Total disagreements: 99 out of 570 pairs.
