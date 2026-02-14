# P5-04A Hard-Negative Curation + Directional Intervention Report

- **Run ID:** `p5_04a_v3_vs_hardneg`
- **Variant ID:** `p5_04a_hardneg_candidate`
- **Date (UTC):** 2026-02-14
- **Status:** **NO-GO (Directional Slice)**
- **Scope:** Offline-only bounded hard-negative curation + directional intervention trial under `research/ab-eval/`.

## 1. Executive Summary

P5-04A was executed as a deterministic, auditable, offline directional trial using a curated hard-negative slice and a single directional intervention variant. The run completed successfully and generated required artifacts.

Outcome on the curated slice (`n=12`) was **neutral**:

- Agreement Delta: `+0.00%`
- Precision Delta: `+0.00%`
- Helps/Hurts Net: `0`

Gate result is **NO-GO** (directional slice), with unchanged governance semantics.

## 2. Global Metrics Table

| Metric | v3 (Baseline) | p5_04a_hardneg_candidate | Delta |
|---|---:|---:|---:|
| Agreement | 0.0000 | 0.0000 | +0.0000 |
| Precision | 0.0000 | 0.0000 | +0.0000 |
| Recall | 0.0000 | 0.0000 | +0.0000 |
| F1 | 0.0000 | 0.0000 | +0.0000 |

## 3. Gate Status (Canonical, Unchanged)

| Gate | Metric | Threshold | Value | Status |
|---|---|---|---:|---|
| G1 | Agreement Delta | >= +1.0% | +0.00% | **FAIL** |
| G2 | Precision Delta | >= -2.0% | +0.00% | **PASS** |
| G3 | Helps/Hurts Net | > 0 | 0 | **FAIL** |
| G4 | Visual QA | Zero clipping/overlap (Manual) | Manual | **PENDING** |

**Overall:** **NO-GO**.

## 4. Per-Query-Class Breakdown

- `historical_context`: 12 pairs, helps=0, hurts=0

Observed motif counts in selected slice:

- `vintage_era`: 12
- `over_strict_semantic`: 0

## 5. Helps/Hurts Analysis

- Helps: **0**
- Hurts: **0**
- Net: **0**

No directional case flips occurred on the selected hard-negative slice.

## 6. Qualitative Notes & Failure Modes

- **Preflight:** All required inputs were readable and valid.
- **Determinism controls:** seed=42, repeats=1, stable sorting and tie-breaks.
- **Locked assumptions applied explicitly:**
  - confidence from `g3_v3_gated_results.json` used as ranking proxy,
  - metadata joined from `corpus.200.json` by font name,
  - standard English stopword list used for `over_strict_semantic` token-miss checks.
- **Quota behavior:** `over_strict_semantic` had zero qualifying candidates under the locked hard-negative definition; deterministic shortfall fill came from `vintage_era` to maintain total `n=12`.
- **Directional limitation:** This slice result is directional evidence only and does not imply global promotion readiness.

## Governance Integrity Statement

This run did **not** modify governance semantics. Gate thresholds, remap policy (`2 -> 0`), and decision interpretation remain unchanged from `research/ab-eval/EVALUATION_CONTRACT.md`.

## Artifacts

- Variant artifact: `research/ab-eval/out/p5_04a_hardneg_candidate.json`
- Comparison artifact: `research/ab-eval/out/p5_04a_v3_vs_hardneg_comparison.json`
- Gate validation artifact: `research/ab-eval/out/p5_04a_v3_vs_hardneg_gates.json`
- Runner script: `research/ab-eval/py/run_p5_04a_hardneg_trial.py`

