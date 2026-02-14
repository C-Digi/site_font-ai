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
- [x] Execute Fontshare Seeding & v5.1 Baseline
- [x] Adjudication support package + deterministic gating path
  - [x] Implemented `gen_oem_labeling_ui.py` (HTML artifact)
  - [x] Implemented `run_oem_gating.py` (Acceptance gate runner)
  - [x] Validated coverage block (20/100 pairs pending human review)
  - [x] Completed human adjudication and unblocked deterministic gating
  - [x] Week 4 P2 OEM gating result: targeted GO (`v3` vs `v5_1`)
- [x] Week 4 P3 full-set validation (`v3` vs `v5_1`)
  - [x] Result: NO-GO for global promotion (G1 +0.40%, below +1.0% threshold)
- [x] Week 4 P3 hurts root-cause analysis
  - [x] Decision: `NO_ACTIONABLE_SINGLE_VARIABLE` (no dominant >50% actionable motif)
- [x] Week 4 governance decision finalized
  - [x] Keep `v3` champion; OEM-slice GO treated as directional, not sufficient for global promotion
  - [x] Pause prompt-only `v5_x` iteration pending stronger motif concentration
- [ ] Roll out Prompt V3 to JIT Seeding path

### Phase 5: Non-Prompt Structural Improvements (Feb 14+)
- [x] P5-01: Deterministic Rerank + Calibration Trial
  - [x] Implemented token-overlap reranker with fusion calibration
  - [x] Result: NO-GO (G2 Precision Delta failure: -13.35%)
  - [x] Finding: Token-overlap reranker not discriminative enough for font relevance
  - [x] Artifacts: `REPORT_P5_01_RERANK_CALIB.md`, comparison/gates JSON
- [x] P5-02A: Learned Reranker Trial (cross-encoder)
  - [x] Implemented cross-encoder reranker (`ms-marco-MiniLM-L-6-v2`)
  - [x] Result: NO-GO (G2 Precision Delta: -14.28%, G3 Helps/Hurts Net: 0)
  - [x] Finding: MS-MARCO trained on web search, not font relevance; neutral helps/hurts
  - [x] Artifacts: `REPORT_P5_02A_LEARNED_RERANK.md`, comparison/gates JSON
- [x] P5-03A: VL Embedding-Path Re-evaluation (B2 vs VL-enriched text-only baseline)
  - [x] Implemented bounded offline evaluator: `run_p5_03a_vl_reeval.py`
  - [x] Deterministic controls: seed=42, repeats=1, label remap `2 -> 0`
  - [x] Result: NO-GO (G1 -2.83%, G2 -14.55%, G3 net -7)
  - [x] Artifacts: `REPORT_P5_03A_VL_REEVAL.md`, comparison/gates JSON
- [x] P5-04A: Bounded Hard-Negative Curation + Directional Intervention Trial
  - [x] Implemented deterministic offline runner: `run_p5_04a_hardneg_trial.py`
  - [x] Preflight input readability check + explicit assumptions logging
  - [x] Curated hard-negative directional slice (`n=12`) with deterministic selection and quota-fill policy
  - [x] Applied directional penalties (`vintage_era` / `over_strict_semantic`) with stable re-ranking
  - [x] Result: NO-GO (directional slice; neutral deltas, G1 fail, G3 fail, G2 pass)
  - [x] Artifacts: `REPORT_P5_04A_HARDNEG.md`, variant/comparison/gates JSON
- [x] P5-05A: Coverage Sufficiency Audit (Pre-Trial Hardening)
  - [x] Implemented deterministic pre-trial audit runner: `run_p5_05a_coverage_audit.py`
  - [x] Added readiness preflight for required inputs with explicit `RETURN_RETRY` blocker/remediation path
  - [x] Implemented required checks: motif coverage, sample floor, penalty applicability, rank-shift opportunity (ranks 8-12 boundary analysis)
  - [x] Added explicit `coverage_decision` (`SUFFICIENT|INSUFFICIENT`) and delegate guidance (`CONTINUE_SAFE|RETURN_RETRY`)
  - [x] Result: `coverage_decision=INSUFFICIENT` (motif imbalance: `over_strict_semantic` below minimum)
  - [x] Artifacts: `REPORT_P5_05A_COVERAGE_AUDIT.md`, `out/p5_05a_coverage_audit.json`
- [x] P5-05B-EXPANDED: Motif-Detection Expansion + Coverage Re-Audit
  - [x] Expanded deterministic `over_strict_semantic` motif detection heuristics in `run_p5_05a_coverage_audit.py`
  - [x] Re-ran coverage audit and regenerated report/artifacts
  - [x] Result: `coverage_decision=INSUFFICIENT` (strict motif coverage still below minimum)
  - [x] Artifacts: updated `REPORT_P5_05A_COVERAGE_AUDIT.md` and `out/p5_05a_coverage_audit.json`
- [x] P5-05C: Coverage Remediation (Bounded Offline Logic Sync + Re-Audit)
  - [x] Synchronized deterministic strict-cue motif assignment between curation and coverage-audit paths
  - [x] Re-ran curation and coverage audit artifacts deterministically
  - [x] Result: `coverage_decision=SUFFICIENT` (`over_strict_semantic=6`, `vintage_era=6`)
  - [x] Governance semantics unchanged (pre-trial gate only; G1/G2/G3/G4 unchanged)
- [x] P5-06A: Directional Intervention Trial (Coverage-Remediated Balanced Slice)
  - [x] Executed bounded offline trial using P5-05C balanced slice (12 pairs; 6 per motif)
  - [x] Deterministic controls: seed=42, repeats=1, penalties unchanged (vintage=-0.12, strict=-0.10)
  - [x] Result: NO-GO (neutral deltas; G1 fail, G3 fail, G2 pass)
  - [x] Finding: Penalty magnitudes insufficient to produce boundary flips on saturated baseline confidence
  - [x] Artifacts: `REPORT_P5_06A_DIRECTIONAL.md`, variant/comparison/gates JSON
  - [x] Governance semantics unchanged (directional evidence only; not global promotion proof)
- [ ] P5-03: Domain-Specific Reranker Training (pending)

### Next-Phase: Productization & Scale (Feb 20+)
- **Strategic Direction:** Non-prompt pivot (structural quality) and foundational product build-out.
- **Champion State:** `v3` remains production champion; `v5.x` iterations paused.
- [ ] **Retrieval Quality Hardening**
  - [x] P5-01: Deterministic reranking trial (NO-GO)
  - [x] P5-02A: Learned reranker / cross-encoder evaluation (NO-GO)
  - [x] P5-04A: Hard-negative directional curation trial (NO-GO, neutral signal)
  - [x] P5-05A: Coverage sufficiency pre-trial gate (INSUFFICIENT)
  - [x] P5-05B-EXPANDED: Motif-detection expansion + coverage re-audit (INSUFFICIENT)
  - [x] P5-05C: Coverage remediation executed; pre-trial coverage now `SUFFICIENT`
  - [x] P5-06A: Directional intervention trial on balanced slice (NO-GO, neutral deltas)
  - [ ] Scale eval dataset to Complex v2 (Human SSoT)
- [ ] **VL Embedding Re-evaluation**
  - [x] P5-03A: Benchmarking image+text (B2) vs text-only baseline (using VL-enriched descriptions) completed (NO-GO for default replacement)
  - [ ] Define follow-on embedding-path hypotheses before another benchmark cycle
  - [ ] **Promotion Gate:** Must pass canonical `EVALUATION_CONTRACT.md` gates before switching production default
- [ ] **User-Facing AI Improvements**
  - [ ] Multi-turn chat context refinement
  - [ ] Enhanced font comparison/explanation generation
- [ ] **UI/UX Build-up**
  - [ ] Advanced filtering & specimen interaction
  - [ ] Responsive design & accessibility audit
- [ ] **Foundational Tracks**
  - [ ] **Auth:** User accounts, saved fonts, search history
  - [ ] **Payments:** Subscription tiers / Monetization strategy
  - [ ] **Ops:** Observability, error tracking, and release readiness
  - [ ] **Reliability:** Queue worker hardening and DLQ management

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
- [x] P2 OEM Extension labeling (100 pairs) completed
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
