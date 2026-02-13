# Project Progress Tracking

## Core RAG Migration (B2)
- **Status:** In Progress
- **Next Milestone:** M4: Production Cutover
- **Decision Reference:** [DEC-20260206-01-production-b2-migration](./decisions/DEC-20260206-01-production-b2-migration.md)

### Phase 1: Foundation (Feb 6 – Feb 12)
- [x] Initialize SSoT Documentation (LightSpec)
- [x] Design/Setup Background Queue for JIT
- [x] Implement B2 Embedding Utility
- [x] Update Search API for B2 Queries
- [x] Local E2E Validation (Toy Set)
- [x] Batch Re-embedding (Full Corpus)

### Phase 3: Quality Optimization (Feb 9 – Feb 15)
- [x] Deep Mismatch Analysis vs amended SSoT
- [x] Run Intervention Matrix (Prompt V3, Specimen V3, Policy Gating)
- [x] Quantify Agreement gains (+1.1% on G2)
- [x] Execute G3 Production-Like Trial (V3 Policy + 0.9 Gating)
  - [x] Precision boost (+13.9%), Agreement (+3.2%)
- [x] Week 1 Prompt A/B completed (G3 Pro, Prompt V3 control vs Prompt V4 treatment)
  - [x] Outcome: keep Prompt V3 as champion (V4 reduced Agreement/Precision under current gate policy)
- [x] Week 2 Specimen Validation completed (V3.1 validated, improved Recall)
- [x] Week 3 Dynamic Threshold Calibration completed (Agreement-focused tuning)
  - [x] Implemented global and group-aware calibration (Technical vs Subjective)
  - [x] Validated via 5-fold CV by query
  - [x] Outcome: 0.9 gate confirmed safe; T=0.0 optimal for Agreement but 0.9 preferred for Precision/Noise floor.
- [ ] Roll out Prompt V3 to JIT Seeding path

### Phase 4: Refinement & Orthogonal Probes (Feb 13 – Feb 19)
- [x] Week 4: P1 Diagnostic Neutrality Probe (`v5_1`)
  - [x] Implementation and directional run (`n=20`)
  - [x] Decision: NO-GO / ITERATE (Zero delta observed)
- [x] Part A: Full-Set Failure Localization (v3 Champion)
  - [x] Analyzed 243 rows; localized 52 mismatches (21.4% rate)
  - [x] Identified 5 ranked failure buckets (Geometric Trap, Monospace Hallucination, Calligraphy, Era/Vintage, Texture)
- [x] Part B: P2 OEM Augmentation Plan (Fontshare)
  - [x] Designed 10-family high-signal extension plan (ITF/Fontshare)
  - [x] Defined acceptance criteria and effort estimate
- [ ] Execute Fontshare Seeding & v5.1 Baseline (Next Step)
- [ ] Roll out Prompt V3 to JIT Seeding path

---

## Offline A/B Evaluation
- **Status:** In Progress
- **Current Dataset:** Medium Human v1
- **Next Dataset:** Complex Human v2
- **Decision Reference:** [DEC-20260207-01-complex-eval-b2-promotion](./decisions/DEC-20260207-01-complex-eval-b2-promotion.md)

### Human Labeling (Medium v1)
- [x] Preparation scripts (queries + candidate pool)
- [x] Interactive HTML labeling UI (Binary 0/1)
- [x] Export conversion to canonical labels
- [x] Human labeling session (Reviewer: casey)
- [x] Generate `labels.medium.human.v1.json`
- [x] Validation + Adjudication Waiver (Single Reviewer)
- **Reference:** [DEC-20260208-01-human-label-medium-v1-workflow](./decisions/DEC-20260208-01-human-label-medium-v1-workflow.md)

### Quality-First Track
- **Reference:** [DEC-20260208-03-quality-first-experiment-plan](./decisions/DEC-20260208-03-quality-first-experiment-plan.md)
- [x] Step A — Specimen v2
- [x] Step B — Attribute Schema v2
- [x] Step C — Uncertainty Discipline
- [x] Step C.5 — Label SSoT Review Gate (Complex v1)
- [x] Step C.7 — FontCLIP Benefit Quantification Experiment
  - [x] Design experiment design (arms/hypotheses)
  - [x] Implement typographic proxy pipeline
  - [x] Run Baseline vs FontCLIP-Proxy vs Assisted arms
  - [x] Quantify impact on Precision/Recall
- [x] Step C.8 — Agreement Optimization Session
  - [x] Build experiment matrix (Calibration, Fusion, Query-aware)
  - [x] Establish query-level validation protocol
  - [x] Execute session and generate agreement leaderboard
  - [x] Deliver policy recommendation
- [ ] Step D — Targeted Quality Validation
- [ ] Step E — Retrieval Rerun

### Governance Upgrades
- [x] Lock Canonical Evaluation Contract (`EVALUATION_CONTRACT.md`)
- [x] Implement Hard Acceptance Gates (G1-G4)
- [x] Standardize Reproducibility & Quota Handling
- [x] Link Governance to LightSpec
