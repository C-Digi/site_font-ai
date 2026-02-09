# Evaluation Report: gemini-3-flash-preview
Generated on: 2026-02-08 22:05:46

## Run Configuration
- **Model:** `gemini-3-flash-preview`
- **Source:** Gemini API
- **Bias Prevention:** Font name removed from prompt and specimen image.
- **Population:** `candidate_pool.medium.v1.json` (Full set)
- **Ground Truth:** `labels.medium.human.v1.json` (Human labeling)

## Aggregate Metrics
- **Agreement:** 82.63%
- **Precision:** 65.41%
- **Recall:** 62.14%
- **F1 Score:** 63.74%

### Confusion Matrix
| | AI Match=1 | AI Match=0 |
|---|---|---|
| **Human Match=1** | 87 (TP) | 53 (FN) |
| **Human Match=0** | 46 (FP) | 384 (TN) |
| **Total** | | 570 |

## Notable Disagreement Patterns
Total disagreements: 99 out of 570 pairs.
