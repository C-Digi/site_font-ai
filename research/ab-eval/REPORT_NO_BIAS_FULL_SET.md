# Full-Set Evaluation Report (No-Bias Run)

## Overview
This report documents the evaluation of two vision-language models on a font retrieval task using a comprehensive dataset (570 pairs) with all potential font-name bias removed.

## Bias Removal Methodology
1.  **Prompt Modification**: The font name was explicitly removed from the LLM prompt. The model now only receives the query text and the specimen image.
2.  **Specimen Re-rendering**: All 189 fonts in the medium dataset were re-rendered into 1024x1024 specimens. The footer, which previously contained the font name, was updated to say "Specimen v2 - Deterministic 1024 - No Label".
3.  **Audit**: Evaluation scripts (`research/ab-eval/py/run_full_comparison.py`) were verified to ensure no metadata or identifying strings are passed to the model-visible payload.

## Execution Details
- **Command**: `python research/ab-eval/py/run_full_comparison.py --model [MODEL] --output [OUTPUT]`
- **Specimens**: `research/ab-eval/out/specimens_v2_medium_nobias/`
- **Ground Truth**: `research/ab-eval/data/labels.medium.human.v1.json` (Human labeling by Casey)

## Aggregate Metrics

| Model | Agreement | Precision | Recall | F1 Score | TP | FP | FN | TN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Qwen 235B** | 79.30% | 58.21% | 55.71% | 56.93% | 78 | 56 | 62 | 374 |
| **Qwen VL Plus** | 66.49% | 40.23% | 75.00% | 52.37% | 105 | 156 | 35 | 274 |
| **Kimi K2.5** | 82.63% | 66.67% | 58.57% | 62.36% | 82 | 41 | 58 | 389 |

*Note: Total pairs = 570.*

## Human Review UI Updates
The alignment review HTML has been regenerated (`research/ab-eval/out/alignment_full_set_review.html`) with the following improvements:
- **Faster Controls**: Replaced `<select>` dropdowns with single-click button groups for "Correct", "Incorrect", and "Ambiguous" ratings.
- **Side-by-Side Comparison**: Human (Casey) vs Qwen 235B vs Qwen VL Plus.
- **No-Bias Artifacts**: Linked to the new no-bias specimen images.
- **JSON Export**: Maintained the ability to export results for further analysis.

## Key Observations
- **Qwen 235B** remains the more conservative and accurate model (higher precision and agreement).
- **Qwen VL Plus** has higher recall but significantly more false positives, suggesting a lower internal threshold for "matching" or a more liberal interpretation of queries.
- Removing the font name bias resulted in a clean benchmark where model performance is strictly based on visual analysis of the specimen against the query text.

## Artifacts
- **Results (235B)**: `research/ab-eval/out/full_set_no_bias_qwen235b.json`
- **Results (VL Plus)**: `research/ab-eval/out/full_set_no_bias_vl_plus.json`
- **Review HTML**: `research/ab-eval/out/alignment_full_set_review.html`
- **Specimens**: `research/ab-eval/out/specimens_v2_medium_nobias/`
