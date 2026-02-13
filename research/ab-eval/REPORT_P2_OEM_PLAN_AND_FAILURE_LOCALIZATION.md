# Report: Part A Full-Set Failure Localization & Part B P2 OEM Plan

## Executive Summary
This report localizes the failure modes for the champion model `v3` on the adjudicated full-set SSoT (n=243) and proposes a minimal, high-signal P2 OEM augmentation plan focusing on Fontshare (ITF). 

Current mismatch rate: **21.4%** (52/243).

---

## Part A: Failure Localization (Full-Set v3)

### Ranked Failure Buckets

1.  **The "Geometric" Trap (Excessive Lenience)**
    - **Count**: 14 (26.9% of mismatches)
    - **Description**: The model frequently attributes "perfect circles" and "low stroke variation" to fonts that are close but possess minor flares, tapers, or non-circular 'o' glyphs that the SSoT strictly rejects.
    - **Exemplars**:
        - `Farro` (cq_002): Model claims perfect circles; SSoT rejects.
        - `JetBrains Mono` (cq_002): Model sees near-perfect circles in a monospaced context; SSoT rejects.
        - `LXGW WenKai Mono TC` (cq_002): Model identifies rounded forms as geometric circles; SSoT rejects.
    - **v5.1 Addressability**: **Yes**. Stricter rubric requirements for "monolinear" and "perfectly circular" in `v5_1` should reduce these False Positives.

2.  **Monospace Hallucination / Detection Failure**
    - **Count**: 12 (23.1% of mismatches)
    - **Description**: Dual-sided failure where the model either hallucinates monospace properties in clean proportional sans/slabs or fails to recognize genuine monospaced fonts (like `Source Code Pro`) due to perceived width variation in the specimen.
    - **Exemplars**:
        - `Sixtyfour` (cq_015): Model identifies as cold/sterile monospace; SSoT rejects.
        - `Source Code Pro` (cq_015): Model *rejects* as monospace, claiming varying widths.
        - `Roboto Mono` (cq_040): Model *rejects* as monospace.
    - **v5.1 Addressability**: **Yes**. The inclusion of "micro-tells" (alignment guides) and a specific monospaced checklist in `v5_1` is designed for this.

3.  **Calligraphy vs. Casual Script Confusion**
    - **Count**: 10 (19.2% of mismatches)
    - **Description**: Model attributes "traditional calligraphic" status to casual handwriting or brush scripts based solely on stroke contrast, missing the formal/historical requirement of "traditional".
    - **Exemplars**:
        - `Ga Maamli` (cq_010): Model identifies as traditional; SSoT rejects as too modern/casual.
        - `Ms Madi` (cq_010): Model identifies as traditional; SSoT rejects.
    - **v5.1 Addressability**: **Uncertain**. Requires stronger semantic differentiation between "calligraphy" and "script" in the system prompt.

4.  **Vintage/Era Hallucination**
    - **Count**: 8 (15.4% of mismatches)
    - **Description**: Model misattributes specific eras (e.g., "1920s") to modern fonts with retro influences, often relying on "rounded serifs" or "high contrast" without checking era-specific markers.
    - **Exemplars**:
        - `Calistoga` (cq_019): Model claims 1920s; SSoT rejects.
        - `Bentham` (cq_021): Model claims 19th-century Victorian; SSoT rejects.
    - **v5.1 Addressability**: **No**. This remains a world-knowledge ceiling for the model without external metadata.

5.  **Texture/Inline Neglect**
    - **Count**: 8 (15.4% of mismatches)
    - **Description**: Model ignores structural modifiers (Inline, Sketch, Shade) when they conflict with a categorical judgment (e.g., rejecting an "Inline" font for a "clean" query).
    - **Exemplars**:
        - `Bungee Inline` (cq_025): Model rejects for Art Deco; SSoT says it's a match.

---

## Part B: P2 OEM Augmentation Plan (Fontshare)

### Objective
Expand the evaluation baseline to high-quality non-Google typefaces from **Fontshare (ITF)** to test generalization and model sensitivity to professional type design.

### Minimal Candidate Shortlist (n=10)

| Family | Category | Target Query | Reason for Inclusion |
| :--- | :--- | :--- | :--- |
| **Satoshi** | Sans | cq_002 | Premier geometric sans; ultimate test for "perfect circle" strictness. |
| **General Sans** | Sans | cq_018 | High-quality Neo-Grotesque; test for "modern minimal" intent. |
| **Sentient** | Serif | cq_016 | Elegant, high-contrast serif; test for "luxury branding". |
| **Zodiak** | Serif | cq_001 | Extreme contrast serif; test for "ultra-thin hairline". |
| **Expose** | Display | cq_003 | Condensed, aggressive design; test for "industrial" feel. |
| **Cabinet Grotesk**| Display | cq_011 | Variable width display; test for "quirky/playful" intent. |
| **Vela Mono** | Mono | cq_015 | Clean, functional monospace; test for "cold/sterile" terminal feel. |
| **Telma** | Rounded | cq_009 | Soft rounded sans; test for "friendly children brand". |
| **Chillax** | Display | cq_011 | Relaxed, quirky sans; test for "candy shop" vibe. |
| **Papiard** | Serif | cq_012 | Stern, sharp serif; test for "law firm" authority. |

### Effort & Burden
- **Annotation**: 100 predictions (10 families * 10 intents).
- **Load**: ~1.5 hours for expert adjudication.
- **Reviewer**: Casey (SSoT Author).

### Acceptance Criteria
- **Present**: Agreement >= 0.70; model successfully distinguishes ITF designs with same/higher precision than Google Fonts.
- **Absent**: Agreement < 0.60; model fails to generalize or shows bias toward Google Fonts training data.

---

## Recommendation Priority
1.  **Execute Fontshare Seeding**: Seed the 10 target families to the `fonts` table.
2.  **Run v5.1 Baseline**: Evaluate `v5_1` prompt on the new Fontshare subset to confirm precision gains.
3.  **Merge SSoT**: Adjudicate results into a new `Fontshare_v1` golden set.
