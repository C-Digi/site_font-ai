# Work Breakdown Structure (WBS)

## Milestone 1: Rollout Setup (Day 1)
- **Task 1.1:** Initialize SSoT Docs (README, RUNBOOK, PROGRESS, DECISIONS, WBS).
  - *Status:* Done.
- **Task 1.2:** Update Roadmap in `tasks-user.md`.
  - *Status:* In-progress.

## Milestone 2: Core Implementation (Week 1)
- **Task 2.1:** Implement `generateB2Embedding` in `src/lib/ai/embeddings.ts`.
  - *Description:* Use `transformers` or API to generate multimodal embeddings.
  - *Acceptance:* Successful local run with a sample image + text.
- **Task 2.2:** Search API Integration.
  - *Description:* Update `src/app/api/search/route.ts` to use B2 embedding for the user query.
  - *Acceptance:* Search results returned using B2 space.
- **Task 2.3:** Background JIT Seeding Logic.
  - *Description:* Create a worker/queue to handle async re-embedding of fonts.
  - *Acceptance:* Fonts lacking B2 embeddings are queued and eventually processed.

## Milestone 3: Batch Migration (Week 2)
- **Task 3.1:** Bulk Re-embedding Script.
  - *Description:* Script to iterate over all `fonts` and generate B2 embeddings.
  - *Acceptance:* All fonts have populated `embedding_b2` (or updated main embedding column).
- **Task 3.2:** Production Cutover.
  - *Description:* Final validation and deployment of search changes.
  - *Acceptance:* Production users see results driven by B2.

## Milestone 4: Quality Assurance (Week 2)
- **Task 4.1:** Benchmark Verification.
  - *Description:* Run `score_retrieval.py` against the updated production DB.
  - *Acceptance:* Recall@10 >= 0.36.
- **Task 4.2:** Human Validation.
  - *Description:* Manual review of top 50 common queries.
  - *Acceptance:* Qualitative improvement confirmed by stakeholders.
