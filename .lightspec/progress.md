# Project Progress Tracking

## Core RAG Migration (B2)
- **Status:** In Progress
- **Next Milestone:** M4: Production Cutover
- **Decision Reference:** [DEC-20260206-production-b2-migration](./decisions/DEC-20260206-production-b2-migration.md)

### Phase 1: Foundation (Feb 6 – Feb 12)
- [x] Initialize SSoT Documentation (LightSpec)
- [x] Design/Setup Background Queue for JIT
- [x] Implement B2 Embedding Utility
- [x] Update Search API for B2 Queries
- [x] Local E2E Validation (Toy Set)
- [x] Batch Re-embedding (Full Corpus)

### Phase 2: Migration & Launch (Feb 13 – Feb 20)
- [ ] Production Database Backup
- [ ] Deployment to Production
- [ ] Human Visual-Intent Validation

---

## Offline A/B Evaluation
- **Status:** In Progress
- **Current Dataset:** Medium Human v1
- **Next Dataset:** Complex Human v2
- **Decision Reference:** [DEC-20260207-complex-eval-b2-promotion](./decisions/DEC-20260207-complex-eval-b2-promotion.md)

### Human Labeling (Medium v1)
- [x] Preparation scripts (queries + candidate pool)
- [x] Interactive HTML labeling UI (Binary 0/1)
- [x] Export conversion to canonical labels
- [x] Human labeling session (Reviewer: casey)
- [x] Generate `labels.medium.human.v1.json`
- [x] Validation + Adjudication Waiver (Single Reviewer)

### Quality-First Track
- **Reference:** [DEC-20260208-quality-first-experiment-plan](./decisions/DEC-20260208-quality-first-experiment-plan.md)
- [ ] Step A — Specimen v2
- [ ] Step B — Attribute Schema v2
- [ ] Step C — Uncertainty Discipline
- [ ] Step C.5 — Label SSoT Review Gate (Complex v1)
- [ ] Step D — Targeted Quality Validation
- [ ] Step E — Retrieval Rerun
