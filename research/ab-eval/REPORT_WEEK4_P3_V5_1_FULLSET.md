# Week4 Phase3 V5.1 Full-Set Validation Report

**Run ID:** week4_p3_v5_1_fullset  
**Timestamp:** 2026-02-13T06:40:00Z  
**Control:** v3 (promo_v3_control_r1_results.json)  
**Treatment:** v5_1 (Diagnostic Neutrality intervention)

---

## 1. Executive Summary: NO-GO

**Promotion Readiness:** NOT READY

The v5_1 treatment (Diagnostic Neutrality single-variable intervention) failed G1 (Agreement Delta) with a delta of +0.40% against the required threshold of >= +1.0%. While G2 (Precision Delta) and G3 (Helps/Hurts Net) passed, the strict governance contract requires all gates to pass for promotion.

---

## 2. Global Metrics Table

| Metric | Control (v3) | Treatment (v5_1) | Delta |
|--------|-------------|------------------|-------|
| Agreement | 85.83% | 86.23% | +0.40% |
| Precision | 59.62% | 61.22% | +1.60% |
| Recall | 68.89% | 66.67% | -2.22% |
| F1 | 63.92% | 63.83% | -0.09% |

### Confusion Matrix

| | Control | Treatment |
|---|---------|-----------|
| TP | 31 | 30 |
| FP | 21 | 19 |
| FN | 14 | 15 |
| TN | 181 | 183 |
| **Total** | 247 | 247 |

---

## 3. Gate Status

| Gate | Status | Value | Threshold |
|------|--------|-------|-----------|
| G1 (Agreement Delta) | **FAIL** | +0.40% | >= +1.0% |
| G2 (Precision Delta) | PASS | +1.60% | >= -2.0% |
| G3 (Helps/Hurts Net) | PASS | +1 | > 0 |
| G4 (Visual QA) | PENDING | Manual | Zero clipping/overlap |

**Overall Gate Result:** FAIL (NO-GO)

---

## 4. Per-Query-Class Breakdown

N/A - Full-set validation uses aggregate metrics. Query-class breakdown not generated for this run.

---

## 5. Helps/Hurts Analysis

### Summary
- **Helps:** 8 cases (treatment correct where control was wrong)
- **Hurts:** 7 cases (treatment wrong where control was correct)
- **Net:** +1

### Top 5 Helps (Treatment Wins)

| Query ID | Font | Human | Control | Treatment |
|----------|------|-------|---------|-----------|
| cq_003 | Nova Mono | 1 | 0 | 1 |
| cq_039 | Goblin One | 1 | 0 | 1 |
| cq_011 | Bungee Shade | 0 | 1 | 0 |
| cq_011 | Playwrite BR Guides | 0 | 1 | 0 |
| cq_039 | Bungee Inline | 0 | 1 | 0 |

### Top 5 Hurts (Treatment Losses)

| Query ID | Font | Human | Control | Treatment |
|----------|------|-------|---------|-----------|
| cq_003 | Encode Sans Condensed | 1 | 1 | 0 |
| cq_009 | LXGW WenKai Mono TC | 1 | 1 | 0 |
| cq_012 | Esteban | 1 | 1 | 0 |
| cq_010 | Ga Maamli | 0 | 0 | 1 |
| cq_015 | Suravaram | 0 | 0 | 1 |

---

## 6. Qualitative Notes & Failure Modes

### Observed Patterns

1. **G1 Failure Analysis:** The v5_1 intervention (Diagnostic Neutrality) produced a modest agreement improvement (+0.40%) but fell short of the +1.0% threshold. This suggests the single-variable intervention is directionally correct but insufficient magnitude.

2. **Precision Improvement:** The +1.60% precision improvement indicates v5_1 reduces false positives, likely due to the stricter evidence requirement for category classification from the Diagnostic Neutrality guardrail.

3. **Recall Reduction:** The -2.22% recall indicates v5_1 is more conservative, missing some true positives that v3 caught. This is consistent with the guardrail requiring body/alphabet evidence rather than relying on the Critical Distinction block.

4. **Helps/Hurts Pattern:** The net +1 helps/hurts suggests marginal improvement, but the magnitude is too small to meet governance thresholds.

### Failure Mode: Insufficient Signal

The Diagnostic Neutrality intervention alone does not provide enough signal improvement to cross the G1 threshold. The v3 baseline already performs well (85.83% agreement), making incremental gains difficult with single-variable changes.

---

## 7. Artifacts

| Artifact | Path |
|----------|------|
| Treatment Results | `research/ab-eval/out/week4_v5_1_fullset_results.json` |
| Comparison | `research/ab-eval/out/week4_v3_vs_v5_1_fullset_comparison.json` |
| Gate Results | `research/ab-eval/out/week4_v3_vs_v5_1_fullset_gates.json` |
| This Report | `research/ab-eval/REPORT_WEEK4_P3_V5_1_FULLSET.md` |

---

## 8. Recommendation

**Verdict:** NO-GO for promotion

**Iteration Recommendation:**

The v5_1 intervention shows directional improvement but insufficient magnitude. Two concrete options for next iteration:

1. **Combine Interventions:** Test v5_1 + Geometric Inclusivity guardrail together (multi-variable) to amplify the agreement signal. This would require a new prompt version (e.g., v5_2) combining multiple calibrated guardrails from the v3_3/v3_4 experiments.

2. **Alternative Focus:** Investigate the 7 hurts cases to identify systematic patterns. If a specific query class (e.g., monospace, geometric) is disproportionately affected, consider a targeted guardrail for that class.

**Next Immediate Step:** Analyze the 7 hurts cases by query class to determine if a targeted intervention would be more effective than combining guardrails.

---

## 9. Governance Compliance

- [x] Label remap `2 -> 0` applied
- [x] Validator-compatible comparison schema used
- [x] Strict all-gates-pass semantics enforced
- [x] One-variable-at-a-time discipline maintained (v5_1 = Diagnostic Neutrality only)
- [x] G4 evidence/context alignment pending manual verification
