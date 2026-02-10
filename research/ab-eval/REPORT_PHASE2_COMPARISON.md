# Comprehensive Model Comparison Report (Phase 2)

**Generated on:** 2026-02-10
**Evaluation Set:** Full-set evaluation population (247 pairs)
**Ground Truth (SSoT):** `research/ab-eval/out/full_set_review_export_1770612809775.json` (casey_label)
**Specimen Version:** V3 (Rendering fixes)
**Prompt Version:** V3 (Master Typography Auditor)
**Confidence Policy:** 0.9 Gating (Matches with confidence < 0.9 are treated as 0)

## 1. Capability Verification: Pony Alpha
**Model ID:** `openrouter/pony-alpha`
**Result:** **BLOCKED / INELIGIBLE**
**Evidence:** 
- Practical probe using `research/ab-eval/py/verify_pony_alpha.py` returned: `{"error":{"message":"No endpoints found that support image input","code":404}}`.
- OpenRouter documentation confirms input modalities are limited to `text`.
- Model is optimized for coding, reasoning, and roleplay, but lacks native vision capabilities required for Specimen V3 analysis.

## 2. Comprehensive Evaluation Metrics

| Model | Agreement | Precision | Recall | F1 | TP | FP | FN | TN | Total |
|---|---|---|---|---|---|---|---|---|---|
| **Gemini 3 Flash (Baseline)** | 0.6761 | 0.7857 | 0.7333 | 0.7586 | 33 | 9 | 12 | 134 | 247 |
| **Gemini 3 Pro Preview** | **0.6842** | **0.8611** | 0.6889 | **0.7654** | 31 | 5 | 14 | 138 | 247 |
| **GPT-5.2** | 0.6275 | 1.0000 | 0.2667 | 0.4211 | 12 | 0 | 33 | 143 | 247 |
| **Pony Alpha** | - | - | - | - | - | - | - | - | - |

*Note: Deltas vs Baseline (Gemini 3 Flash):*
- **Gemini 3 Pro Preview**: +0.81% Agreement, +7.54% Precision, -4.44% Recall, +0.68% F1.
- **GPT-5.2**: -4.86% Agreement, +21.43% Precision (Perfect), -46.66% Recall, -33.75% F1.

## 3. Failure Pattern Analysis

### Gemini 3 Pro Preview
- **Strengths**: Higher precision than Flash. Fewer false positives (5 vs 9). Very reliable "No" judgments.
- **Weaknesses**: Slightly more False Negatives (14 vs 12). Sometimes over-analyzes technical details and misses the broader "vibe" (e.g., missed `Faster One` for playful/quirky because it focused on racing speed lines).

### GPT-5.2 (OpenRouter)
- **Strengths**: **Perfect Precision (1.0)**. In this trial, it produced ZERO False Positives. If GPT-5.2 says a font matches with high confidence, it is almost certainly correct.
- **Weaknesses**: **Severe Recall issues**. 24 of its "match" votes had confidence scores below the 0.9 threshold and were gated to 0. It is extremely cautious and hesitant to commit to a match, leading to 33 False Negatives. It often correctly identifies the style but fails to bridge the gap to the specific user intent query if there is any ambiguity.

## 4. Recommendation
1. **Promote Gemini 3 Pro Preview** as the new gold-standard auditor for human-in-the-loop validation or complex enrichment tasks where precision is paramount.
2. **Retain Gemini 3 Flash** for high-volume JIT seeding/auditing if cost/latency is a factor, as it still offers the best balance of recall and speed.
3. **Use GPT-5.2 as a "Strict Validator"**: If a font needs to pass a "zero-hallucination" bar, GPT-5.2 is the best candidate, but expect it to reject many valid fonts.
4. **Discard Pony Alpha** for vision-based typography tasks.

## 5. Artifacts
- Raw results: `research/ab-eval/out/g3_pro_v3_gated_raw.json`, `research/ab-eval/out/gpt52_v3_gated_raw.json`
- Metrics: `research/ab-eval/out/metrics_g3_pro_v3_gated_raw.json`, `research/ab-eval/out/metrics_gpt52_v3_gated_raw.json`
- Analysis Scripts: `research/ab-eval/py/run_phase2_comparisons.py`, `research/ab-eval/py/verify_pony_alpha.py`, `research/ab-eval/py/analyze_failures.py`
