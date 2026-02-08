# DEC-20260207-01-complex-eval-b2-promotion

- **Date:** 2026-02-07
- **Status:** Approved
- **Type:** Evaluation Decision
- **Run ID:** `complex_all_v1`

## Context
Evaluation of `Qwen3-VL` embeddings against the text-only baseline (Variant A) using the complex query set (`queries.complex.v1`).

## Decision
**GO_REPLACE**: Promote B2 (Vision + Metadata) to production default. Keep Hybrid D (RRF) as a research toggle for specialized searches.

## Rationale
Variant B2 significantly outperforms the text baseline (A) across all complex query classes, particularly in visual shape and historical context.
- **Metrics (Recall@10)**: { A: 0.1617, B2: 0.3962 }
- **Metrics (MRR@10)**:    { A: 0.2531, B2: 0.5231 }

### Qualitative Wins
Massive improvement in "visual_shape" (e.g. "geometric sans") where text often hallucinated handwriting fonts.

### Qualitative Losses
Some "semantic_mood" queries still benefit from text semantics, but B2 remains competitive.

## Next Steps
- Finalize B2 as the production default retrieval path.
- Keep Hybrid D (RRF) as a research toggle for "functional_pair" specialized searches.
