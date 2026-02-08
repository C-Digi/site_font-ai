# Font Search RAG

## Requirements

### Quality-First Retrieval Iteration Gate
Before changing production retrieval defaults, run the quality-first experiment sequence (specimen v2, schema v2, uncertainty handling, and label adjudication), then rerun complex benchmark comparisons.

### Hybrid Retrieval as Explicit Opt-In
Hybrid strategies (C/D) must remain behind an explicit feature flag and disabled by default until they demonstrate stable global quality gains over B2.

## Completed

### Production Retrieval Default Uses B2
Production retrieval uses B2 (`Qwen/Qwen3-VL-Embedding-8B`) as the default embedding strategy with 4096-dimensional vectors.

### Search Pipeline Uses Cache Then Vector Search Then LLM
Search flow performs semantic cache lookup, vector retrieval (`match_fonts`), and LLM response generation in that order.

### JIT Seeding Is Queue-Based and Non-Blocking
Request-time search does not block on embedding generation; missing/unseeded recommendations enqueue jobs for background workers.

## Decision Links
- [DEC-20260208-lightspec-initialization](./decisions/DEC-20260208-lightspec-initialization.md)

## Scenarios
- A user submits a complex visual-shape query and receives B2-ranked results without waiting for any new embeddings to be generated inline.
- A recommendation references an unseeded font; the response returns immediately and a background job is queued for seeding.

