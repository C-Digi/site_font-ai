# Consolidated Description Model Bakeoff Report (2026-02-07)

## 1. Executive Summary
This report aggregates findings from the initial smoke bakeoff and the subsequent large-model probes (32B/235B) to select a production model for vision-grounded font descriptions.

**Recommendation:** Promote **Qwen3-VL-235B (Instruct)** as the provisional production model for the 200-font answer key generation.

## 2. Comparison Metrics

| Model | Provider | Success Rate | Avg Latency | Cost (Est/Font) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Qwen3-VL-235B-A22B** | OpenRouter | **100% (259/259)** | 5.45s | ~$0.0003 | Superior depth, stable, low cost. |
| **Qwen3-VL-32B** | OpenRouter | **100% (259/259)** | 3.28s | ~$0.0005 | Faster, high precision, slightly less nuance. |
| Qwen3-VL-8B | Local/OR | 100% | 2.65s (OR) | ~$0.0002 | Good baseline, lacks 235B's vocabulary. |
| Gemini 2.5 Flash Lite | Gemini | 100% | 1.37s | <$0.0001 | Fastest, but occasionally misses subtle terminals. |
| Gemini 3 Flash | Gemini | 90% | 8.16s | ~$0.0020 | High quality but unstable (503 errors). |

## 3. Qualitative Assessment

### Winner: Qwen3-VL-235B-A22B
- **Visual Precision:** Correctingly identifies "tapered terminals" and "geometric counters" where smaller models generalize.
- **Consistency:** High agreement between mood tags and technical summary.
- **Formatting:** 100% direct JSON parse rate across all test runs.

### Challenger: Qwen3-VL-32B
- **Speed:** ~40% faster than 235B with very similar quality for 90% of fonts.
- **Suitability:** Excellent candidate if latency becomes a constraint in background workers.

## 4. Full-Run Artifacts
The 200-font corpus has been fully processed by both the winner and challenger models:
- **Winner (235B):** `research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl` (rows where model=235b)
- **Challenger (32B):** `research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl` (rows where model=32b)

## 5. Next Steps: Human Review
The next blocker is a formal human review of the generated descriptions to validate stylistic fidelity before these descriptions are used to generate the final vector embeddings.
