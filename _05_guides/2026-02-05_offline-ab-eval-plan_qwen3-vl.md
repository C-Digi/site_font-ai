# Offline A/B evaluation plan: text embedding vs Qwen3-VL embedding (fonts)

Related context: [`_05_guides/2026-02-04_qwen3-vl-embedding_assessment.md`](_05_guides/2026-02-04_qwen3-vl-embedding_assessment.md)

```yaml
task: Run a small offline A/B evaluation to determine whether Qwen3-VL embeddings improve font retrieval.
approach: Hybrid evaluation harness comparing (A) current text-only embeddings, (B) VL doc embeddings using glyph-sheet images, and (C) a simple fusion/hybrid scorer.

context_gathered:
  - Current baseline uses OpenRouter text embeddings with model `qwen/qwen3-embedding-8b` via [`generateEmbedding()`](src/lib/ai/embeddings.ts:4).
  - Seed-time doc embedding text is `Name/Category/Tags/Description` ([`contextString`](scripts/seed-fonts.ts:193)).
  - Query-time embedding is the raw user `message` ([`POST()`](src/app/api/search/route.ts:37)).
  - Font retrieval today is single-space vector search via RPC [`match_fonts()`](supabase/migrations/003_upgrade_vector_dimension.sql:6).

implementation_plan:
  - step: Define the evaluation corpus (fonts) and ensure each font has a downloadable file URL.
    verification: Produce a manifest (CSV/JSON) of N fonts with validated font file URLs and metadata fields (name/category/tags/desc/source).
    dependencies: None.

  - step: Define the evaluation query set and relevance labels.
    verification: A single labels file that maps each query -> a set of relevant font names (or graded relevance 0/1/2).
    dependencies: Corpus manifest.

  - step: Generate deterministic glyph-sheet images for each font.
    verification: For every font in the manifest, output a PNG with consistent dimensions and layout; spot-check 10 random fonts for rendering correctness.
    dependencies: Corpus manifest.

  - step: Compute embeddings for the A/B variants.
    verification: For each variant, produce embedding files with consistent dimension; confirm cosine similarity computation runs end-to-end.
    dependencies: Glyph-sheet images; labels; access to baseline embedding API.

  - step: Run retrieval + scoring for each variant (A/B/C), compare metrics.
    verification: Produce a single report table with Recall@K and MRR@K plus per-query breakdown and qualitative notes.
    dependencies: Embeddings computed.

alternatives_considered:
  - approach: Only run VL embeddings and ignore baseline.
    pros:
      - Faster to implement.
    cons:
      - No apples-to-apples evidence for improvement.
    rejected_because: We need a grounded go/no-go decision with baseline comparables.

validation_strategy:
  - Offline metrics: Recall@10/20 and MRR@10 on a labeled query set.
  - Qualitative review: Inspect “wins” and “losses” by query type (visual/style vs semantic/history).
  - Cost/perf: Record embedding throughput (fonts/sec; queries/sec) and VRAM usage on local GPUs.

open_questions:
  - Do we want the offline benchmark to reflect only “real inventory” fonts (those with valid downloadable files), or include metadata-only entries too?
  - What query mix should dominate: UI/product design prompts vs print/editorial vs branding?
```

## Scope targets (keep it small)

- Fonts in corpus: 200–500 (start at 200 if glyph rendering is the bottleneck)
- Queries: 30–60
- Labels per query: 5–20 relevant fonts (binary relevance is fine)

## Step details

### Define the corpus manifest

Goal: make the dataset reproducible and debuggable.

- Data source options:
  - Export from Supabase `fonts` table (preferred, because it matches production docs).
  - Or regenerate a small list from Google Fonts API.

- Manifest fields (minimum):
  - `name`
  - `category`
  - `tags`
  - `description`
  - `source`
  - `file_url` (choose a single canonical file per font: Regular 400 if possible)

- URL validation requirement:
  - Use the existing `HEAD` validation concept used in [`validateUrl()`](scripts/seed-fonts.ts:31) (same logic, just applied during corpus build).

Why this matters:
- Our current seeding includes a known risk: some sources may have placeholder URLs (not a real font binary). The offline benchmark should only include fonts we can actually render.

### Define the query set + labels

Goal: measure what users actually care about, not generic IR benchmarks.

- Create a query set with an explicit mix:
  - Visual/shape-driven (expected to benefit from VL)
    - “high x-height, open counters, readable at 12px”
    - “condensed grotesk for dense UI tables”
    - “soft rounded terminals, friendly tone”
    - “very high contrast modern serif, fashion editorial”
  - Semantic/use-case-driven (baseline likely strong)
    - “serif inspired by old-style book typography”
    - “geometric sans similar to Futura”
    - “typewriter / monospaced coding font”

- Labeling approach options:
  - Manual labeling (fast, small set): you pick relevant fonts per query.
  - “Bootstrap then edit”: run baseline retrieval, select good candidates, then add a few “missed but relevant” fonts.

Label format suggestions:
- JSON:
  - `[{ "query": "...", "relevant": ["Font A", "Font B"], "notes": "optional" }]`

### Generate glyph-sheet images (deterministic)

Goal: each font gets *one* stable visual representation.

- Image spec (recommended):
  - Canvas: 1024×1024 PNG
  - Foreground/background: black text on white background (or invert; just be consistent)
  - Font size and line spacing: fixed constants
  - Text content (exact):
    - `ABCDEFGHIJKLMNOPQRSTUVWXYZ`
    - `abcdefghijklmnopqrstuvwxyz`
    - `0123456789`
    - `Sphinx of black quartz, judge my vow.`
    - Optional: `The quick brown fox jumps over the lazy dog.`

- Determinism notes:
  - Prefer TTF/OTF sources for rendering stability.
  - If using WOFF2, ensure the renderer supports it reliably.
  - Avoid per-machine font fallback: render directly from the downloaded font file.

### Embedding variants to compute

Use identical query/corpus sets across all variants.

#### Variant A (baseline): text-only Qwen3 embeddings

- Queries:
  - Embed `message` exactly as production does ([`generateEmbedding(message)`](src/app/api/search/route.ts:50)).
- Docs:
  - Embed `Name/Category/Tags/Description` like seed-time ([`contextString`](scripts/seed-fonts.ts:193)).

#### Variant B (VL): Qwen3-VL embedding with glyph-sheet images

- Queries:
  - Embed the query as **text** using Qwen3-VL-Embedding.
- Docs:
  - Embed **image only** (glyph sheet), and also test **image + short structured text** (two sub-variants):
    - B1: `{image}`
    - B2: `{image, text: "Name: ... Category: ... Tags: ..."}`

Rationale:
- B1 isolates “pure visual” similarity.
- B2 tests whether light metadata helps disambiguate category/script.

#### Variant C (hybrid fusion): combine A + B scores

- Candidate generation:
  - Compute similarities in both spaces; either:
    - Union top-K from both, then rescore
    - Or do reciprocal-rank fusion (RRF)
- Scoring:
  - Start with a simple weighted sum:
    - `score = α * sim_text + (1-α) * sim_vl`
  - Sweep α across e.g. 0.2 / 0.5 / 0.8.

### Retrieval + metrics

- Similarity:
  - Use cosine similarity (if embeddings are normalized) or dot-product consistent with how the embedding model is intended.
- Primary metrics:
  - Recall@10
  - Recall@20
  - MRR@10

- Per-query breakdown:
  - Identify which query classes improve (visual vs semantic)
  - Save a “top 10 results” table for each query and variant

Success criteria (proposed):
- For visual/style-driven queries, VL or hybrid improves Recall@10 by ≥ 10–15% absolute without strongly regressing semantic queries.

## Infra / runtime plan for local GPUs (2×3090)

- Target environment:
  - Prefer Linux or WSL2 for best compatibility with modern attention kernels.
- Execution modes to consider:
  - Official HF/Transformers-style embedding script (highest fidelity; simplest correctness story)
  - vLLM pooling runner (higher throughput, but treat as “needs parity validation” for embeddings)

Instrumentation to capture:
- VRAM usage peak
- embeddings/sec for docs (batchable)
- embeddings/sec for queries (latency-oriented)

## Risks and mitigations

- Risk: Font file URLs are inconsistent / not renderable.
  - Mitigation: strict manifest validation; exclude non-renderable fonts.

- Risk: Glyph-sheet rendering introduces noise (different rasterization settings).
  - Mitigation: deterministic renderer settings; fixed image spec; single machine baseline.

- Risk: VL embeddings help only in some query slices.
  - Mitigation: report by query class; consider hybrid fusion rather than replacement.

- Risk: Serving stack differences (e.g., vLLM vs official) change embedding outputs.
  - Mitigation: treat “embedding backend” as a factor; validate parity on a small subset before scaling.

