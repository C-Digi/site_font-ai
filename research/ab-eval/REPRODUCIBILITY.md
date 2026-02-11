# REPRODUCIBILITY & QUOTA MANAGEMENT

## 1. Determinism Standards
- **Global Seed**: Default `42`.
- **Stochasticity**: Most retrieval logic is deterministic (cosine similarity). LLM-based components (description generation, gating logic) are stochastic.
- **Repeat Policy**:
  - `repeats=1`: Standard for deterministic retrieval runs.
  - `repeats=3`: Required for new prompt/model probes (Week 1 style).

## 2. Quota & Rate Limiting Strategy
- **Provider**: Gemini API (primary).
- **Strategy**:
  - Scripts must implement exponential backoff for `429` (Rate Limit) errors.
  - For long runs (Full Corpus 200+), use the `--resume` flag to allow recovery from interruptions or quota exhaustion.
  - **Key Rotation**: Manual rotation via `.env.local` if needed, but primary focus is on non-blocking background processing to stay within steady-state quotas.

## 3. Canonical Command Templates

### Week 1: Prompt & Model Probes
```powershell
# Run with repeats to check stability
. .venv-ab-eval\Scripts\python research/ab-eval/py/run_all.py --dataset complex --variant A --seed 42 --repeats 3
```

### Week 2: Specimen & Attribute Changes
```powershell
# Standard run on 200-font set
. .venv-ab-eval\Scripts\python research/ab-eval/py/run_all.py --dataset 200 --variant all --seed 42
```

### Week 3: Calibration & Fusion
```powershell
# Calibration run on medium human-labeled set
. .venv-ab-eval\Scripts\python research/ab-eval/py/run_all.py --dataset medium --variant all --seed 42
```

## 4. Aggregation Rules
When `repeats > 1` are used:
- **Metrics**: Average results across all valid repeats.
- **Rankings**: Use the ranking from the first successful run (Seed 42) or implement Borda count if stability is low.
