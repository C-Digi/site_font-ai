# DEC-20260206-01-production-b2-migration

- **Date:** 2026-02-06
- **Status:** Approved
- **Type:** Architectural Decision

## Context
Benchmarking Variant A (text-only), B1 (image-only), B2 (image + short text), and B2-plus (image + long text) showed B2 provided the best balance of retrieval quality and simplicity. Local GPU resources (2x 3090) are not guaranteed to be online 24/7. Embedding generation is relatively slow (~5-10s per font).

## Decisions
1. **Selection of B2 as Production Default**: Use B2 (image + short text) for all production retrieval.
2. **Queue-Based Background JIT Seeding**: Implement JIT seeding as a background queue.
3. **External Font Binary Hosting**: Continue to rely on external font hosting (e.g., Google Fonts, Fontshare).
4. **Vector Dimension Persistence (4096)**: Maintain 4096 dimensions for direct compatibility with `Qwen/Qwen3-VL-Embedding-8B`.
5. **Retry Policy for Seed Jobs**: Implement a 3-attempt retry policy with atomic claim/fail/complete operations.
6. **Cutover Criteria**: Cutover happens when 100% of corpus is processed, queue health < 1% failure, and Recall@10 >= 0.36.

## Justification
- B2 outperformed A in Recall@10 (0.36 vs 0.28) and showed better stability than B2-plus.
- Background queue prevents blocking user search requests.
- External hosting minimizes infrastructure overhead.
- Dimensionality preservation avoids information loss.

## Consequences
- Requires background worker process to be running (`scripts/worker-seed-jobs.ts`).
- Search results for unseeded fonts may be sub-optimal until background job completes.
