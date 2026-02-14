# P5-01 Rerank + Calibration Trial Report

**Run ID:** `p5_01_rerank_calib`
**Date:** 2026-02-14
**Status:** NO-GO

---

## 1. Executive Summary

**Decision: NO-GO** - The deterministic token-overlap reranker with fusion-based calibration fails G2 (Precision Delta) with a -13.35% regression. While G1 (Agreement) and G3 (Helps/Hurts) pass, the precision loss is too large for production consideration.

---

## 2. Global Metrics Table

| Metric | v3 (Champion) | p5_01_rerank_calib | Delta |
|--------|---------------|---------------------|-------|
| Agreement | 0.6761 | 0.8745 | +0.1984 |
| Precision | 0.7857 | 0.6522 | -0.1335 |
| Recall | 0.7333 | 0.6667 | -0.0666 |
| F1 | 0.7586 | 0.6593 | -0.0993 |

---

## 3. Gate Status

| Gate | Metric | Threshold | Value | Status |
|------|--------|-----------|-------|--------|
| G1 | Agreement Delta | >= +1.0% | +19.84% | **PASS** |
| G2 | Precision Delta | >= -2.0% | -13.35% | **FAIL** |
| G3 | Helps/Hurts Net | > 0 | +2 | **PASS** |
| G4 | Visual QA | Zero clipping | Manual | **PENDING** |

**Overall: FAIL (NO-GO)** - G2 failure blocks promotion.

---

## 4. Implementation Details

### Reranker Approach
- **Type:** Deterministic heuristic reranker (no model dependency)
- **Top-K:** 20 candidates per query
- **Scoring:** Token-overlap relevance between query text and font metadata (name, category, tags, description)
- **Formula:** Jaccard-like overlap + query coverage

### Calibration/Fusion
- **Formula:** `final_score = 0.5 * normalized_confidence + 0.5 * normalized_rerank_score`
- **Normalization:** Per-query min-max with epsilon safety
- **Decision Threshold:** 0.45 (fusion score)

### Variant ID
- `p5_01_rerank_calib`

---

## 5. Analysis

### Why G2 Failed

The token-overlap reranker is fundamentally not discriminative enough for font relevance:

1. **Sparse Metadata:** Font metadata (name, category, tags, description) is too sparse to capture nuanced relevance signals
2. **Query Vocabulary Mismatch:** User queries use descriptive terms ("geometric", "luxury", "playful") that don't directly match font metadata
3. **False Positive Introduction:** The fusion approach introduces false positives by lowering the effective decision barrier

### Alternative Approaches Tested

| Approach | G1 | G2 | G3 | Outcome |
|----------|----|----|----|----|
| Fusion (threshold 0.45) | PASS | FAIL (-13.35%) | PASS | NO-GO |
| Fusion (threshold 0.55) | PASS | FAIL (-14.28%) | FAIL | NO-GO |
| Precision-preserving filter | PASS | FAIL (-10.28%) | PASS | NO-GO |
| Zero-relevance filter | PASS | FAIL (-15.82%) | PASS | NO-GO |
| Recovery-only | PASS | FAIL (-19.64%) | FAIL | NO-GO |
| Overconfidence correction | PASS | FAIL (-18.19%) | FAIL | NO-GO |

All approaches failed G2, indicating the token-overlap signal is fundamentally weak for this domain.

---

## 6. Helps/Hurts Analysis

**Helps (6 cases):** Queries where rerank recovered correct matches
**Hurts (4 cases):** Queries where rerank introduced errors
**Net: +2**

Top helps and hurts are documented in the comparison artifact.

---

## 7. Recommendations

1. **Do NOT promote** `p5_01_rerank_calib` to production
2. **Future work:** Consider learned rerankers (cross-encoder models) that can capture semantic relevance beyond token overlap
3. **Alternative path:** Focus on hard-negative curation and query expansion rather than post-hoc reranking

---

## 8. Artifacts

- Comparison: `research/ab-eval/out/p5_01_v3_vs_p5_01_comparison.json`
- Gates: `research/ab-eval/out/p5_01_v3_vs_p5_01_gates.json`
- Script: `research/ab-eval/py/run_p5_01_rerank_calib.py`

---

## 9. Reproducibility

- **Seed:** 42 (where applicable)
- **Data:** SSoT `full_set_review_export_1770612809775.json`
- **Baseline:** v3 champion results `g3_v3_gated_results.json`
