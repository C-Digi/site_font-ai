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

### 2026-02-07: Complex Query Set Evaluation - B2 vs Baseline

```yaml
date: 2026-02-07
run_id: complex_all_v1
datasets:
  corpus_id: corpus.200
  queryset_id: queries.complex.v1
  labelset_id: labels.complex.v1

decision: GO_REPLACE

rationale:
  - summary: >-
      Variant B2 (Vision + Metadata) significantly outperforms the text baseline (A) across all complex query classes,
      particularly in visual shape and historical context. B2-plus shows even higher recall but at the cost of
      higher retrieval noise in some classes. Hybrid C/D offer marginal gains in specific classes but introduce complexity.
  - metrics:
      global:
        recall_at_10: { A: 0.1617, B1: 0.2283, B2: 0.3962, B2-plus: 0.4575, C_0.5: 0.4054, D_RRF: 0.4029 }
        mrr_at_10:    { A: 0.2531, B1: 0.2035, B2: 0.5231, B2-plus: 0.4833, C_0.5: 0.4553, D_RRF: 0.4778 }
      by_class_r10:
        visual_shape:       { A: 0.1150, B2: 0.5283, D: 0.4183 }
        semantic_mood:      { A: 0.1983, B2: 0.2483, D: 0.3600 }
        historical_context: { A: 0.0917, B2: 0.4167, D: 0.3750 }
        functional_pair:    { A: 0.2417, B2: 0.3917, D: 0.4583 }
  - qualitative:
      - wins: Massive improvement in "visual_shape" (e.g. "geometric sans") where text often hallucinated handwriting fonts.
      - losses: Some "semantic_mood" queries (e.g. "stern and authoritative") still benefit from text semantics, though B2 is competitive.
  - cost_perf:
      - peak_vram: ~16GB (RTX 3090 Ti)
      - notes: B2 is the sweet spot for production.

next_steps:
  - Finalize B2 as the production default retrieval path.
  - Keep Hybrid D (RRF) as a research toggle for "functional_pair" specialized searches.
```

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

### 2026-02-07: Description Model Selection (235B vs 32B)

**Decision**: GO_PRODUCTION (Qwen3-VL-235B). Use Qwen3-VL-235B for generating the 200-font production answer key.

**Rationale**:
- **Nuance**: 235B captures finer typographic details (e.g., specific terminal shapes) than 8B or 32B.
- **Stability**: 100% success rate on 398 total generations (235B and 32B combined).
- **Cost**: OpenRouter DeepInfra pricing (~$0.0003/font) makes the 235B model economically viable for offline seeding.
- **Latency**: ~5.5s per font is acceptable for background processing.

**Artifacts**:
- `research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl`
- `research/ab-eval/out/description_model_bakeoff_consolidated.md`

**Next Steps**:
- Submit human-review packet.
- Upon approval, use 235B descriptions to generate the final 4096-dim vector embeddings.

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

### 2026-02-08: Quality-First Core Functionality Experiment Plan (No Production Rush)

**Decision**: NEEDS_MORE_DATA. Prioritize targeted quality experiments over production rollout and over additional model-shopping.

**Rationale**:
- Current descriptor outputs in `research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl` show repetitive, generic attribute patterns across many fonts.
- The current specimen renderer likely limits visual signal for nuanced extraction:
  - `research/ab-eval/py/render_glyph_sheet.py` currently renders a small deterministic sheet with partial alphabet and no pangram.
- Current description schema is too shallow for robust vibe/style retrieval:
  - Prompt in `research/ab-eval/py/gen_font_descriptions.py` enforces only a small free-form set of fields and 3–6 mood/use-case tags.

**Selected Approach**:
- Improve and validate **input representation + ontology quality** first, then re-score retrieval.

**Planned Experiment Sequence**:
- Step A — Specimen v2 (highest impact)
  - Move to 1024 deterministic layout.
  - Include full `A–Z`, `a–z`, `0–9`, punctuation, pangram, and a dedicated micro-tell strip (`a g 0 1 Q R & @`).
- Step B — Attribute schema v2 (backward-compatible)
  - Keep existing top-level fields for compatibility.
  - Add fixed-vocabulary scored blocks for moods and use-cases (continuous ranking, not only list presence).
  - Add confidence and brief evidence notes per attribute.
- Step C — Uncertainty discipline
  - Require explicit `unknown`/`uncertain` handling when evidence is weak.
- Step C.5 — Label SSoT review gate (`labels.complex.v1.json`)
  - Treat `research/ab-eval/data/labels.complex.v1.json` as provisional until human-reviewed.
  - Perform a focused adjudication pass (especially borderline/subjective vibe queries).
  - Freeze reviewed labels as canonical before using them for score-driven comparisons.
- Step D — Targeted quality validation before retrieval reruns
  - A/B only these levers:
    - old specimen + old schema
    - new specimen + old schema
    - new specimen + new schema
  - Use human-review workflow to measure technical accuracy + vibe fidelity agreement.
  - If any quantitative scoring references `labels.complex.v1.json`, run only after Step C.5 sign-off.
- Step E — Retrieval rerun only after quality gate
  - Regenerate embeddings with winning schema and rerun complex benchmark.

**Open Questions to Resolve Before Implementation**:
- Final fixed vocab lists and sizes for mood/use-case dimensions.
- Score scale to standardize (`none/low/medium/high/excellent` mapped to numeric 0–4).
- Minimum UI surfacing policy (e.g., show top 3–6 labels while storing full scored vectors).

**Next Steps**:
- Log this plan as the active blocker-clearing priority for the next engineering session.
- Keep production retrieval default unchanged (B2) while this quality workstream runs.
