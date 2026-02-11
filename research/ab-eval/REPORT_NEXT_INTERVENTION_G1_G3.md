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
