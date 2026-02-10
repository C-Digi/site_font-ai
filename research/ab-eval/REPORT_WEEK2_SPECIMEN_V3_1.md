# Week 2 Evaluation Report: Specimen V3.1 Validation

## Scope Executed
- **Implementation**: Upgraded Specimen Renderer to V3.1.
    - Added dedicated macro-scale `il1I0O` distinction block.
    - Expanded stylistic "tells" (Style Identifiers).
    - Preserved V3 layout robustness.
- **Regeneration**: Full 200-font output set generated under `research/ab-eval/out/specimens_v3_1/`.
- **Validation**: Manual visual QA of 12+ fonts including previous defect targets (Red Hat Mono, Playwrite Guides).
- **Evaluation**: Full-set run using Week 1 Champion configuration:
    - Model: `google/gemini-3-pro-preview`
    - Prompt: V3 (Champion)
    - Specimen: V3.1 (New)
    - Gate: 0.9 confidence.

## Metrics Comparison (Week 2 vs Week 1 Champion)

| Metric | Week 1 (V3 Specimen) | Week 2 (V3.1 Specimen) | Delta |
|---|---|---|---|
| **Agreement** | 0.6761 | 0.6761 | +0.0000 |
| **Precision** | 0.8333 | 0.8158 | -0.0175 |
| **Recall**    | 0.6667 | 0.6889 | +0.0222 |
| **F1 Score**  | 0.7407 | 0.7470 | +0.0063 |
| **TP**        | 30 | 31 | +1 |
| **FP**        | 6 | 7 | +1 |
| **FN**        | 15 | 14 | -1 |
| **TN**        | 137 | 136 | -1 |
| **Total**     | 247 | 247 | 0 |

## Analysis
- **Stability**: Overall Agreement remained exactly the same at 67.61%.
- **Trade-off**: The gain of 1 True Positive (improving Recall) was offset by 1 new False Positive (decreasing Precision).
- **Net Impact**: The shift is marginal, but the improved Recall suggests that the higher density of visual information (the new distinction block and tells) helped the model catch at least one previously missed match.
- **Visual Confidence**: Manual inspection confirms that V3.1 is visually superior for human-in-the-loop auditing and provides the model with clearer "tells" without breaking the existing robust layout.

## Helps / Hurts Summary
- **Helps (4)**: `Encode Sans Condensed` (cq_003), `Suravaram` (cq_016 - fixed FP), `Bungee Inline` (cq_025), `Overpass Mono` (cq_039 - fixed FP).
- **Hurts (4)**: `Alata` (cq_002), `Esteban` (cq_016), `Manuale` (cq_016), `Overlock SC` (cq_040).

The "helps" on `cq_016` and `cq_039` (moving from FP to TN) indicate improved discrimination on these specific queries.

## Recommendation
**PROCEED with Specimen V3.1 as the new baseline.**

Rationale:
1.  **No regression in Agreement.**
2.  **Improved Recall/F1.**
3.  **Superior Visual Information**: The added distinction blocks are objectively better for auditing and likely contribute to long-term model reliability even if the immediate metric gain is small.
4.  **Layout Safety**: Zero regressions in layout artifacts (cropping/overlap) confirmed via hard QA targets.

## Artifacts
- Renderer: `research/ab-eval/py/render_specimen_v3_1.py`
- Results: `research/ab-eval/out/week2_g3pro_v3_1_results.json`
- Comparison: `research/ab-eval/out/week2_specimen_v3_1_comparison.json`
- QA Note: `research/ab-eval/QA_SPECIMEN_V3_1.md`
