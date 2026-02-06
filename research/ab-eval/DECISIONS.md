# DECISIONS — Offline A/B eval (text vs Qwen3-VL embeddings)

This file is the running decision log for the offline evaluation.

Guidance:

- Record **what** was decided, **why**, and **what happens next**.
- Tie each decision to a specific `run_id` and dataset IDs.

---

## Decision template

```yaml
date: YYYY-MM-DD
run_id: <run_id>
datasets:
  corpus_id: <corpus_id>
  queryset_id: <queryset_id>
  labelset_id: <labelset_id>

decision: GO_REPLACE | GO_HYBRID | NO_GO | NEEDS_MORE_DATA

rationale:
  - summary: >-
      (1–3 sentences.)
  - metrics:
      # include at least overall + by query_class
      recall_at_10: { A: <n>, B1: <n>, B2: <n>, C_best: <n> }
      mrr_at_10:    { A: <n>, B1: <n>, B2: <n>, C_best: <n> }
  - qualitative:
      - wins: (what improved)
      - losses: (what regressed)
      - failure_modes: (patterns)
  - cost_perf:
      - throughput_docs: <fonts/sec>
      - throughput_queries: <queries/sec>
      - peak_vram: <GB>
      - notes: (backend + parity validation)

next_steps:
  - (concrete follow-up tasks)
```

---

## Log

### 2026-02-05: Local Embedding Backend for Qwen3-VL

**Decision**: Use `transformers` + `qwen-vl-utils` (Option 1) instead of vLLM (Option 2) for generating Variant B embeddings.

**Rationale**:
- **Correctness First**: Official reports and internal assessment suggest vLLM's pooling/preprocessing for embeddings might diverge from the official implementation.
- **Reproducibility**: The official path is the reference for the model's performance on benchmarks.
- **Latency/Throughput**: While vLLM is faster, the offline evaluation of ~200 fonts is small enough that correctness outweighs the need for high-throughput serving.

**Hardware Mapping**:
- 2× RTX 3090 will use `device_map="auto"` via `transformers`/`accelerate` for the official path.
- NVLink will benefit inter-GPU communication if sharding occurs, though the 8B model fits in a single 24GB VRAM in FP16.

### 2026-02-06: 8B GPU Evaluation and Model Selection

**Decision**: GO_REPLACE (A -> B2). Use `Qwen/Qwen3-VL-Embedding-8B` as the primary embedding backend, potentially replacing text-only embeddings entirely or using a very low hybrid alpha.

**Rationale**:
- **Performance Jump**: Moving from 2B (CPU) to 8B (GPU) increased B2 Recall@10 from 0.289 to 0.360.
- **Vision Dominance**: The 8B vision-augmented variant (B2) now outperforms the hybrid (C) optimized for the 2B model. This indicates the 8B model captures enough semantic text info via its vision-language training that the external text-only embedding (A) adds marginal or even negative value in some configurations.
- **Latency**: GPU inference on 2× RTX 3090 Ti handles the 8B model comfortably (FP16), making it viable for production or near-real-time JIT seeding.

**Metrics**:
- **recall_at_10**: { A: 0.178, B1: 0.111, B2: 0.360, C_best: 0.360 }
- **mrr_at_10**:    { A: 0.700, B1: 0.519, B2: 1.000, C_best: 1.000 }

**Hardware Mapping**:
- 2× RTX 3090 Ti utilized.
- `device_map="auto"` successfully shards/loads the 8B model.
- Throughput: ~200 fonts embedded in approx 10 minutes (including glyph rendering).

**Next Steps**:
- Implement `Qwen/Qwen3-VL-Embedding-8B` in the main application's search/seeding pipeline.
- Consider dropping the `searches` table text-only cache or updating it to the 8B VL vectors.

### 2026-02-06: B2 vs B2-plus Ablation

**Decision**: NO_GO (B2-plus). Do not expand the B2 text payload to include full descriptions.

**Rationale**:
- **Regression at Top-K**: B2-plus showed a slight regression in Recall@10 (0.351 vs 0.360) despite having more textual context.
- **Efficiency**: B2 uses fewer tokens and provides better or equal performance in all key metrics except a marginal gain in Recall@20.
- **Payload Balance**: The vision-language model seems optimized for short, structured prompts. Longer descriptions may be introducing semantic noise or diluting the impact of the visual features in the joint embedding space.

**Metrics**:
- **recall_at_10**: { B2: 0.3604, B2-plus: 0.3509 }
- **recall_at_20**: { B2: 0.5549, B2-plus: 0.5579 }
- **mrr_at_10**:    { B2: 1.000, B2-plus: 1.000 }

**Next Steps**:
- Stick with the B2 payload (Name + Category + Tags + Image) for the production Qwen3-VL-8B embedding pipeline.

