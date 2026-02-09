# Alignment Spot-Check Report (Batched)

This report compares `qwen/qwen3-vl-235b-a22b-instruct` and `qwen/qwen-vl-plus` on a spot-check scope of 15 font-query pairs.

## Commands Run
```powershell
# Run the evaluation with batching
python research/ab-eval/py/run_spot_check_alignment_models.py

# Generate the conflict review HTML
python research/ab-eval/py/gen_alignment_review_html.py
```

## Batching Strategy
- Decisions are grouped by **font specimen image**.
- Each LLM request evaluates up to **10 queries per font**.
- The prompt provides a list of queries and requires a JSON response with a matching list of 0/1 results and a shared reasoning (`thought`).
- This reduces redundant image processing and latency for fonts that appear across multiple queries in a single evaluation run.

## Model Configurations
- **Model A:** `qwen/qwen3-vl-235b-a22b-instruct` (OpenRouter)
- **Model B:** `qwen/qwen-vl-plus` (OpenRouter)
- **Parameters:** Temperature 0.1, Max Tokens 512 (per batch).
- **Specimen Context:** Specimen v2 images (including legibility pairs like `O0`, `il1I`, etc.).

## Key Metrics

| Model | Agreement Rate | TP | FP | FN | TN |
|-------|----------------|----|----|----|----|
| **Qwen 235B** | **86.67%** | 2 | 0 | 2 | 11 |
| **Qwen VL Plus** | 53.33% | 2 | 5 | 2 | 6 |

### Observations
- **Qwen 235B** demonstrates significantly higher alignment with Casey's labels, particularly in avoiding False Positives.
- **Qwen VL Plus** struggled with several queries, often hallucinating matches for fonts that were clearly non-geometric or monospaced when the query asked for serifs (e.g., `Solitreo` for luxury serif).

## Artifact Paths
- **Detailed JSON (235B):** `research/ab-eval/out/spot_check_alignment_qwen3vl_235b.json`
- **Detailed JSON (VL Plus):** `research/ab-eval/out/spot_check_alignment_vl_plus.json`
- **Review HTML:** `research/ab-eval/out/alignment_conflict_review.html`

## Human Review Interface
The updated `alignment_conflict_review.html` allows:
- Side-by-side comparison of **Casey (Human Reference)**, **Qwen 235B**, and **Qwen VL Plus**.
- Filtering for cases where at least one model differs from Casey.
- Per-decision voting (Correct/Incorrect/Ambiguous).
- Overall model preference selection.
- JSON Export of review data including labels, user decisions, and timestamps.
