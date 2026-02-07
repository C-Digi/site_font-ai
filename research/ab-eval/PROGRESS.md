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
- [x] Validate dataset integrity (IDs match across files; URLs renderable) — `DONE`
- [x] Generate real 200-font dataset and metadata-driven labels — `DONE`

### Artifacts (derived outputs)

- [x] Create `run_id` and `RUN_META.json` — `DONE` (toy)
- [x] Generate glyph-sheet PNGs — `DONE` (toy)
- [x] Compute embeddings: A docs + A queries — `DONE` (toy)
- [x] Compute embeddings: B1 docs + B queries — `DONE` (toy)
- [x] Compute embeddings: B2 docs + B queries — `DONE` (toy)
- [x] Retrieval + scoring: A / B1 / B2 — `DONE` (toy)
- [x] Hybrid fusion scoring (Variant C, α sweep) — `DONE` (toy)
- [x] Produce report.md with qualitative wins/losses — `DONE` (toy)

### Decision

- [x] Record go/no-go decision + rationale — `DONE`
- [x] Record next-step plan (replace vs hybrid vs no-go) — `DONE`

---

## Status blocks (fill as you go)

### Real 200-Font Run (End-to-End)
- **Status:** `DONE`

### Complex Query Set Evaluation (End-to-End)
- **Status:** `DONE` (2026-02-07)
- **Notes:** Completed with GPU acceleration on RTX 3090 Ti. Verified non-placeholder metrics for A, B2, C, D.

### Large Model VL Description Bakeoff (32B & 235B)
- **Status:** `DONE` (2026-02-07)
- **Notes:** Tested `qwen/qwen3-vl-32b-instruct` and `qwen/qwen3-vl-235b-a22b-instruct` via OpenRouter.
- **Results:** 100% success on both 10-font smoke and 50-font follow-on.
- **Artifacts:** `out/descriptions_bakeoff_qwen32_235_50.jsonl`, `out/descriptions_bakeoff_qwen32_235_50.summary.md`.
- **Runtime:** ~50 mins
- **Dataset:** 200 fonts
- **VL Model:** Qwen/Qwen3-VL-Embedding-2B
- **Key Findings:** 
  - Hybrid C (alpha=0.4) achieves Recall@10 0.33 vs 0.17 for Variant A.
  - Variant B2 (VL + Text) significantly outperforms A on metadata-proxy labels.
  - CPU inference is viable for batch runs but slow.
- **Issues:**
  - `flash-attn` installation failed due to missing CUDA; proceeded without it.
  - Used 2B model instead of 8B for CPU performance/memory.

### Complex Evaluation Round (v1) — GPU/env-ready rerun
- **Status:** `DONE`
- **Date (UTC):** 2026-02-07
- **Interpreter:** `.venv-ab-eval\\Scripts\\python` (CUDA verified)
- **Command:** `.\\.venv-ab-eval\\Scripts\\python research/ab-eval/py/run_all.py --dataset complex --variant all`
- **Canonical outputs:**
  - `research/ab-eval/out/report_all.json`
  - `research/ab-eval/out/report_all.md`
- **Completeness checks:**
  - Global metrics present and numeric for A, B2, C (alpha=0.5), D (RRF).
  - Per-query-class breakdown present for `functional_pair`, `historical_context`, `semantic_mood`, `visual_shape`.
  - Prior interrupted artifact `research/ab-eval/out/report_complex.md` remains non-canonical (A-only partial output).

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
- 2026-02-05 — Executed full ABC eval on toy dataset. Results recorded in `research/ab-eval/out/LATEST_RESULTS.md`. Pipeline confirmed working end-to-end.
- 2026-02-05 — Added 200-font corpus generator (`build_corpus_google_fonts.py`) and metadata-driven query/label generator (`build_queries_labels_metadata.py`).
- 2026-02-05 — Updated `run_all.py` to support `--dataset 200` preset.
- 2026-02-07 — Initialized Complex Evaluation Round (v1).
  - Created `queries.complex.v1.json` and `labels.complex.v1.json`.
  - Added Variant D (RRF) and per-class breakdown to `score_all_variants.py`.
  - Updated `run_all.py` with `complex` dataset preset.
- 2026-02-07 — Completed complex rerun with eval interpreter after GPU/env readiness confirmation.
  - Runtime checks passed (`torch.cuda.is_available() == True`; `.env.local` load path confirmed in eval scripts).
  - Ran end-to-end pipeline for `--dataset complex --variant all`.
  - Confirmed canonical report set is `report_all.json/.md` for this run; `report_complex.*` is stale/interrupted.

