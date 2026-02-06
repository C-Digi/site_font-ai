# Decision Log: B2 Production Migration

## DECISION-001: Selection of B2 as Production Default
- **Date:** 2026-02-06
- **Status:** Approved
- **Context:** Benchmarking Variant A (text-only), B1 (image-only), B2 (image + short text), and B2-plus (image + long text) showed B2 provided the best balance of retrieval quality and simplicity.
- **Decision:** Use B2 (image + short text) for all production retrieval.
- **Justification:** B2 outperformed A in Recall@10 (0.36 vs 0.28) and showed better stability than B2-plus for top-10 results.

## DECISION-002: Queue-Based Background JIT Seeding
- **Date:** 2026-02-06
- **Status:** Approved
- **Context:** Local GPU resources (2x 3090) are not guaranteed to be online 24/7. Embedding generation is relatively slow (~5-10s per font).
- **Decision:** Implement JIT seeding as a background queue.
- **Justification:** This prevents blocking the user search request. If a font is found but lacks a B2 embedding, it will be served based on existing metadata/text similarity, and a re-embedding job will be queued.

## DECISION-003: External Font Binary Hosting
- **Date:** 2026-02-06
- **Status:** Approved
- **Context:** Self-hosting font binaries adds storage and bandwidth costs plus potential legal complexities.
- **Decision:** Continue to rely on external font hosting (e.g., Google Fonts, Fontshare).
- **Justification:** Minimizes infrastructure overhead. The rendering engine will download the font on-the-fly for embedding generation.

## DECISION-004: Vector Dimension Persistence (4096)
- **Date:** 2026-02-06
- **Status:** Approved
- **Context:** Current Supabase setup uses 4096 dimensions for Qwen3 embeddings.
- **Decision:** Maintain 4096 dimensions.
- **Justification:** Direct compatibility with `Qwen/Qwen3-VL-Embedding-8B` without dimensionality reduction which could lose information.

## DECISION-005: Retry Policy for Seed Jobs
- **Date:** 2026-02-06
- **Status:** Approved
- **Context:** Embedding generation and AI enrichment are subject to transient network failures or rate limits.
- **Decision:** Implement a 3-attempt retry policy with atomic claim/fail/complete operations.
- **Justification:** Exponential backoff is handled by the polling interval and the `attempts < max_attempts` check in `claim_seed_job`.

## DECISION-006: Cutover Criteria for Week 2
- **Date:** 2026-02-06
- **Status:** Approved
- **Context:** Transitioning to B2-only retrieval requires confidence in the new embedding corpus.
- **Decision:** Cutover happens when:
  1. 100% of the production corpus has been processed by the B2 worker.
  2. Queue health shows < 1% failure rate for the last 500 jobs.
  3. Recall@10 on benchmark set meets or exceeds 0.36.
- **Justification:** Ensures retrieval quality doesn't regress before removing the text-only fallback.
