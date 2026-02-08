# RUNBOOK — Offline A/B eval (text vs Qwen3-VL embeddings)

**Latest Canonical Run:** `2026-02-07` (Complex Query Set)
- **Artifact Path:** `research/ab-eval/out/report_all.md`
- **JSON Source:** `research/ab-eval/out/report_all.json`
- **Visual Spot-Check:** `research/ab-eval/out/spot-check-complex-2026-02-07.html`
- **Description Winner:** Qwen3-VL-235B (`out/descriptions_bakeoff_qwen32_235_full200.jsonl`)

This runbook defines the **offline** evaluation procedures, dataset definitions, artifact naming, and “done”/decision criteria.

Authoritative plan references:

- [`_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md`](_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md)
- [`_05_guides/2026-02-04_qwen3-vl-embedding_assessment.md`](_05_guides/2026-02-04_qwen3-vl-embedding_assessment.md)

---

## 0) Goal and variants

Goal: determine whether Qwen3-VL embeddings improve **font retrieval quality** vs the current text-only baseline.

Variants (compute on identical corpora/queries/labels):

- **A (baseline / text):** current production-style embeddings via [`generateEmbedding()`](src/lib/ai/embeddings.ts:4)
  - docs: `Name/Category/Tags/Description` (seed-time proxy)
  - queries: raw user `message`
- **B (VL):** Qwen3-VL embedding
  - queries: embed query as text (VL text encoder)
  - docs:
    - **B1:** glyph sheet image only
    - **B2:** glyph sheet image + short structured text (Name/Category/Tags)
- **C (hybrid):** fuse scores from A + B
  - weighted sum `score = α * sim_text + (1-α) * sim_vl` (sweep α)
  - or RRF if weighted sum is unstable (record which you use)

Primary metrics:

- Recall@10, Recall@20
- MRR@10

---

## 1) Dataset definitions (frozen inputs)

All datasets should be **frozen** under [`research/ab-eval/data/`](research/ab-eval/data/) before computing artifacts.

### 1.0 Generating the 200-font dataset

To generate the reproducible 200-font corpus and its corresponding queries/labels:

1. **Build Corpus:** Fetch 200 fonts from Google Fonts (via Fontsource API).
   ```powershell
   python research/ab-eval/py/build_corpus_google_fonts.py --limit 200 --out research/ab-eval/data/corpus.200.json
   ```
2. **Generate Queries & Labels:** Derive ground truth from metadata.
   ```powershell
   python research/ab-eval/py/build_queries_labels_metadata.py --corpus research/ab-eval/data/corpus.200.json
   ```

3. **Generate VL Descriptions (Bakeoff):**
   ```powershell
   # Standard smoke run
   python research/ab-eval/py/gen_font_descriptions.py --limit 10 --out research/ab-eval/out/descriptions_bakeoff_smoke_v2.jsonl
   
   # Large model probe (32B and 235B)
   python research/ab-eval/py/gen_font_descriptions.py --models "qwen/qwen3-vl-32b-instruct,qwen/qwen3-vl-235b-a22b-instruct" --limit 50 --out research/ab-eval/out/descriptions_bakeoff_qwen32_235_50.jsonl

   # Full 200-font run (Winner + Challenger)
   python research/ab-eval/py/gen_font_descriptions.py --models "qwen/qwen3-vl-235b-a22b-instruct,qwen/qwen3-vl-32b-instruct" --out research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl --resume
   ```

Note: These labels are **proxy labels** derived from objective metadata (e.g., Google Fonts category). This evaluation tests whether retrieval respects known categorical constraints. It does NOT measure nuanced style matching (x-height, etc.) without human labels.

### 1.1 Corpus manifest (fonts)

Purpose: reproducible font set aligned to production docs, constrained to **renderable fonts** (valid downloadable files).

Target size:

- 200–500 fonts (start with 200 if rendering is the bottleneck)

Manifest format (choose one, but keep it stable across runs):

- `corpus.<corpus_id>.jsonl` (preferred)
  - One JSON object per font.
- `corpus.<corpus_id>.csv`

Required fields (minimum):

- `font_id` (stable identifier; can be name-based if needed, but must be unique)
- `name`
- `category`
- `tags` (array or delimited string)
- `description`
- `source`
- `file_url` (single canonical file; prefer Regular 400)

Required constraints:

- `file_url` must be validated (HEAD/GET) and must download a real font binary (WOFF2/TTF/OTF)
- Only include fonts we can render deterministically from the downloaded file

### 1.2 Query set

Purpose: represent real user intent with an explicit mix of query types.

Target size:

- 30–60 queries

Query format:

- `queries.<queryset_id>.jsonl`

Required fields:

- `query_id` (stable identifier)
- `query_text`
- `query_class` (categorical label; recommended values below)

Recommended `query_class` taxonomy:

- `visual_shape` (x-height, counters, terminals, width, contrast)
- `semantic_history` (era, inspiration, “in the style of…”, genre)
- `use_case` (UI, editorial, branding, coding/mono)
- `language_script` (if you include script/locale queries)

### 1.3 Human-reviewed label set (Medium v1)

Purpose: derive high-quality, nuanced style labels from human visual judgment for a diverse set of 20 queries.

Artifacts:
- `research/ab-eval/data/queries.medium.human.v1.json` (The query set)
- `research/ab-eval/human_labeling_medium_v1.html` (The interactive UI)
- `research/ab-eval/data/labels.medium.human.v1.json` (The canonical scoring labels)

Procedure:
1. **Prepare:** Generate queries and candidate pool.
   ```powershell
   python research/ab-eval/py/prepare_human_labeling.py
   ```
2. **Generate UI:** Create the interactive HTML labeling tool.
   ```powershell
   python research/ab-eval/py/gen_human_labeling_ui.py
   ```
3. **Label:** Open `human_labeling_medium_v1.html` in a browser. Complete binary labeling (0/1) for each query and font.
4. **Export:** Click "Export JSON" to download `judgments_medium_v1_<name>.json`.
5. **Convert:** Produce the canonical labels file.
   ```powershell
   python research/ab-eval/py/convert_judgments_to_labels.py --input <path_to_exported_json>
   ```

### 1.4 Human-reviewed medium label workflow (new canonicalization track)

Use this workflow to create a human-reviewed labelset that can replace/augment provisional complex labels.

Authoritative spec:

- [`research/ab-eval/HUMAN_LABELING_WORKFLOW_MEDIUM_V1.md`](research/ab-eval/HUMAN_LABELING_WORKFLOW_MEDIUM_V1.md)

Canonical targets:

- `research/ab-eval/data/queries.medium.human.v1.json`
- `research/ab-eval/data/labels.medium.human.v1.json`
- `research/ab-eval/data/labels.medium.human.v1.meta.json`

Raw provenance artifacts:

- `research/ab-eval/data/human/raw/judgments.medium.human.v1.jsonl`
- `research/ab-eval/data/human/raw/sessions.medium.human.v1.jsonl`
- `research/ab-eval/data/human/adjudication.medium.human.v1.json`

Operator flow (high-level):

- Freeze medium query slate (`16–24`, target `20`).
- Run blind-first visual review with graded `0/1/2` relevance per candidate card.
- Ensure minimum two reviewers per query, plus stratified audit pass.
- Apply deterministic conversion + adjudication to emit canonical labels.
- Promote only if agreement and conflict gates are satisfied.

Promotion gates (default):

- weighted kappa overall `>= 0.55`
- per-class weighted kappa `>= 0.45`
- unresolved conflict rate (pre-adjudication) `<= 0.25`
- each query yields `5–12` relevant fonts in final export

Scoring integration command after promotion:

```powershell
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_all.py --dataset 200 --queries research/ab-eval/data/queries.medium.human.v1.json --labels research/ab-eval/data/labels.medium.human.v1.json --variant all
```

---

## 2) Artifact paths and naming

All derived outputs go under:

- `research/ab-eval/artifacts/<run_id>/...`

`run_id` naming (recommended):

```
YYYY-MM-DD__corpus-<corpus_id>__queries-<queryset_id>__labels-<labelset_id>
```

Each run folder should contain (at minimum):

- `RUN_META.json`
  - `run_id`, timestamps, git commit hash, machine info, embedding backend info
  - dataset IDs: `corpus_id`, `queryset_id`, `labelset_id`
- `glyph_sheets/`
  - one PNG per `font_id`
- `embeddings/`
  - `docs.variant-<A|B1|B2>.npy|parquet|jsonl` (pick one format)
  - `queries.variant-<A|B>.npy|...`
- `rankings/`
  - top-K results per query per variant
- `metrics/`
  - summary table (CSV/JSON)
  - per-query breakdown (CSV/JSON)
- `report.md`
  - human-readable summary + qualitative notes

Recordable invariants (should not change within a run):

- glyph sheet image spec (size, text content, colors)
- similarity function (cosine vs dot) and normalization behavior
- variant definitions (especially B2 text template and α sweep range)

---

## 3) Procedures (high-level)

### Step 1 — Freeze datasets

Output:

- Corpus manifest file under `datasets/`
- Query set file under `datasets/`
- Labels file under `datasets/`

Verification:

- Every `font_id` in labels exists in corpus
- Every `query_id` in labels exists in query set
- Manifest URLs validated and renderable

### Step 2 — Generate deterministic glyph sheets

Output:

- `artifacts/<run_id>/glyph_sheets/*.png`

Image spec (recommended; keep stable):

- 1024×1024 PNG
- black text on white background (or the inverse; choose one)
- content:
  - `ABCDEFGHIJKLMNOPQRSTUVWXYZ`
  - `abcdefghijklmnopqrstuvwxyz`
  - `0123456789`
  - `Sphinx of black quartz, judge my vow.`

Verification:

- Spot-check at least 10 random fonts for correct rendering (no fallback font)
- Confirm file count equals corpus size

### Step 3 — Compute embeddings

Compute embeddings for:

- A docs (text) + A queries (text)
- B docs (B1 image-only and B2 image+text) + B queries (text)

Record (for later cost/perf comparisons):

- embedding backend (official vs vLLM, etc.)
- throughput (docs/sec; queries/sec)
- peak VRAM

Verification:

- embedding dimension is consistent (expected 4096 for the 8B variants)
- end-to-end similarity computation runs on a small subset

### Step 4 — Retrieve + score

For each variant (A, B1, B2, C):

- compute top-K per query (K=20 is sufficient to score Recall@20)
- compute Recall@10/20 and MRR@10
- produce per-query tables and a summary table

Verification:

- metrics are produced for all queries
- sanity-check: random query should not return identical rankings across all variants

### Step 5 — Qualitative review

For each query class (`visual_shape`, `semantic_history`, etc.):

- list “wins” where VL/hybrid improves ranking meaningfully
- list “losses” where baseline is better
- annotate failure modes (script mismatch, category confusion, “style drift”, etc.)

Output:

---

## 4) Execution (The Runner)

The main entry point for running the evaluation is [`research/ab-eval/py/run_all.py`](research/ab-eval/py/run_all.py).

### 4.0 VL description generation bakeoff (glyph-sheet image -> typographic description)

Use [`research/ab-eval/py/gen_font_descriptions.py`](research/ab-eval/py/gen_font_descriptions.py) to generate model-comparison JSONL artifacts for vision-grounded font descriptions.

Scope and behavior:

- Input corpus defaults to `research/ab-eval/data/corpus.200.json`.
- Glyph sheets are resolved from `research/ab-eval/out/glyphs` by font name (configurable).
- Prompt intentionally excludes font-family-name leakage and asks for typographic attributes only.
- Supports provider routing:
  - Gemini API models (e.g., `gemini-3-flash-preview`, `gemini-2.5-flash-lite-preview-09-2025`)
  - Local Qwen VL instruct models via Transformers (e.g., `Qwen/Qwen3-VL-8B-Instruct`, `Qwen/Qwen3-VL-4B-Instruct`)
  - OpenRouter multimodal fallback (e.g., `qwen/qwen3-vl-8b-instruct`, optional `google/gemini-2.5-flash-image`)

Required env keys by provider:

- Gemini: `GEMINI_API_KEY`
- OpenRouter: `OPENROUTER_API_KEY`
- Local Qwen: local GPU/runtime dependencies from [`research/ab-eval/py/requirements-vl.txt`](research/ab-eval/py/requirements-vl.txt)

Example smoke run (10 fonts, required slate):

```powershell
.\.venv-ab-eval\Scripts\python research/ab-eval/py/gen_font_descriptions.py --limit 10 --models "gemini-3-flash-preview,gemini-2.5-flash-lite-preview-09-2025,Qwen/Qwen3-VL-8B-Instruct,Qwen/Qwen3-VL-4B-Instruct,qwen/qwen3-vl-8b-instruct" --out research/ab-eval/out/descriptions_bakeoff_smoke.jsonl --resume
```

Include optional fallback model in the same run:

```powershell
.\.venv-ab-eval\Scripts\python research/ab-eval/py/gen_font_descriptions.py --limit 10 --models "gemini-3-flash-preview,gemini-2.5-flash-lite-preview-09-2025,Qwen/Qwen3-VL-8B-Instruct,Qwen/Qwen3-VL-4B-Instruct,qwen/qwen3-vl-8b-instruct" --include-optional-fallback --out research/ab-eval/out/descriptions_bakeoff_smoke_with_optional.jsonl --resume
```

Dry-run to validate routing/resume without API calls:

```powershell
.\.venv-ab-eval\Scripts\python research/ab-eval/py/gen_font_descriptions.py --limit 10 --dry-run --out research/ab-eval/out/descriptions_bakeoff_dryrun.jsonl
```

Output schema (JSONL row):

- `font_name`, `model`, `provider`, `prompt_template`, `description`
- `metadata` (timings, usage/tokens when available, parse details)
- `status` (`ok|error|dry_run`) and `error`

### 4.1 Running the 200-font pipeline

To run the full evaluation on the 200-font dataset:
```powershell
python research/ab-eval/py/run_all.py --dataset 200 --variant all
```

### 4.2 Running the complex pipeline (A/B2/C/D)

To run the evaluation on the complex query dataset (v1):
```powershell
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_all.py --dataset complex --variant all
```

Run note (2026-02-07 GPU/env-ready rerun):

- Treat [`research/ab-eval/out/report_all.md`](research/ab-eval/out/report_all.md) and [`research/ab-eval/out/report_all.json`](research/ab-eval/out/report_all.json) as the canonical outputs for complex v1.
- Treat [`research/ab-eval/out/report_complex.md`](research/ab-eval/out/report_complex.md) and [`research/ab-eval/out/report_complex.json`](research/ab-eval/out/report_complex.json) as stale/interrupted artifacts from prior attempts.

- **Variant A**: Text baseline
- **Variant B2**: VL + Short Metadata
- **Variant C**: Weighted Fusion (A + B2)
- **Variant D**: Reciprocal Rank Fusion (A + B2)

### 4.3 Running the toy pipeline (A/B/C)

To run the full evaluation on the toy dataset:
```powershell
python research/ab-eval/py/run_all.py --dataset toy --variant all
```

- `artifacts/<run_id>/report.md`

---

## 4) Definition of DONE (offline evaluation)

The offline evaluation is **done** when all of the following exist for at least one run:

- Frozen dataset files (corpus, queries, labels) committed to the repo under `research/ab-eval/datasets/` (or, if too large, committed as stubs + stored elsewhere with a pointer recorded in `RUN_META.json`)
- A complete `artifacts/<run_id>/` folder with:
  - glyph sheets (for the corpus)
  - embeddings for A, B1, B2 (and C if used)
  - rankings + metrics (summary + per-query)
  - a human-readable report with qualitative notes
- A recorded decision in [`DECISIONS.md`](research/ab-eval/DECISIONS.md)

---

## 5) Decision criteria (go/no-go)

This is a **retrieval-quality** decision with a cost/perf sanity check.

### 5.1 Proposed success criteria

Treat these as defaults; adjust only if you write down the rationale in the run report.

- On `visual_shape` queries:
  - **B1/B2 or C** improves Recall@10 by **≥ 10% absolute** vs A
- On `semantic_history` + `use_case` queries:
  - no “strong regression”
  - suggested guardrail: Recall@10 drop ≤ 5% absolute, and MRR@10 drop ≤ 0.03

### 5.2 Cost / feasibility guardrails

- Embedding throughput is acceptable for the intended serving plan (local GPUs vs API)
- If using a high-throughput backend (e.g., vLLM), parity concerns are addressed via a small parity check run (recorded in `RUN_META.json`)

### 5.3 Outcomes

- **GO (replace):** VL (B2) beats baseline broadly and doesn’t regress semantic queries meaningfully.
  - Next: plan schema/search changes for full rollout OR overwrite single embedding if doing replacement.
- **GO (hybrid):** VL wins on visual queries but baseline wins on semantic.
  - Next: implement hybrid retrieval (two vectors + fusion) per assessment recommendation.
- **NO-GO:** No meaningful improvement, or large regressions / operational infeasibility.
  - Next: keep baseline; consider alternative improvements (better text proxy, structured metrics, reranker).

