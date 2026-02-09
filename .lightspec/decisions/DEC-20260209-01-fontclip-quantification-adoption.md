# DEC-20260209-01: FontCLIP Benefit Quantification & Adoption Strategy

- **Status:** Proposed
- **Date:** 2026-02-09
- **Deciders:** Assistant, Project Lead
- **Related:** [DEC-20260208-03-quality-first-experiment-plan](./DEC-20260208-03-quality-first-experiment-plan.md)

## Context and Problem Statement

As we refine the font retrieval pipeline (B2 migration), general-purpose vision models (Gemini Flash) have shown strength in "vibe" matching but struggle with typographic precision (e.g., specific x-heights, exact stroke contrast, or technical categories like "Slab Serif"). We need to quantify the benefit of adding specialized typographic signals (simulated as FontCLIP-Proxy) to the retrieval decision process.

## Decision Drivers

1.  **Precision vs. Recall:** Does adding a typographic gate reduce "hallucinated" matches (FPs)?
2.  **Subjectivity vs. Objectivity:** Where does typographic signal help (objective features) and where does it hurt (subjective aesthetics)?
3.  **Complexity/Cost:** Is the incremental overhead of a second model/pipeline justified?

## Considered Options

1.  **Baseline only (Status Quo):** General vision model (Gemini) makes all judgments.
2.  **FontCLIP-Assisted (AND):** Gating the visual judgment—fonts must pass BOTH visual and typographic filters.
3.  **FontCLIP-Assisted (OR):** Expansive retrieval—fonts pass if EITHER visual OR typographic filters match.

## Decision Outcome

**Chosen Option: FontCLIP-Assisted (AND) for Objective/Technical Queries; Baseline for Subjective Queries.**

### Evidence (Experiment Results - Feb 9, 2026)

| Arm | Precision | Recall | F1 | Agreement |
|-----|-----------|--------|----|-----------|
| Baseline | 0.6415 | 0.7556 | 0.6939 | 0.6397 |
| FontCLIP-Assisted (AND) | **0.7333** | 0.4889 | 0.5867 | 0.6356 |
| FontCLIP-Assisted (OR) | 0.4444 | **0.8000** | 0.5714 | 0.5425 |

### Pros and Cons of the Chosen Option

- **Pros:**
  - Significant boost in Precision (+0.09 absolute, ~14% relative) for objective queries.
  - Effectively eliminates False Positives for technical categories like "western slab serif" or "monospaced".
  - Typographic proxy signal (descriptions) provides a grounded "latent space" for visual reasoning.
- **Cons:**
  - "AND" strategy reduces Recall significantly (from 0.75 to 0.49), which may be too restrictive for exploratory search.
  - Increased latency and API cost (requires typographic enrichment).

## Implementation Plan

1.  **Enrichment:** Use the existing Qwen-235B typographic descriptions (already in repo) as the SSoT for font attributes.
2.  **Routing:** 
    - For queries containing "technical keywords" (serif, sans, slab, x-height, condensed, mono), apply the **AND** gate.
    - For subjective queries (luxury, fun, scary, professional), rely on the **Baseline** vision model.
3.  **Future:** Transition to official FontCLIP weights once environment constraints allow local GPU execution.
