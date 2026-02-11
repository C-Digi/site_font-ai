# Instruction Feedback - Governance Gate Pipeline Drift Investigation

## Instruction Ambiguities
- "governance gate pipeline drift": The exact nature of the drift isn't specified, but the task implies it relates to inconsistencies between `EVALUATION_CONTRACT.md` and the implementation scripts/artifacts.
- "reproduce current behavior": Determined to be `python research/ab-eval/py/validate_gates.py research/ab-eval/out/governance_gate_ready_v3.json --out research/ab-eval/out/governance_gate_results_v3.json`.

## Missing Inputs
- None.

## Conflicts
- `EVALUATION_CONTRACT.md` Table says G2 is "Precision Delta >= -2.0%".
- `validate_gates.py` uses `PRECISION_DELTA_MIN = -0.02`. This is numerically equivalent (-2% = -0.02), but the table says `Precision Delta >= -2.0%` (which usually means -0.02) while the script logic checks `delta_p >= -0.02`. However, the contract header for the table says `Precision Delta` but the value is `>= -2.0%`.
- Actually, -2.0% is -0.02.
- Wait, the contract says "G2 | Precision Delta | >= -2.0%".
- If the delta is -1.75%, that is >= -2.0%. So PASS is correct.

## Resolution Decisions
- Phase 1: Reproduced behavior. Observed FAIL on G1 and G3.
- Phase 2: Comparison reveals:
    - G1: 0.0000 < 0.01 (FAIL) - Correct according to contract.
    - G2: -0.0175 >= -0.02 (PASS) - Correct according to contract (though naming in script says "Delta" but value is absolute delta).
    - G3: 0 > 0 (FAIL) - Correct according to contract.
    - G4: PASS - Correct according to manual evidence.
- The "drift" might be in the terminology or derivation logic.
- Hypothesis 1: `derive_governance_artifact.py` doesn't include the treatment name in a way `validate_gates.py` prefers, but it works because of fallbacks.
- Hypothesis 2: G2 naming in `EVALUATION_CONTRACT.md` (Table) says "Precision Delta" but value is a percentage. Script uses decimal. This is fine.
- Hypothesis 3: The `governance_gate_results_v3.json` was already present and matched my reproduction. So where is the drift?
- Maybe the provenance has fabricated values? Let's check `comp['delta_treatment_minus_control']['agreement']` in `week2_specimen_v3_1_comparison.json`. It is `0.0`. `derive_governance_artifact.py` maps it.
- Wait, I see one issue: `G2` in `EVALUATION_CONTRACT.md` says `Precision Delta >= -2.0%`. In `validate_gates.py`, it prints `G2 (Precision Delta)`.
