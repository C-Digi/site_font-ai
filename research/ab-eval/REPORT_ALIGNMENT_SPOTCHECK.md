# AI-vs-Human Alignment Spot-Check (Track A - Medium Labels)

## Overview
This report summarizes a targeted alignment check between AI judgments (`openai/gpt-5.2` via OpenRouter) and human ground-truth labels provided by "Casey".

## Setup
- **Model**: `openai/gpt-5.2` (via OpenRouter)
- **Settings**: `include_reasoning: true`, `temperature: 0.1`
- **Specimen**: Specimen v2 (1024x1024, deterministic, with `O0` legibility pair tweak).
- **Data Source**: `research/ab-eval/data/labels.medium.human.v1.json` (Human reference labels for 20 complex queries).
- **Spot-Check Scope**: 5 queries, top 3 candidates each (15 total judgments).

## Commands Used
1. **Apply Specimen Tweak**: Verified `O0` in `research/ab-eval/py/render_specimen_v2.py`.
2. **Re-render Specimens**: 
   ```bash
   python research/ab-eval/py/render_specimen_v2.py --corpus research/ab-eval/data/corpus.200.json --out research/ab-eval/out/specimens_v2_medium
   ```
3. **Run Alignment Pass**:
   ```bash
   python research/ab-eval/py/run_spot_check_alignment.py
   ```

## Metrics Summary
| Metric | Value |
| --- | --- |
| **Total Pairs Evaluated** | 15 |
| **Agreement Rate** | 86.67% |
| **True Positives (TP)** | 2 |
| **False Positives (FP)** | 0 |
| **False Negatives (FN)** | 2 |
| **True Negatives (TN)** | 11 |

### Interpretation
- **High Precision (0 FP)**: The AI is currently very conservative; it didn't recommend anything the human rejected.
- **Recall Gap (2 FN)**: 
  - `Ovo` was missed for "geometric sans".
  - `Kumbh Sans` was missed for "art deco".
- **Success Case**: `IBM Plex Mono` was correctly identified for "coding font with 0 and O distinction," validating the `O0` specimen tweak.

## Artifacts
- **Judgment Details**: `research/ab-eval/out/spot_check_alignment.json` (includes model thoughts).
- **Updated Specimens**: `research/ab-eval/out/specimens_v2_medium/`

## Key Takeaway
The AI shows strong alignment with human judgment on clear positive/negative matches. The `O0` tweak provides sufficient visual evidence for the model to reason about specific legibility requirements. The False Negatives suggest a need for slightly more permissive relevance thresholds or improved prompt nuance for stylistic categories like "art deco".
