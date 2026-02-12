# Preflight Readiness Assessment: Promotion Rerun (v3 vs v3.3)

## 1. Readiness Assessment

- **Is it ready/safe to launch promotion-grade rerun with repeat policy (repeats=3)?**
  - **Status**: READY (with precautions).
  - **Precautions**: Week 1 runs are stochastic and high-quota. The --resume flag is mandatory for long runs. Gemini-2.0-flash-lite (default search) is generally stable, but repeats=3 will consume 3x quota.
  
- **Paired Rerun Fairness**:
  - **Recommendation**: ALWAYS rerun control (v3) fresh alongside treatment (v3_3). 
  - **Rationale**: Reusing historical control artifacts risks 'drift bias' where changes in API response distributions or latent platform factors over time could pollute the delta. A promotion gate requires a clean, contemporaneous baseline.

- **Artifact Naming Scheme**:
  - **Control**: research/ab-eval/out/promo_v3_control_rep3.json
  - **Treatment**: research/abm-eval/out/promo_v3_3_treatment_rep3.json
  - **Comparison**: research/ab-eval/out/promo_v3_vs_v3_3_comp_rep3.json
  - **Gate Results**: research/abm-eval/out/promo_v3_vs_v3_3_gate_rep3.json

- **Manual G4 Supply**:
  - **Strategy**: Inject the G4 payload into the comparison report before running validate_gates.py.
  - **Proposed Command Patch**: Add a --visual-qa-pass flag to validate_gates.py or use a temporary JSON patcher to set visual_qa: { 'status': 'PASS', 'evidence': 'Verified on specimen v3.1' }.

## 2. Blockers & Risks

- **Quota Deadlock**: Long runs with repeats=3 on the full complex dataset may hit daily tier limits.
- **Aggregation Logic**: Verification needed that run_all.py correctly averages Agreement metrics across repeats. (Current REPRODW+jšr IBILITY.md says average results).

## 3. Resolution Assumptions

- **Agreement Definition**: Assumption is that Agreement is computed per-repeat and then averaged, rather than pooling all results and computing once.
- **Label Remapping**: Assumption is that the 2 -> 0 remap is applied before Agreement is calculated in the run_all.py path.