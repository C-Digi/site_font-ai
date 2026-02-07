# Offline A/B eval SSoT — text vs Qwen3-VL embeddings

This folder is the **Single Source of Truth (SSoT)** for the offline A/B evaluation comparing:

- **Variant A (baseline):** current text embeddings (`qwen/qwen3-embedding-8b`) via [`generateEmbedding()`](src/lib/ai/embeddings.ts:4)
- **Variant B (VL):** Qwen3-VL doc embeddings using a deterministic glyph-sheet image (with B1/B2 sub-variants)
- **Variant C (hybrid):** fusion of A + B scores (α sweep)

Source plans:

- [`_05_guides/2026-02-04_qwen3-vl-embedding_assessment.md`](_05_guides/2026-02-04_qwen3-vl-embedding_assessment.md)
- [`_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md`](_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md)

## What lives here

- Procedures and definitions: [`RUNBOOK.md`](research/ab-eval/RUNBOOK.md)
- Progress + status log: [`PROGRESS.md`](research/ab-eval/PROGRESS.md)
- Decision log (go/no-go + follow-ups): [`DECISIONS.md`](research/ab-eval/DECISIONS.md)

## Directory conventions (for reproducibility)

This repo does not yet contain the datasets/artifacts, but the evaluation should write outputs under this structure.

- `research/ab-eval/datasets/`
  - Frozen inputs (corpus manifest, queries, labels)
- `research/ab-eval/out/`
  - Generated artifacts (JSONL, summaries, reports)

`run_id` naming (recommended):

```
YYYY-MM-DD__fonts-<N>__queries-<M>__A-vs-B1-B2__notes
```

Example:

```
2026-02-05__fonts-200__queries-40__A-vs-B1-B2__alpha-sweep
```

