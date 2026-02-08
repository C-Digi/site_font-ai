# Human-Review Packet: Font Description Quality (v1)

## 1. Overview

This packet facilitates the first human-in-the-loop validation of the AI-generated font descriptions. The goal is to ensure the descriptions are technically accurate and stylistically faithful to the glyph images before we commit them to the 200-font production vector key.

## 2. Review Files

- **Review Tool (HTML):** [`research/ab-eval/human_review_v1.html`](human_review_v1.html)
- **Descriptions:** `research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl`
- **Glyph Images:** `research/ab-eval/out/glyphs/*.png`

## 3. Sample Selection Method

The review tool now automatically presents a **stratified sample of 50 fonts** (approx. 10 per category: Serif, Sans-Serif, Display, Handwriting, Monospace) to ensure variety while keeping the task manageable.

## 4. Reviewer Rubric

For each font, evaluate both the **235B (Winner Candidate)** and **32B (Challenger)** using the tabs. Score each model on a scale of 0–2:

| Score        | Meaning                                                                                       |
| :----------- | :-------------------------------------------------------------------------------------------- |
| **2 (High)** | Description is perfectly accurate and captures subtle details (e.g., "cup-shaped terminals"). |
| **1 (Pass)** | Description is generally correct but uses generic terms (e.g., "rounded").                    |
| **0 (Fail)** | Description hallucinates features or contradicts the image (e.g., "serif" for a sans font).   |

**Checklist:**

- [ ] **Tabs:** Toggle between models to see which one provides better typographic nuance.
- [ ] **Shape:** Does the geometry match (e.g., geometric vs. humanist)?
- [ ] **Contrast:** Is the weight variation accurately described?
- [ ] **Mood:** Do the tags make sense for the visual style?
- [ ] **Use Cases:** Are the suggested applications appropriate for the font?
- [ ] **Summary:** Is the integrated description cohesive?

## 5. Acceptance Gates

To promote the candidate model to full-key generation:

- **Model Preference:** 235B should demonstrate equal or better nuance than 32B in at least 80% of samples.
- **Accuracy:** At least 45/50 (90%) of sampled fonts must score "Pass" (1) or "High" (2) on technical attributes.
- **Precision:** At least 25/50 (50%) should score "High" (2).
- **Zero Hallucination:** No fonts should have "Fail" (0) scores for fundamental category (Serif vs. Sans).

## 6. Promotion Workflow

1. Open [`human_review_v1.html`](human_review_v1.html) in a browser.
2. Review the presented 50 fonts. Use the score buttons (0/1/2) and notes field for **each model**.
3. Click **"Export Results"** to download the `bakeoff_human_review_results.json` file.
4. If gates are met, update `research/ab-eval/DECISIONS.md` with the "GO_PRODUCTION" status.
5. Proceed to generate full-key embeddings using the winning descriptions.