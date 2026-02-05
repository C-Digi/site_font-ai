# PROGRESS — Offline A/B eval (text vs Qwen3-VL embeddings)

This file tracks execution status and provides a running log.

Status legend:

- `NOT STARTED`
- `IN PROGRESS`
- `BLOCKED`
- `DONE`

---

## Checklist

### SSoT docs

- [x] Create SSoT folder and entry docs — `DONE`
  - Notes: added README/runbook/progress/decisions.

### Datasets (freeze inputs)

- [ ] Define `corpus_id` + produce corpus manifest — `NOT STARTED`
- [ ] Define `queryset_id` + produce query set — `NOT STARTED`
- [ ] Define `labelset_id` + produce labels file — `NOT STARTED`
- [ ] Validate dataset integrity (IDs match across files; URLs renderable) — `NOT STARTED`

### Artifacts (derived outputs)

- [ ] Create `run_id` and `RUN_META.json` — `NOT STARTED`
- [ ] Generate glyph-sheet PNGs — `NOT STARTED`
- [ ] Compute embeddings: A docs + A queries — `NOT STARTED`
- [ ] Compute embeddings: B1 docs + B queries — `NOT STARTED`
- [ ] Compute embeddings: B2 docs + B queries — `NOT STARTED`
- [ ] Retrieval + scoring: A / B1 / B2 — `NOT STARTED`
- [ ] Hybrid fusion scoring (Variant C, α sweep) — `NOT STARTED`
- [ ] Produce report.md with qualitative wins/losses — `NOT STARTED`

### Decision

- [ ] Record go/no-go decision + rationale — `NOT STARTED`
- [ ] Record next-step plan (replace vs hybrid vs no-go) — `NOT STARTED`

---

## Status blocks (fill as you go)

### Current dataset IDs

- `corpus_id`: _TBD_
- `queryset_id`: _TBD_
- `labelset_id`: _TBD_

### Current run

- `run_id`: _TBD_
- embedding backend:
  - baseline A: OpenRouter `qwen/qwen3-embedding-8b`
  - VL B: _TBD_ (official vs vLLM; record exact)
- similarity function: _TBD_ (cosine vs dot)
- normalization: _TBD_

### Snapshot (what we know right now)

- Baseline embedding entrypoint: [`generateEmbedding()`](src/lib/ai/embeddings.ts:4)
- Offline plan: [`_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md`](_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md)

---

## Status log

- 2026-02-05 — Initialized SSoT docs under `research/ab-eval/`.

