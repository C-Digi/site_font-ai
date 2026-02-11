# Preflight Feedback: Post-Expanded Next Intervention Recommendation

## Status: READY
The evidence quality from the expanded probe (v3 vs v3_2) is sufficient to recommend a next single-variable intervention.

## Artifact Validation
- Coverage: common_coverage=68 (PASS, >20 threshold).
- Control Results: research/ab-eval/out/week1_expanded_v3_control_results.json (Verified).
- Treatment Results: research/ab-eval/out/week1_expanded_v3_2_treatment_results.json (Verified).
- Comparison: research/ab-eval/out/week1_expanded_v3_vs_v3_2_comparison.json (Verified).
- Report: research/ab-eval/REPORT_WEEK1_PROMPT_V3_V3_2_SMOKE.md (Verified).

## Ambiguities & Observations
1. Precision/Recall Trade-off: v3_2 achieved a significant Recall boost (+11%) but suffered a Precision dip (-3%), resulting in a net-help of 0.
2. Help Analysis: v3_2 successfully recovered Art Deco (Federant) which v3 rejected for being not pure enough (calligraphic traits). This suggests the Geometric Inclusivity block in v3_2 is effective.
3. Hurt Analysis: v3_2 incorrectly matched a serif (Artifika) to playful candy shop due to whimsical vibe interpretation. This suggests the Rigorous evaluation instruction might need better anchoring for vibe vs technical alignment.
4. Instruction Conflict: The v3_2 prompt says Partial matches or almost matches should be scored as NO MATCH (0), yet it still matched Artifika to candy shop.

## Missing Inputs
- None. Artifacts provide sufficient textual reasoning (thought/evidence) to diagnose the delta.

## Conflicts
- None.

## Resolution Assumptions
- The next intervention should aim to preserve the Recall gains (likely from Geometric Inclusivity) while tightening the vibe interpretation to fix the Precision dip.
- No further paid runs are required for the recommendation itself, though a validation run will be needed eventually.

## Proposed Strategy
- Patch v3_2 to include a Vibe vs. Technical Anchor block that prevents vibe from overriding structural category failures (e.g., matching a formal serif to a playful display query).
