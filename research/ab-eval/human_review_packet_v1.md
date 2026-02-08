# Human-Review Packet: Font Description Quality (v1)

## 1. Overview

This packet facilitates the first human-in-the-loop validation of the AI-generated font descriptions. The goal is to ensure the descriptions are technically accurate and stylistically faithful to the glyph images before we commit them to the 200-font production vector key.

## 2. Review Files

- **Review Tool (HTML):** [`research/ab-eval/human_review_v1.html`](human_review_v1.html)
- **Descriptions:** `research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl`
- **Glyph Images:** `research/ab-eval/out/glyphs/*.png`

## 3. Sample Selection Method

Reviewers should check a **stratified sample of 20 fonts**:

- **5 Serif:** (e.g., Cormorant, Spectral SC)
- **5 Sans-Serif:** (e.g., Albert Sans, Golos Text)
- **5 Monospace:** (e.g., IBM Plex Mono, JetBrains Mono)
- **5 Display/Script:** (e.g., Bungee Inline, Ms Madi)

## 4. Reviewer Rubric

For each font, score the description fields on a scale of 0–2:

| Score        | Meaning                                                                                       |
| :----------- | :-------------------------------------------------------------------------------------------- |
| **2 (High)** | Description is perfectly accurate and captures subtle details (e.g., "cup-shaped terminals"). |
| **1 (Pass)** | Description is generally correct but uses generic terms (e.g., "rounded").                    |
| **0 (Fail)** | Description hallucinates features or contradicts the image (e.g., "serif" for a sans font).   |

**Checklist:**

- [ ] **Shape:** Does the geometry match (e.g., geometric vs. humanist)?
- [ ] **Contrast:** Is the weight variation accurately described?
- [ ] **Mood:** Do the tags make sense for the visual style?
- [ ] **Summary:** Is the integrated description cohesive?

## 5. Acceptance Gates

To promote the candidate model to full-key generation:

- **Accuracy:** At least 18/20 (90%) of sampled fonts must score "Pass" (1) or "High" (2) on technical attributes.
- **Precision:** At least 10/20 (50%) should score "High" (2).
- **Zero Hallucination:** No fonts should have "Fail" (0) scores for fundamental category (Serif vs. Sans).

## 6. Promotion Workflow

1. Open [`human_review_v1.html`](human_review_v1.html) in a browser.
2. Review the selected sample (or all 200).
3. Click **"Export Review Data"** to download the `font_description_reviews.json` file.
4. If gates are met, update `research/ab-eval/DECISIONS.md` with the "GO_PRODUCTION" status.
5. Run the answer-key embedding generation script (Next Phase).