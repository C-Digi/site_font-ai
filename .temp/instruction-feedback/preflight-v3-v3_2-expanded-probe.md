# Preflight Validation: Expanded Prompt v3 vs v3_2 Probe

## Status: READY
## Confidence: 0.95
## Risk Level: low


### Ambiguities
- Target common_coverage: Assumption is set to 40-60 based on 'max-fonts 20-40'.
- Quota availability: 5 keys in 'key.md' are assumed sufficient for 40 fonts.


### Missing Inputs
- None.


### Conflicts
- None.


### Assumptions_if_continue
- 'gemini-3-pro-preview' remains the baseline model.
- 'specimens_v3' is the correct specimen directory for prompt v3/v3_2 testing.
- 'key.md' is populated with active keys as per the smoke report.


### Command Plan (Expanded Probe)
1. **Control Arm (v3):**
   `python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --spec-dir specimens_v3 --max-fonts 40 --keys-file key.md --output week1_expanded_v3_control_results.json --cache-output week1_expanded_v3_control_raw.json`
2. **Treatment Arm (v3_2):**
   `python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_2 --gate 0.9 --spec-dir specimens_v3 --max-fonts 40 --keys-file key.md --output week1_expanded_v3_2_treatment_results.json --cache-output week1_expanded_v3_2_treatment_raw.json`
3. **Comparison:**
   `python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/week1_expanded_v3_control_results.json --treatment research/ab-eval/out/week1_expanded_v3_2_treatment_results.json --output research/ab-eval/out/week1_expanded_v3_vs_v3_2_comparison.json`


### Stop Conditions
- 'common_coverage' < 30 after full execution (indicates sample mismatch).
- Any arm returns 0 results (indicates API failure or model block).
- 'net_help' remains exactly 0 (suggests prompt differences are too subtle for the specimen/sample, though unlikely at N=40).


### Assessment
An expanded probe to 40 fonts is highly likely to provide meaningful directional signal. The 'v3_2' prompt includes specific guardrails for 'Geometric', 'Monospace', and 'Luxury' which were likely not triggered in the 6-font smoke test. A 40-font sample (approx. 30% of total SSoT) is the optimal balance between cost and significance for a phase 1 probe.
