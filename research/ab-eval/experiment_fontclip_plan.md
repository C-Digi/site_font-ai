# FontCLIP Benefit Quantification Experiment Plan

## 1. Objective
Quantify the performance lift of integrating FontCLIP-derived typographic signals into the existing font-judgment pipeline.

## 2. Hypotheses
- **H1**: FontCLIP-derived signals provide superior discrimination for "micro-feature" queries (e.g., "slab serif", "high contrast", "open counters") compared to general-purpose text/VL embeddings.
- **H2**: Fusing FontCLIP signals with LLM judgments (Gemini 3) will reduce False Positives in visual-shape retrieval.

## 3. Experimental Arms
1. **Baseline Arm (Current Best)**: Gemini 3 Flash Preview judgments (from `full_set_no_bias_gemini3flashpreview_updated_ssot.json`).
2. **FontCLIP-Proxy Arm (Specialized Signal)**: Similarity-derived decisioning using specialized typographic descriptions (proxy for FontCLIP's latent space). 
   - *Implementation*: Use Qwen-235B generated typographic descriptions as the "latent" representation and compute similarity/relevance.
3. **FontCLIP-Assisted Arm (Fusion)**: Hybrid decisioning.
   - *Implementation*: Decision = `LLM_Vote` boosted/gated by `FontCLIP_Score`.

## 4. Evaluation Dataset
- **Ground Truth**: Human SSoT (`research/ab-eval/out/full_set_review_export_1770612809775.json`).
- **Population**: Same 247 query-font pairs as evaluated in the comprehensive report.

## 5. Success Metrics
- Agreement with Human SSoT
- Precision, Recall, F1
- Delta vs Baseline (Absolute % change)
- Failure Analysis (Per-query impact)
