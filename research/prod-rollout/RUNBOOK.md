# Rollout Runbook: B2 Retrieval Migration

This runbook outlines the operational steps for transitioning the production environment from text-only embeddings to B2 (Multimodal) embeddings over a 2-week period.

## Week 1: Infrastructure & Pipeline Implementation

### 1. Database Preparation
- [x] Verify Supabase schema supports 4096-dimensional vectors (already implemented).
- [x] Create `seed_jobs` table and helper functions for JIT re-embedding queue.

### 2. Backend Integration
- [x] Implement `B2` embedding generation in `src/lib/ai/embeddings.ts`.
- [x] Update `src/app/api/search/route.ts` to use B2 for query embedding.
- [x] Implement the background queue mechanism for JIT seeding.
  - [x] Search request enqueues a `seed_jobs` entry if font missing.

### 3. Pipeline Validation
- [x] Run end-to-end local smoke test:
  - [x] `npx tsx scripts/smoke-test-b2.ts`
- [ ] Validate glyph rendering consistency in the production pipeline.

## Week 2: Data Migration & Cutover

### 4. Batch Re-embedding
- [x] Implement worker runtime: `scripts/worker-seed-jobs.ts`.
- [x] Implement backfill script: `scripts/backfill-b2-embeddings.ts`.
- [ ] Run backfill dry-run: `npx tsx scripts/backfill-b2-embeddings.ts --dry-run`.
- [ ] Trigger batch re-embedding: `npx tsx scripts/backfill-b2-embeddings.ts`.
- [ ] Start worker(s): `npx tsx scripts/worker-seed-jobs.ts`.
- [ ] Monitor health: `npx tsx scripts/queue-health.ts`.

### 5. Cutover
- [ ] Switch production search default to B2 (Search API already uses B2 with fallback).
- [ ] Keep Hybrid C / Variant A as a fallback toggle (internal/debug only).

### 6. Post-Migration Cleanup
- [ ] Validate final retrieval metrics on the 200-font benchmark set.
- [ ] Clean up deprecated text-only embedding logic if no longer needed for fallback.

---

## 🛑 Rollback Plan
If production search quality regresses or performance degrades:
1. Revert `src/app/api/search/route.ts` to use Variant A (OpenRouter text embeddings).
2. Point search queries back to the original vector column (if separate).
3. Disable the background JIT worker.

## 🏁 Cutover Gates
- [ ] All 200+ fonts in production have valid B2 embeddings.
- [ ] JIT background worker successfully processes at least 10 fonts in < 5 mins (local GPU speed).
- [ ] Search latency (p95) remains within acceptable limits (< 1s for embedding + search).
