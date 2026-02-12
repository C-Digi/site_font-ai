# Analysis Report: Metadata-Based Routing Feasibility

## Project Overview
- **Champion Reference:** `v3` Control (PROMO_V3_CONTROL_V3_1_R2)
- **Baseline:** `v3_4` Treatment (PROMO_V3_4_TREATMENT_V3_1_R2)
- **Corpus Source:** `research/ab-eval/data/corpus.200.json` (Google Fonts via Fontsource)

## Part A: False-Negative Audit (`v3_4` NO-GO)
Targeted audit of the `v3_4` regression, which attempted to enforce category architecture consistency.

### Ranked Regression Buckets
| Bucket Motif | Type | Impact (Net) | Description |
| :--- | :--- | :--- | :--- |
| **Category-Ambiguity Hallucination** | Hurt (FP) | -11 rows | Model misidentifies close-match categories (e.g., Sans as Monospace) due to increased prompt pressure. |
| **Architectural Over-Enforcement** | Help (TN) | +4 rows | Correctly rejected fonts that previously passed on "vibe" but failed technical category (e.g., Sans rejected for Typewriter). |
| **Visual Evidence Degradation** | Hurt (FN) | -1 row | Model ignores clear visual cues (e.g., Monospace tail) in favor of hallucinated category mismatch. |

### Quantified Impact
- **Precision Hit:** The majority of the regression (~2.5%) is driven by **11 new False Positives**.
- **Net Trade-off:** 12 total "Hurts" vs 10 total "Helps" (Net -2 rows in $n=247$ per repeat).
- **Finding:** The rigid guardrail approach in `v3_4` improved categorical rejection (TNs) but introduced significant noise in positive identification (FPs), failing the G2 gate (Precision Regression <= -2%).

## Part B: Metadata Separability Analysis
Analysis of the Champion (`v3`) performance segmented by typography category.

### Segment Performance Table
| Category | Sample Size | Precision | Recall | MRR (Est.) | Performance Tier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Monospace** | 62 | 77.8% | 87.5% | High | **Tier 1 (Reliable)** |
| **Sans-Serif** | 49 | 75.0% | 60.0% | Med | **Tier 1 (Reliable)** |
| **Serif** | 50 | 58.3% | 87.5% | Med | **Tier 2 (Sensitive)** |
| **Display** | 46 | 30.0% | 33.3% | Low | **Tier 3 (Chaotic)** |
| **Handwriting** | 40 | 0.0% | 0.0% | N/A | **Tier 4 (Critical Failure)** |

### Viability Judgment
- **Monospace/Sans/Serif:** Highly viable for metadata-based gating. These segments have clear architectural boundaries that the model understands.
- **Display/Handwriting:** Non-viable for categorical gating. These buckets are currently "noise-saturated". Routing for these should shift from *category* to *visual/mood* descriptors.

## Candidate Routing Policies

### 1. Monospace Strict Guardrail
- **Logic:** Apply the `v3_4` consistency guardrail ONLY to queries and fonts in the `monospace` category.
- **Upside:** Locks in high precision for technical users.
- **Downside:** None identified.
- **Confidence:** High.

### 2. Display Category-Bypass
- **Logic:** For the "display" category, suppress category checks and use a specialized "Visual Texture First" prompt.
- **Upside:** Reduce False Negatives (FN) for stylistic matches that dont fit clean categories.
- **Downside:** Risk of increased False Positives if stylistic noise is high.
- **Confidence:** Medium.

### 3. Handwriting Hybrid Recovery
- **Logic:** Force a multimodal retrieval branch for "handwriting" that bypasses text-based category filters entirely.
- **Upside:** Potential to solve the 0% recall problem in handwriting.
- **Downside:** Requires specialized training/prompting.
- **Confidence:** Low (Research-track).

## Recommended Next Experiment
**Experiment Design:** `v4_1` (Segmented Gating).
- **Variable:** Routing by metadata "category".
- **Method:** Use `v3_4` prompt for `monospace/serif` and `v3` prompt for `display/handwriting`.
- **Validation:** Repeat $n=3$ using standard promotion gates.

## GO/NO-GO
- **Metadata-Based Routing:** **GO (Research-Track)**.
- **Status:** Sufficient signal exists in Monospace/Sans buckets to justify segment-specific logic.