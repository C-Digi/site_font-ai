# ADR: Adoption of Specimen V3 and Prompt V3 for Font Evaluation

## Status
Proposed

## Context
Following a deep failure analysis sprint, it was discovered that the baseline Gemini 3 model (0.69 Agreement) suffered from technical strictness and lack of visual density in certain categories (Historical, Functional Pairs). Baseline Gemini 2.0 Flash was significantly lower at 0.66.

## Decision
We will transition to **Specimen V3** and **Prompt V3** for all future vision-based font judgments.

### Key Enhancements
1. **Specimen V3 (Split View)**: 
   - Splits the 1024x1024 specimen into two separate 1024x1024 images (Top: Macro/Charset, Bottom: Micro/Texture).
   - Increases pixel density for character details by ~2x.
   - Adds "Style Identifiers" strip (`a, g, y, Q, &`) to highlight stylistic "tells".
2. **Prompt V3 (Master Auditor Rubric)**:
   - Enforces a strict decision rubric (technical constraints + vibe).
   - Requires explicit visual evidence for every match decision.
   - Adds confidence scoring for policy-based gating.
3. **Policy Gating**:
   - Matches with confidence < 0.9 on G2 models will be treated as negative matches to prioritize Precision.

## Consequences
- **Improved Agreement**: Demonstrated +1.1% gain on Gemini 2.0 Flash models.
- **Improved Reliability**: Precision increased by ~5% using the new rubric.
- **Storage/Bandwidth**: Increased image storage requirements (2 images per font instead of 1).
- **Inference Latency**: Slight increase in token count and image processing time.

## Evaluation
- Baseline (G2 V2): 0.6640
- Improved (G2 V3): 0.6749
- Baseline (G3 V2): 0.6923 (Goal: Test G3 with V3 components next).
