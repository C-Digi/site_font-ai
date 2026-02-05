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

