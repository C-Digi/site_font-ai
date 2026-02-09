# Alignment Spot-Check Report: Qwen3-VL Models

Date: 2026-02-09
Scope: Alignment evaluation of two Qwen3-VL variants against Casey's human labels (`labels.medium.human.v1.json`).

## Models Evaluated

1.  **Qwen3-VL 235B (Instruct)**
    *   **Endpoint:** OpenRouter (`qwen/qwen3-vl-235b-a22b-instruct`)
    *   **Configuration:** Temperature 0.1, max tokens 512.
2.  **Qwen3-VL 8B (Instruct)**
    *   **Runtime:** Local (GPU)
    *   **Configuration:** Temperature 0.1, max tokens 512, `bfloat16` on CUDA.
    *   **Model ID:** `Qwen/Qwen3-VL-8B-Instruct` (Hugging Face)

## Summary Metrics

| Metric | Qwen3-VL 235B | Qwen3-VL 8B (Local) | GPT-5.2 (Reference) |
| :--- | :--- | :--- | :--- |
| **Agreement Rate** | 86.67% | 86.67% | 86.67% |
| **True Positives** | 2 | 2 | 2 |
| **False Positives** | 0 | 0 | 0 |
| **False Negatives** | 2 | 2 | 2 |
| **True Negatives** | 11 | 11 | 11 |

### Key Findings
- All three models (including GPT-5.2) achieved the same overall agreement rate of **86.67%** on the 15-pair spot check.
- **Disagreement on specific fonts:**
    - `cq_002 (Geometric Sans) / Ovo`: Correctly identified by **8B Local**, but missed by **235B** and **GPT-5.2**.
    - `cq_011 (Playful) / Atma`: Correctly identified by **235B** and **GPT-5.2**, but missed by **8B Local**.
    - `cq_025 (Art Deco) / Kumbh Sans`: Missed by **all three models** (Human labeled as match).
- Precision is perfect (100%) for all models in this small sample, but Recall is 50%.

## Artifacts

- **Metrics/Details (JSON):**
    - `research/ab-eval/out/spot_check_alignment_qwen3vl_235b.json`
    - `research/ab-eval/out/spot_check_alignment_qwen3vl_8b_local.json`
- **Human Review UI (HTML):**
    - `research/ab-eval/out/alignment_conflict_review.html`
    - *Features:* Shows only disagreements, rendered specimens, and provides an exportable favorite-model selection.

## Commands Executed

```powershell
# 1. Run alignment evaluation for both models
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_spot_check_alignment_models.py

# 2. Generate interactive conflict-only HTML
python research/ab-eval/py/gen_alignment_review_html.py
```

## Caveats & Local Setup
- **GPU Requirement:** The local 8B model requires ~16GB+ VRAM for comfortable inference in `bfloat16`. 
- **Dependencies:** Uses `transformers`, `qwen-vl-utils`, and `torch` (CUDA) from the `.venv-ab-eval` environment.
- **Latency:** Local 8B inference latency was ~8-12s per image on the current hardware, compared to ~3s for the 235B OpenRouter endpoint.
- **Small Sample:** Results are based on 15 font/query pairs. Larger scale testing is recommended for definitive model ranking.
