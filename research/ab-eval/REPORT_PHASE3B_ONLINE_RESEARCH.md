# Online Research Report: Phase 3B - High-ROI Paths for Font Decision Quality

## 1. Executive Summary
This research session (2024–2026 horizon) identifies critical interventions to improve the **Agreement** KPI (and its more robust successor **Youden’s J**) between AI font judgments and human SSoT. Key findings suggest a pivot from "single-sample" visual audits to "multi-scale, representative description" cycles, leveraging the long-context capabilities of Gemini-3 and Qwen-2.5-VL.

## 2. Key Research Findings (2024–2026)

### A. Typography-Aware Vision & Feature Extraction
- **FontCLIP (2024)** & **Font-Agent (CVPR 2025)**: Validates that generic CLIP models lack typography-specific nuance. Successful implementations now use **Edge-Aware Traces** or **Control Point Extraction** to capture fine geometric details (strokes, serifs) before LLM judgment.
- **AI-Driven Typography Framework (2025/2026)**: Suggests moving from pixel-based checking to "experiential rubrics" that capture the "voice" and "reflective qualities" of type, reducing the "Geometric Trap" (pedantic alignment vs. intent).

### B. Prompting & Visual Strategy
- **All-at-Once Description (2025)**: High-performing pipelines (e.g., Qwen-2.5-VL 72B) feed **10 representative images** per class to an LVLM to generate detailed visual descriptions *first*, then compile these into a single "Class Essence" description for the final classifier.
- **Multi-Scale Visual Prompting (MSVP) (2025)**: Explicitly attending to "patch-level" features (zoomed glyphs) alongside global context significantly improves fine-grained anomaly detection (crucial for font-pair distinction).

### C. Metrics & Calibration under Class Imbalance
- **Youden’s J Statistic (2025)**: ArXiv '25 research argues that Cohen's Kappa and raw Agreement are "prevalence-dependent." **Youden’s J (Sensitivity + Specificity - 1)** is now the recommended KPI for LLM judges in imbalanced domains (e.g., rare "Luxury" or "Historical" fonts).
- **GHOST Thresholding (2025)**: A post-processing method that automatically tunes the decision threshold (moving away from 0.5 or a fixed 0.9) to maximize balanced metrics like MCC or Youden's J.

### D. Human-in-the-Loop (HITL) & Active Learning
- **Disagreement-Aware Loops (2025)**: Rather than treating model disagreement as noise, modern Active Learning loops (e.g., **APE - Ambiguous Prompt Experiment**) treat high-variance cases (Flash vs. Pro vs. FontCLIP) as the primary candidates for human relabeling.
- **LLM-as-Annotator (2025)**: Using a strong model (G3 Pro) for "pre-annotation" followed by human "confirmation/adjustment" (Relabeling over Filtering) yields higher quality SSoT sets.

## 3. Intervention Matrix for `site_font-ai`

| Intervention | Rationale | Expected Impact | Effort | Validation Plan |
| :--- | :--- | :--- | :--- | :--- |
| **KPI Pivot: Youden's J** | Corrects for prevalence bias in rare font categories. | High (Agreement stability) | S | Re-run `py/run_agreement_experiment.py` with J-stat. |
| **GHOST Thresholding** | Replaces arbitrary 0.9 gating with data-driven optimal. | High (F1 / Balanced Acc) | M | Add threshold sweep script to `research/ab-eval/py/`. |
| **Multi-Scale Specimen V3.1** | Addresses "Technical Blindness" to 8pt/zoomed details. | Med (Visual Shape Acc) | M | Update `scripts/seed-fonts.ts` to generate zoomed crops. |
| **All-at-Once Description** | Uses 10-sample context to build a "Class Essence" before label. | High (Consistency) | L | Prompt V4 implementation using G3-Pro context window. |
| **Disagreement-Aware AL** | Focuses human review on "Split Decisions" (Flash vs Pro). | High (SSoT Quality) | M | Export CSV of Flash/Pro delta cases for human review. |
| **Intent-Based Rubric (V4)** | Reduces FP-01 (Geometric Trap) via "voice" assessment. | Med (Precision) | S | Prompt V4 rubric overhaul focusing on "experiential" traits. |

## 4. Prioritized Experiment Roadmap

### Top 3 "Run Next" Plan
1. **[METRIC] Pivot to Youden's J + GHOST Tuning**: Re-evaluate the baseline using J-stat and find the optimal threshold (on current G3 Flash scores) to maximize this balanced metric.
   - *Stopping Criteria*: If J-stat improves > 10% vs baseline 0.9 gating.
2. **[SPECIMEN] Implement Specimen V3.1 (Multi-Scale)**: Update the image generation pipeline to include a "Comparison Block" (il1I) and an "8pt Legibility Block."
   - *A/B Design*: V3 (Standard) vs V3.1 (Multi-Scale) on G3 Flash.
3. **[PROMPT] Prompt V4 (All-at-Once Description)**: Test a two-stage prompt where the model first describes 10 samples of the font's "range" before committing to a classification.
   - *A/B Design*: V3 (Single-audit) vs V4 (Description-first) on G3 Pro.

### Backlog (Top 10)
1.  **KPI Pivot**: Transition from Agreement to Youden’s J.
2.  **GHOST Tuning**: Dynamic thresholding for class-balanced F1.
3.  **Specimen V3.1**: Multi-scale zoom (il1I) and 8pt body text.
4.  **Prompt V4**: "All-at-Once" Description-First Audit.
5.  **Disagreement-Aware AL**: Human review of high-variance model splits.
6.  **Intent-Based Rubric**: Refined "Experiential" typography audit.
7.  **Edge-Aware Features**: Feed SVG/Control Point density as text metadata.
8.  **Stacked Ensemble**: Linear Regressor meta-model over (G3 + Qwen + FC).
9.  **Semantic Perturbation**: Augment validation set with glyph distortions.
10. **MCC Monitoring**: Add Matthews Correlation Coefficient to leaderboard.

## 5. Sources and Research
1. [FontCLIP: Semantic Typography VLM (2024)](https://anranqi.github.io/img/fontCLIP.pdf)
2. [Font-Agent: Enhancing Font Understanding (CVPR 2025)](https://openaccess.thecvf.com/content/CVPR2025/papers/Lai_Font-Agent_Enhancing_Font_Understanding_with_Large_Language_Models_CVPR_2025_paper.pdf)
3. [Balanced Accuracy & Youden's J for LLM Judges (ArXiv 2025)](https://arxiv.org/html/2512.08121v2)
4. [Zero-Shot Fine-Grained Classification via LVLM (2025)](https://arxiv.org/html/2510.03903v1)
5. [GHOST: Threshold Adjustment for Imbalance (2025)](https://pubs.acs.org/doi/10.1021/acs.jcim.1c00160)
6. [Can LLMs Capture Human Disagreements? (Ni et al., 2025)](https://aclanthology.org/2025.nlperspectives-1.7.pdf)
7. [AI-Driven Typography Framework (MDPI 2026)](https://www.mdpi.com/2078-2489/17/2/150)
8. [Multi-Scale Visual Prompting (Emergent Mind 2025)](https://www.emergentmind.com/topics/multi-scale-visual-prompting-msvp)
9. [LLM Ensemble Stacking Strategy (SemEval-2025)](https://aclanthology.org/2025.semeval-1.150.pdf)
10. [Active Reward Modeling (Shen et al., 2025)](https://intuitionlabs.ai/articles/active-learning-hitl-llms)

---
*Created: 2026-02-10 | Phase 3B Research Synthesis*
