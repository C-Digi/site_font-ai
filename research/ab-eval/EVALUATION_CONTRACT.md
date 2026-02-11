# EVALUATION_CONTRACT — Governance & Gating for Offline A/B Eval

## 1. Pinned Paths & References
- **Canonical SSoT**: [`.lightspec/font-search-rag.md`](.lightspec/font-search-rag.md)
- **Primary Baseline Artifact**: [`research/ab-eval/out/report_medium_human_v1.json`](research/ab-eval/out/report_medium_human_v1.json)
- **Secondary Baseline Artifact**: [`research/ab-eval/out/report_all.json`](research/ab-eval/out/report_all.json) (Complex v1)
- **Canonical Gating Policy Source**: This document (`research/ab-eval/EVALUATION_CONTRACT.md`)

## 2. Metric Priority & Tie-Breaking
1. **Agreement (Global)**: Primary optimization target for alignment with human judgment.
2. **Recall@10**: Primary retrieval volume metric.
3. **Precision@10**: Primary noise-floor metric.
4. **MRR@10**: Tie-breaker for ranking quality.

**Tie-break order**: Agreement -> Recall@10 -> Precision@10 -> MRR@10.

## 3. Label Handling Policy (Non-Binary "2")
- **Policy**: Explicit Remap
- **Rule**: Labels marked as `2` (Uncertain/Partial) must be remapped to `0` (Negative) for primary metrics to maintain a strict quality bar.
- **Rationale**: We prefer high-precision retrieval. Including "maybe" fonts as positives inflates Recall at the expense of user trust.

## 4. Acceptance Gates (Promotion Criteria)
Before a model or retrieval strategy is promoted to production:

| Gate | Metric | Threshold |
| :--- | :--- | :--- |
| **G1** | Agreement Delta | >= +1.0% |
| **G2** | Precision Delta | >= -2.0% |
| **G3** | Helps/Hurts Net | > 0 |
| **G4** | Visual QA | Zero clipping/overlap (Manual) |

## 5. Reporting Protocol Ordering
Reports must follow this section order:
1. Executive Summary (Go/No-Go Decision)
2. Global Metrics Table (A vs B vs C vs D)
3. Gate Status (Pass/Fail for G1-G4)
4. Per-Query-Class Breakdown
5. Helps/Hurts Analysis (Top 5 wins, Top 5 losses)
6. Qualitative Notes & Failure Modes

## 6. Artifact Naming & Schema
All runs must produce artifacts named with the following prefixes based on the phase:
- `week1_`: Prompt engineering and LLM-only probes.
- `week2_`: Specimen and visual attribute changes.
- `week3_`: Calibration, thresholds, and fusion tuning.

**Required Keys in `report.json`**:
- `metadata`: `run_id`, `timestamp`, `commit_hash`, `variants`
- `global_metrics`: Map of metric names to values per variant.
- `gate_results`: Pass/Fail/Value for G1-G3.
- `helps_hurts`: List of queries where the treatment differs from baseline.

## 7. Scope of Model Promotion
- **Eval-only**: Changes to evaluation scripts or labelsets do not trigger production deployment.
- **Runtime-only**: Changes to search logic/LLM prompts must pass all gates.
- **Both**: Large changes (e.g., new embedding model) require full rerun of all canonical datasets.
