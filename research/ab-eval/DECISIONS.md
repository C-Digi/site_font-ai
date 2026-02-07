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

### 2026-02-07: Complex Query Evaluation Round (v1)

**Decision**: GO_REPLACE (A -> B2). Keep hybrid (C/D) as non-default experimental flags.

**Run metadata**:
- `run_id`: `2026-02-07__complex-v1__gpu-env-ready-rerun`
- `corpus`: `research/ab-eval/data/corpus.200.json`
- `queries`: `research/ab-eval/data/queries.complex.v1.json`
- `labels`: `research/ab-eval/data/labels.complex.v1.json`
- `interpreter`: `.venv-ab-eval\\Scripts\\python` (CUDA-visible)
- `canonical report`: `research/ab-eval/out/report_all.md`

**Rationale**:
- Complex round rerun completed end-to-end after GPU/env readiness confirmation.
- B2 strongly outperforms A globally and on most classes, with higher precision-oriented ranking quality (MRR@10).
- Hybrid C/D do not provide a stable global quality win vs B2 (especially on MRR@10), so they should remain optional and disabled by default.

**Metrics (global, from canonical run)**:
- **recall_at_10**: { A: 0.1617, B2: 0.3962, C_alpha_0_5: 0.4054, D_rrf: 0.4029 }
- **recall_at_20**: { A: 0.2858, B2: 0.6867, C_alpha_0_5: 0.5946, D_rrf: 0.6067 }
- **mrr_at_10**:    { A: 0.2531, B2: 0.5231, C_alpha_0_5: 0.4553, D_rrf: 0.4778 }

**Metrics (per class, Recall@10 / MRR@10)**:
- `functional_pair`: A 0.2417 / 0.2500, B2 0.3917 / 0.3658, C 0.3667 / 0.4458, D 0.4583 / 0.5754
- `historical_context`: A 0.0917 / 0.2000, B2 0.4167 / 0.6333, C 0.4167 / 0.4133, D 0.3750 / 0.4483
- `semantic_mood`: A 0.1983 / 0.3458, B2 0.2483 / 0.4683, C 0.4017 / 0.3469, D 0.3600 / 0.3342
- `visual_shape`: A 0.1150 / 0.2167, B2 0.5283 / 0.6250, C 0.4367 / 0.6150, D 0.4183 / 0.5533

**What this means**:
- Production default should remain **B2** (image + short structured text), not A.
- Hybrid should be a feature flag only (`default=false`) for class-targeted experimentation, not the global default.
- Prior partial artifact `research/ab-eval/out/report_complex.md` is non-canonical for this round (A-only/incomplete).

**Next Steps**:
- Preserve B2 as the production retrieval default path.
- Keep C/D behind an evaluation flag for targeted query classes and future ablations.
