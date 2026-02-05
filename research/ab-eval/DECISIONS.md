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

- _No decisions recorded yet._

