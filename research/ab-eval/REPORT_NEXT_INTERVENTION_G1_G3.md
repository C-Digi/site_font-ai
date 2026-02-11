# Intervention Plan: Improving G1 (Agreement) and G3 (Helps/Hurts Net)

## 1. Root-Cause Analysis (Slices)
- **Bucket 1: Diagnostic Feature Hallucination (High Risk)**
  - *Example*: `Overlock SC` (FP) for query `cq_040` (monospace).
  - *Root Cause*: The model misinterprets the presence of the "Critical Distinction" diagnostic section in Specimen V3.1 as proof of the font being a monospaced technical font.
- **Bucket 2: Category Over-exclusion (FN Regression)**
  - *Example*: `Alata` (FN) for query `cq_002` (geometric sans).
  - *Root Cause*: The model is hallucinating humanist traits (double-story g) or over-weighting minor stroke modulation, causing it to reject quintessentially geometric fonts that have slight humanist DNA.
- **Bucket 3: Subjective Threshold Creep (FP Regression)**
  - *Example*: `Esteban`, `Manuale` (FP) for query `cq_016` (luxury serif).
  - *Root Cause*: Specimen V3.1 rendering quality is high enough that standard book serifs are being over-interpreted as "sophisticated/luxury" by the model.

## 2. Recommended Intervention: Prompt V3.2 (Calibration)
**Single-Variable Change**: Update the System Prompt to include "Specimen Interpretation Guardrails".

### Key Changes:
1. **Diagnostic Neutrality**: Explicitly state that the "Critical Distinction" block is present on ALL specimens and should not be used as an indicator of category (monospace/coding) without verifying width consistency in the body text/alphabet.
2. **Geometric Inclusivity**: Instruct the model that geometric fonts can have minor humanist traits (like slight modulation) and that perfect circles in "o/p/b" should remain the primary identifier for "geometric".
3. **Luxury Anchor**: Define "luxury" more strictly, requiring specific high-end flourishes (swash Q, teardrop terminals) and high contrast to distinguish from standard editorial serifs.

## 3. Expected Metric Movement
- **G1 (Agreement)**: +1.5% (Eliminating 3/4 current hurts).
- **G3 (Net Help)**: > +2 (Move from 0 to +4 by converting Hurts back to TN/TP).
- **G2 (Precision)**: Recovery to > 0.825.

## 4. Risk and Rollback
- **Risk**: Conservative bias might cause FNs in actual luxury or technical fonts.
- **Rollback**: Revert to Prompt V3 if Agreement Delta falls below 0.

## 5. Command Plan
```powershell
# Lightweight parser validation only (no model jobs)
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --help
.\.venv-ab-eval\Scripts\python research/ab-eval/py/intervention_runner.py --help

# Example executable trial command using the new prompt variant (do not run in this task)
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_2 --output weekX_g3pro_promptv3_2_results.json
```
`n`n## 6. Expanded-Probe Analysis (v3 vs v3_2)`n`n### Findings`n- **Recall Gain**: Treatment `v3_2` achieved `+11.11%` recall gain (Recall `77.78%` vs Control `66.67%`), successfully recovering `Federant` for Art Deco (`cq_025`).`n- **Precision Regression**: Treatment `v3_2` suffered a `-3.03%` precision dip (Precision `63.64%` vs Control `66.67%`), caused by "vibe over-extension" on `Artifika` for playful/candy-shop queries (`cq_011`).`n- **Helps/Hurts Net**: Remained at `0` (1 help: `Federant`, 1 hurt: `Artifika`).`n- **Signal Consistency**: `common_coverage=68` provides a reliable directional read.`n`n### Selected Intervention: Prompt V3.3 (Vibe Guardrail)`n**Single-Variable Change**: Add a "Vibe Over-extension Guardrail" to the Specimen Interpretation Guardrails section of the prompt.`n`n**Proposed Addition:**`n> **4. Vibe Over-extension Guardrail (Display/Mood queries)**`n> - For queries requesting "playful", "whimsical", "quirky", or specific themed moods (e.g., candy shop, children's book):`n> - REQUIRE explicit **structural novelty** (e.g., irregular baseline, varying character widths/rhythm, novelty stroke endings, or asymmetrical construction).`n> - Do NOT classify a font as playful based solely on minor calligraphic flourishes (like a quirky 'g' ear or swash tail) if the underlying architecture remains a formal, high-contrast, or strictly traditional historical serif.`n`n### Expected Gate Impact`n- **G1 (Agreement Delta)**: `>= +1.0%` (Targeting recovery of the `Artifika` hurt).`n- **G2 (Precision Delta)**: `>= 0%` (Targeting elimination of the `Artifika` FP).`n- **G3 (Helps/Hurts Net)**: `> 0` (Projected `+1` Net Help).`n- **G4 (Visual QA)**: No expected impact.`n`n### Rollback Condition`n- Revert to Prompt V3 if Agreement Delta falls below 0 or if new precision regressions occur in non-display categories.`n`n### Next-Run Command Plan (Proposed)`n```powershell`n# Arm A: Control`n.\\.venv-ab-eval\\Scripts\\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3 --gate 0.9 --spec-dir specimens_v3 --max-fonts 40 --keys-file key.md --output week1_expanded_v3_control_results.json`n`n# Arm B: Treatment (v3_3)`n.\\.venv-ab-eval\\Scripts\\python research/ab-eval/py/run_production_trial.py --model gemini-3-pro-preview --prompt v3_3 --gate 0.9 --spec-dir specimens_v3 --max-fonts 40 --keys-file key.md --output week1_expanded_v3_3_treatment_results.json`n`n# Comparison`n.\\.venv-ab-eval\\Scripts\\python research/ab-eval/py/compare_week1_prompt_ab.py --control research/ab-eval/out/week1_expanded_v3_control_results.json --treatment research/ab-eval/out/week1_expanded_v3_3_treatment_results.json --output research/ab-eval/out/week1_expanded_v3_vs_v3_3_comparison.json`n```
