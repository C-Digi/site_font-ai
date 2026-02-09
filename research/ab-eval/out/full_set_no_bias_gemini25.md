# Evaluation Report: google/gemini-2.5-flash-lite-preview-09-2025
Generated on: 2026-02-08 21:17:35

## Run Configuration
- **Model:** `google/gemini-2.5-flash-lite-preview-09-2025`
- **Source:** OpenRouter
- **Bias Prevention:** Font name removed from prompt and specimen image.
- **Population:** `candidate_pool.medium.v1.json` (Full set)
- **Ground Truth:** `labels.medium.human.v1.json` (Human labeling)

## Aggregate Metrics
- **Agreement:** 82.98%
- **Precision:** 70.09%
- **Recall:** 53.57%
- **F1 Score:** 60.73%

### Confusion Matrix
| | AI Match=1 | AI Match=0 |
|---|---|---|
| **Human Match=1** | 75 (TP) | 65 (FN) |
| **Human Match=0** | 32 (FP) | 398 (TN) |
| **Total** | | 570 |

## Notable Disagreement Patterns
Total disagreements: 97 out of 570 pairs.
