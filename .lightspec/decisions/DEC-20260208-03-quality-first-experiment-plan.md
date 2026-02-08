# DEC-20260208-03-quality-first-experiment-plan

- **Date:** 2026-02-08
- **Status:** Active
- **Type:** Research Plan

## Context
Current descriptor outputs show repetitive, generic attribute patterns. The specimen renderer and description schema are identified as potential bottlenecks for vibe/style retrieval.

## Decision
**NEEDS_MORE_DATA**: Prioritize targeted quality experiments over further production rollout or model shopping.

## Planned Experiment Sequence
1. **Step A — Specimen v2**: Move to 1024 deterministic layout with full character sets and micro-tell strips.
2. **Step B — Attribute Schema v2**: Add fixed-vocabulary scored blocks for moods and use-cases.
3. **Step C — Uncertainty Discipline**: Explicit handling for `unknown`/`uncertain` evidence.
4. **Step C.5 — Label SSoT Review Gate**: Adjudication pass for `labels.complex.v1.json` before freezing as canonical.
5. **Step D — Targeted Quality Validation**: A/B test specimen and schema variants.
6. **Step E — Retrieval Rerun**: Regenerate embeddings and rerun benchmarks.

## Justification
Improving input representation and ontology quality is expected to yield higher ROI than simply switching models or retrieval algorithms.

## Next Steps
- Implement Specimen v2 renderer.
- Define Attribute Schema v2 vocabulary.
- Execute adjudication pass for complex labels.
