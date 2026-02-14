# P5-03A VL Embedding-Path Re-evaluation Report

- **Run ID:** `p5_03a_b2_vs_text`
- **Date (UTC):** 2026-02-14
- **Status:** **NO-GO**
- **Scope:** Offline-only bounded comparison of production B2 vs strengthened text-only baseline using VL-enriched descriptions.

---

## 1. Executive Summary

**Decision: NO-GO.**

Under canonical gates, production B2 did **not** demonstrate net value versus the strengthened text-only baseline for this gated pair-set comparison.

- G1 Agreement Delta: **-2.83%** (FAIL; threshold >= +1.0%)
- G2 Precision Delta: **-14.55%** (FAIL; threshold >= -2.0%)
- G3 Helps/Hurts Net: **-7** (FAIL; threshold > 0)
- G4 Visual QA: **PENDING (Manual)**

Although retrieval-only metrics still favor B2 on Recall/MRR, the governance promotion path is driven by agreement/precision/helps-hurts behavior on the adjudicated pair set.

---

## 2. Global Metrics Table (Baseline vs Treatment)

| Metric | Text-only (VL-enriched) Baseline | B2 Production Treatment | Delta (B2 - Baseline) |
|---|---:|---:|---:|
| Agreement | 0.8340 | 0.8057 | -0.0283 |
| Precision | 0.6000 | 0.4545 | -0.1455 |
| Recall | 0.2667 | 0.3333 | +0.0666 |
| F1 | 0.3692 | 0.3846 | +0.0154 |

Pair-set denominator:
- Total evaluated pairs: **247**
- Skipped pairs: **0**
- Label policy: **2 -> 0** (enforced)

---

## 3. Gate Status (Canonical, Unchanged)

| Gate | Metric | Threshold | Value | Status |
|---|---|---|---:|---|
| G1 | Agreement Delta | >= +1.0% | -2.83% | **FAIL** |
| G2 | Precision Delta | >= -2.0% | -14.55% | **FAIL** |
| G3 | Helps/Hurts Net | > 0 | -7 | **FAIL** |
| G4 | Visual QA | Zero clipping/overlap (Manual) | Manual | **PENDING** |

**Overall:** **NO-GO**.

---

## 4. Retrieval Snapshot (Context Only)

| Retrieval Metric | Text-only (VL-enriched) | B2 Production |
|---|---:|---:|
| Recall@10 | 0.202962 | 0.352307 |
| Recall@20 | 0.321237 | 0.506494 |
| MRR@10 | 0.352560 | 0.646508 |

Interpretation:
- B2 remains stronger as a pure retriever in this medium set.
- However, promotion gates rely on agreement/precision/helps-hurts against adjudicated pair labels.

---

## 5. Helps/Hurts Analysis

- Helps: **17**
- Hurts: **24**
- Net: **-7**

Representative helps:
- `cq_002` / `Kumbh Sans` (human=1): baseline miss, B2 hit
- `cq_015` / `Google Sans Code` (human=1): baseline miss, B2 hit
- `cq_025` / `Bungee Inline` (human=1): baseline miss, B2 hit

Representative hurts:
- `cq_010` / `Ms Madi` (human=0): baseline correct negative, B2 false positive
- `cq_016` / `Artifika` (human=0): baseline correct negative, B2 false positive
- `cq_019` / `Calistoga` (human=0): baseline correct negative, B2 false positive

---

## 6. Determinism and Protocol Compliance

- Seed: **42**
- Repeats: **1**
- Label remap policy: **2 -> 0**
- Gate thresholds: unchanged from `EVALUATION_CONTRACT.md`
- Existing validator flow invoked (`validate_gates.py`) and produced aligned NO-GO outcome.

---

## 7. Governance Integrity Statement

This run **did not change governance semantics**. Gate definitions, thresholds, and decision policy remain exactly as specified in `research/ab-eval/EVALUATION_CONTRACT.md`.

---

## 8. Artifacts

- Comparison JSON: `research/ab-eval/out/p5_03a_b2_vs_text_comparison.json`
- Gates JSON (run output): `research/ab-eval/out/p5_03a_b2_vs_text_gates.json`
- Gates JSON (validator output): `research/ab-eval/out/p5_03a_b2_vs_text_gates_via_validator.json`
- Runner script: `research/ab-eval/py/run_p5_03a_vl_reeval.py`
