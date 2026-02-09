# DEC-20260209-01-ai-vs-human-alignment-spotcheck

**Status**: PROPOSED
**Date**: 2026-02-09
**Context**: Validation of AI judgment accuracy using Specimen v2 and GPT-5.2 against human labels.

## Decision
Promote `openai/gpt-5.2` (with high-reasoning `include_reasoning: true`) as the canonical judgment engine for visual relevance, even when it disagrees with human labels, provided its internal reasoning identifies specific structural features (e.g., presence of serifs) that contradict the query.

## Reasoning
- **Strictness vs. Nuance**: In spot-checks, the AI demonstrated 100% precision (0 False Positives) and correctly identified structural mismatches (e.g., identifying "Ovo" as a serif when the query asked for a geometric sans) that human reviewers may have overlooked or graded loosely.
- **Micro-tell Validation**: The model successfully used the `O0` legibility pair in Specimen v2 to correctly identify `IBM Plex Mono` for a coding-specific query.
- **Consistency**: AI reasoning is documented and deterministic based on visual evidence, whereas human labels showed more variability in stylistic edge cases (e.g., Art Deco vs. Modern Geometric).

## Alignment Metrics
- **Agreement Rate**: 86.67% (on 15-pair spot check)
- **Precision**: 100% (Model never recommended a font the human rejected)
- **Recall**: 50% (Model was more conservative than the human on stylistic edge cases)

## Implications
- Human labels remain the "Ground Truth" for general preference, but AI "Rejection" with reasoning should be treated as a signal for potential label refinement.
- Future evaluations should distinguish between "Structural/Technical" relevance (where AI is superior) and "Stylistic/Vibe" relevance (where human preference dominates).
