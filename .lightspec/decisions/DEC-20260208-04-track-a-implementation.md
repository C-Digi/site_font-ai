# DEC-20260208-04-track-a-implementation

- **Date:** 2026-02-08
- **Status:** Active
- **Type:** Implementation Record
- **Supersedes:** Partial implementation of [DEC-20260208-03-quality-first-experiment-plan](./DEC-20260208-03-quality-first-experiment-plan.md)

## Context
Track A (Quality-First Research) required upgrading the specimen renderer and the attribute schema to improve retrieval quality.

## Decision
Implemented Step A (Specimen v2), Step B (Attribute Schema v2), and Step C (Uncertainty Discipline).

### Implementation Details
1. **Specimen v2**: 1024x1024 deterministic layout with full character coverage and micro-tell strips (legibility pairs and contrast strips).
2. **Attribute Schema v2**:
   - Fixed-vocabulary for moods and use-cases.
   - Scored blocks (0.0 to 1.0) for each category.
   - Explicit `uncertainty_discipline` field for low-evidence reporting.
3. **Model Routing**: Vision-based description generation now routes through `openai/gpt-5.2` via OpenRouter with `include_reasoning: true` enabled.

## Justification
Standardization of the descriptor ontology and higher-fidelity input specimens are expected to reduce noise in the RAG pipeline and improve "vibe" match accuracy.

## Next Steps
- Execute Step C.5 (Label SSoT Review Gate) to adjudicate complex labels.
- Perform Step D (Targeted Quality Validation) using the new V2 descriptors.
- Rerun retrieval benchmarks (Step E).
