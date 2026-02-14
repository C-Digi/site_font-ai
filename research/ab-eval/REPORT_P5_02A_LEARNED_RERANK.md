# P5-02A Learned Reranker Trial Report

**Run ID:** `p5_02a_learned_rerank`
**Date:** 2026-02-14
**Status:** NO-GO

---

## 1. Executive Summary

**Decision: NO-GO** - The learned cross-encoder reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`) with fusion-based calibration fails G2 (Precision Delta) with a -14.28% regression and G3 (Helps/Hurts Net) with net 0. While G1 (Agreement) passes with +19.03%, the precision loss and neutral helps/hurts balance indicate the reranker does not provide sufficient discriminative signal for font relevance.

---

## 2. Global Metrics Table

| Metric | v3 (Champion) | p5_02a_learned_rerank | Delta |
|--------|---------------|------------------------|-------|
| Agreement | 0.6761 | 0.8664 | +0.1903 |
| Precision | 0.7857 | 0.6429 | -0.1428 |
| Recall | 0.7333 | 0.6000 | -0.1333 |
| F1 | 0.7586 | 0.6207 | -0.1379 |

---

## 3. Gate Status

| Gate | Metric | Threshold | Value | Status |
|------|--------|-----------|-------|--------|
| G1 | Agreement Delta | >= +1.0% | +19.03% | **PASS** |
| G2 | Precision Delta | >= -2.0% | -14.28% | **FAIL** |
| G3 | Helps/Hurts Net | > 0 | 0 | **FAIL** |
| G4 | Visual QA | Zero clipping | Manual | **PENDING** |

**Overall: FAIL (NO-GO)** - G2 and G3 failures block promotion.

---

## 4. Threshold Sweep Results

| Threshold | Agreement | Precision | Recall | F1 |
|-----------|-----------|-----------|--------|-----|
| 0.40 | 0.8664 | 0.6304 | 0.6444 | 0.6374 |
| **0.45** | **0.8664** | **0.6429** | **0.6000** | **0.6207** | * (best) |
| 0.50 | 0.8623 | 0.6341 | 0.5778 | 0.6047 |

Best threshold selected by Agreement (tie-break: Precision): **0.45**

---

## 5. Implementation Details

### Reranker Approach
- **Type:** Learned cross-encoder reranker
- **Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2` (sentence-transformers)
- **Top-K:** 20 candidates per query
- **Payload:** `name + category + tags + description` (structured text)

### Calibration/Fusion
- **Formula:** `final_score = 0.6 * normalized_sim + 0.4 * rerank_score`
- **Normalization:** Per-query min-max with epsilon safety
- **Decision Threshold:** 0.45 (fusion score)

### Determinism
- **Seed:** 42
- **Sorting:** Stable sort by confidence (descending), then font name (ascending)
- **Model:** Eval mode for deterministic inference

### Variant ID
- `p5_02a_learned_rerank`

---

## 6. Helps/Hurts Analysis

**Helps (7 cases):** Queries where reranker recovered correct matches
**Hurts (7 cases):** Queries where reranker introduced errors
**Net: 0** (fails G3 requirement of > 0)

### Top Helps
| Query ID | Font | Human | v3 Pred | p5_02a Pred |
|----------|------|-------|---------|-------------|
| (See comparison artifact for full details) |

### Top Hurts
| Query ID | Font | Human | v3 Pred | p5_02a Pred |
|----------|------|-------|---------|-------------|
| (See comparison artifact for full details) |

---

## 7. Analysis

### Why G2 and G3 Failed

1. **Domain Mismatch:** The MS-MARCO cross-encoder is trained on web search relevance, not typographic/visual font matching. Font relevance signals (geometric, luxury, playful) are semantically distant from web document relevance.

2. **Payload Limitations:** The text payload (name + category + tags + description) lacks the visual richness needed for font relevance. Font names are often opaque (e.g., "Alata", "Geom"), and descriptions are sparse.

3. **False Positive Introduction:** The fusion approach lowers the effective decision barrier, introducing false positives that hurt precision without corresponding true positive recovery.

4. **Neutral Helps/Hurts:** The 7/7 split indicates the reranker is essentially random in its corrections - it helps as often as it hurts, providing no net benefit.

### Comparison to P5-01 (Token-Overlap Reranker)

| Metric | P5-01 (Token) | P5-02A (Learned) | Delta |
|--------|---------------|------------------|-------|
| Agreement Delta | +19.84% | +19.03% | -0.81% |
| Precision Delta | -13.35% | -14.28% | -0.93% |
| Helps/Hurts Net | +2 | 0 | -2 |

The learned reranker performs slightly worse than the simple token-overlap approach, suggesting that:
- MS-MARCO's web search training does not transfer to font relevance
- The text payload is insufficient for semantic font matching

---

## 8. Recommendations

1. **Do NOT promote** `p5_02a_learned_rerank` to production
2. **Future work:** Consider domain-specific reranker training with font relevance labels
3. **Alternative path:** Focus on hard-negative curation and query expansion rather than post-hoc reranking
4. **Visual signals:** Explore multimodal rerankers that can process font specimens (images) alongside text

---

## 9. Artifacts

- Comparison: `research/ab-eval/out/p5_02a_v3_vs_p5_02a_comparison.json`
- Gates: `research/ab-eval/out/p5_02a_v3_vs_p5_02a_gates.json`
- Script: `research/ab-eval/py/run_p5_02a_learned_rerank.py`

---

## 10. Reproducibility

- **Seed:** 42
- **Data:** SSoT `full_set_review_export_1770612809775.json`
- **Baseline:** v3 champion results `g3_v3_gated_results.json`
- **Model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Dependencies:** `sentence-transformers` (installed via pip)

### Environment Setup
```powershell
.\.venv-ab-eval\Scripts\pip install sentence-transformers
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_p5_02a_learned_rerank.py
```
