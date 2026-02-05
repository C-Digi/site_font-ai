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

- [x] Define `corpus_id` + produce corpus manifest — `DONE` (toy)
- [x] Define `queryset_id` + produce query set — `DONE` (toy)
- [x] Define `labelset_id` + produce labels file — `DONE` (toy)
- [ ] Validate dataset integrity (IDs match across files; URLs renderable) — `NOT STARTED`

### Artifacts (derived outputs)

- [ ] Create `run_id` and `RUN_META.json` — `NOT STARTED`
- [x] Generate glyph-sheet PNGs — `DONE` (toy)
- [x] Compute embeddings: A docs + A queries — `DONE` (toy)
- [x] Compute embeddings: B1 docs + B queries — `DONE` (scripts implemented)
- [x] Compute embeddings: B2 docs + B queries — `DONE` (scripts implemented)
- [x] Retrieval + scoring: A / B1 / B2 — `DONE` (scripts implemented)
- [x] Hybrid fusion scoring (Variant C, α sweep) — `DONE` (scripts implemented)
- [x] Produce report.md with qualitative wins/losses — `DONE` (toy)

### Decision

- [ ] Record go/no-go decision + rationale — `NOT STARTED`
- [ ] Record next-step plan (replace vs hybrid vs no-go) — `NOT STARTED`

---

## Status blocks (fill as you go)

### Current dataset IDs

- `corpus_id`: `toy-corpus-v1`
- `queryset_id`: `toy-queries-v1`
- `labelset_id`: `toy-labels-v1`

### Current run

- `run_id`: `run-text-baseline-toy`
- embedding backend:
  - baseline A: OpenRouter `qwen/qwen3-embedding-8b`
  - VL B: `transformers` + `qwen-vl-utils` (Option 1)
- similarity function: `cosine`
- normalization: `none`

### Snapshot (what we know right now)

- Baseline embedding entrypoint: [`generateEmbedding()`](src/lib/ai/embeddings.ts:4)
- Offline plan: [`_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md`](_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md)

---

## Status log

- 2026-02-05 — Initialized SSoT docs under `research/ab-eval/`.
- 2026-02-05 — Implemented offline evaluation harness (scripts + toy data).
- 2026-02-05 — Ran full text baseline pipeline on toy data.
- 2026-02-05 — Established local GPU inference approach for Variant B using `transformers` + `qwen-vl-utils`.
- 2026-02-05 — Integrated Variant B and C into the evaluation harness.
- 2026-02-05 — Added `embed_qwen3_vl_batch.py` for VL embeddings and `score_all_variants.py` for multi-variant reports and hybrid fusion.
- 2026-02-05 — Added `run_all.py` as a unified entrypoint for A/B/all variants.

