# Rollout Runbook: B2 Retrieval Migration

This runbook outlines the operational steps for transitioning the production environment from text-only embeddings to B2 (Multimodal) embeddings over a 2-week period.

## Week 1: Infrastructure & Pipeline Implementation

### 1. Database Preparation
- [ ] Verify Supabase schema supports 4096-dimensional vectors (already implemented).
- [ ] Create `background_tasks` table (or similar) to track JIT re-embedding status.

### 2. Backend Integration
- [ ] Implement `B2` embedding generation in `src/lib/ai/embeddings.ts`.
  - Input: Font Glyph Image + Short Text (Name, Category, Tags).
- [ ] Update `src/app/api/search/route.ts` to use B2 for query embedding.
- [ ] Implement the background queue mechanism for JIT seeding.
  - Search request triggers a queue entry if font needs B2 embedding.
  - Background worker processes queue periodically.

### 3. Pipeline Validation
- [ ] Run end-to-end local smoke test:
  - Input query -> B2 Embedding -> Vector Search -> Results.
- [ ] Validate glyph rendering consistency in the production pipeline.

## Week 2: Data Migration & Cutover

### 4. Batch Re-embedding
- [ ] Trigger batch re-embedding script for all existing fonts in the production database.
- [ ] Monitor background queue for failures (e.g., rendering issues, network timeouts).

### 5. Cutover
- [ ] Switch production search default to B2.
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
