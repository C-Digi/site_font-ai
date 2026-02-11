# Preflight Feedback: v3 vs v3_3 Expanded Probe

## Ambiguities
- **Prompt Inheritance**: Confirmed that v3_3 is intended to be an incremental update over v3_2 (inheriting Diagnostic Neutrality, Geometric Inclusivity, and Luxury Anchor) based on the requirement to recover precision lost in the v3_2 run.

## Missing Inputs
- **None**: All required artifacts (v3/v3_2 results, SSoT, keys, specimen images) are present in the workspace.

## Conflicts
- **None**: No existing v3_3 implementations or conflicting prompt definitions found.

## Resolution Assumptions
- **Implementation Parity**: Both run_production_trial.py and intervention_runner.py should be updated with the v3_3 prompt logic.
- **Argparse Update**: run_production_trial.py requires an update to its --prompt choices list to accept v3_3.

## Proposed Prompt Patch
v3_3 inherits v3_2 and adds:
4. **Vibe Over-extension Guardrail (Display/Mood queries)**
   - For queries requesting playful, whimsical, quirky, or specific themed moods:
   - REQUIRE explicit structural novelty.
   - Do NOT classify based solely on minor flourishes if the underlying architecture remains formal/traditional.
