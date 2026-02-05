# Qwen3-VL-Embedding vs current text-only embedding (site_font-ai)

## Executive summary

We currently embed **font documents** as text-only (name/category/tags/AI description) and embed **user queries** as text-only via OpenRouter model `qwen/qwen3-embedding-8b` ([`generateEmbedding()`](src/lib/ai/embeddings.ts:4)). This works, but it is fundamentally limited by the fidelity of the *text proxy* for a font’s actual visual characteristics.

`Qwen/Qwen3-VL-Embedding-8B` is explicitly trained for **cross-modal retrieval** in a unified vector space (text ↔ image, and mixed). For typography search, a rendered “glyph sheet” image (alphanumerics + pangram) is a high-signal visual representation. Using Qwen3-VL-Embedding to embed **(image + short structured text)** per font is *very likely* to improve retrieval for style- and shape-driven prompts (e.g., “high x-height”, “open counters”, “condensed neo-grotesk”), while being neutral-to-slightly-worse for purely semantic/historical prompts compared to Qwen3 text-only embeddings.

Recommendation:
- Keep the current text embedding pipeline as the baseline.
- Run a short, instrumented A/B evaluation of **multimodal doc embeddings** (font image + text) vs baseline.
- If metrics and UX improve, move to a **hybrid retrieval** approach (text embedding for semantics + multimodal embedding for visual/style), optionally followed by a reranker.

## What we do today (baseline)

- Font seeding builds a text `contextString`:
  - `Name`, `Category`, `Tags`, `Description` (AI-enriched)
  - Then embeds it via OpenRouter `qwen/qwen3-embedding-8b`
  - See [`seed()`](scripts/seed-fonts.ts:77) and its `contextString` construction ([`contextString`](scripts/seed-fonts.ts:193)).
- Runtime search:
  - Embed user query text ([`POST()`](src/app/api/search/route.ts:37) → [`generateEmbedding(message)`](src/app/api/search/route.ts:50))
  - Vector search against `fonts.embedding` (4096-dim) via RPC [`match_fonts()`](supabase/migrations/003_upgrade_vector_dimension.sql:6)
  - LLM response from Gemini uses retrieved context.

Limitations:
- Font “visual truth” is mediated by AI descriptions (good, but imperfect; may hallucinate or omit key glyph traits).
- Retrieval learns similarity between *user language* and *AI language about fonts*; not similarity between user language and *visual properties*.

## What Qwen3-VL-Embedding enables

From the provided Qwen blog/model card:
- Input can be **text**, **image**, or **mixed**.
- Output embedding is **4096** for 8B (matches our DB vector dimension) and supports custom dimensions (MRL).
- Designed for multimodal retrieval; typically paired with a reranker for best quality.

Key implications for our domain:
- We can store per-font embeddings that encode **real glyph shapes**.
- User queries remain text; retrieval becomes **text → image/text** matching.
- We can reduce reliance on (or at least hedge against) AI-generated description quality.

## Proposed “glyph sheet” representation

Goal: one deterministic image per font that captures enough of the font’s identity.

Suggested image content (single PNG, fixed layout):
- Uppercase: `ABCDEFGHIJKLMNOPQRSTUVWXYZ`
- Lowercase: `abcdefghijklmnopqrstuvwxyz`
- Numerals: `0123456789`
- Common punctuation: `.,:;!?()[]{}"'“”‘’/\\@#%&*+-=_` (trim to fit)
- Pangram:
  - Primary: `Sphinx of black quartz, judge my vow.` (short)
  - Optional second line: `The quick brown fox jumps over the lazy dog.` (classic)

Style controls (important for embedding stability):
- Use *Regular (400)* if available; else nearest available.
- Fixed pixel dimensions (e.g., 1024×1024), monochrome text on solid background.
- Disable hinting/antialias variability where possible.
- Consistent line breaks and spacing.

Why this likely helps:
- Many “font vibe” queries are about proportions/contrast/terminal shapes; these are visually present.
- The image becomes a compact proxy for many hard-to-verbalize features.

## Architectural options

### Option A — Replace text-only embeddings with VL embeddings (single vector per font)

- For each font doc: embed **image + short structured text**.
- For user query: embed **text only**.
- Keep schema: `vector(4096)` stays unchanged.

Pros:
- Minimal DB change.
- Best chance to capture visual traits.

Cons:
- Qwen3-VL is slightly worse than Qwen3 text-only on pure text retrieval benchmarks (per the provided model card tables).
- More expensive to compute (vision encoder + larger model).

### Option B — Hybrid retrieval (recommended)

Store two embeddings per font:
- `embedding_text`: current text-only `qwen3-embedding-8b`
- `embedding_vl`: Qwen3-VL embedding from glyph sheet image (+ optional structured text)

At query time:
- Get `query_text_embedding` (text-only) and also `query_vl_embedding` (text-only using Qwen3-VL).
- Retrieve candidates from each space; merge with weighted scoring or reciprocal rank fusion.

Pros:
- Preserves best-in-class text matching (tags/history/use case).
- Adds a second channel specifically for visual similarity.
- Safer rollout: we can tune weights and fall back.

Cons:
- Requires schema/RPC updates (additional vector column and match function).

### Option C — Two-stage: embedding recall + VL reranker

- Stage 1: recall via baseline (fast)
- Stage 2: rerank top-K with `Qwen3-VL-Reranker` using (query text, font glyph sheet image + font text)

Pros:
- Maximum quality potential.
- Reranker can focus on fine-grained alignment.

Cons:
- Higher latency and infra complexity.

## Local inference feasibility on 2× RTX 3090 + NVLink

High-level answer: **Yes, feasible for local inference**, with caveats.

What the hardware implies:
- RTX 3090 has 24GB VRAM, strong FP16 tensor cores.
- Consumer Ampere (3090) is generally **FP16/TF32-first**; BF16 is not typically the sweet spot. Expect to run `float16`.
- NVLink **does not pool VRAM** into one address space for typical PyTorch/vLLM usage; it mainly improves **inter-GPU bandwidth** for tensor parallel collectives.

Why two GPUs might still matter:
- Tensor-parallel inference can shard weights across GPUs, reducing per-GPU memory pressure.
- NVLink can materially improve TP throughput vs PCIe-only (supported by public benchmarking anecdotes; verify on your box).

Practical expectation:
- `Qwen3-VL-Embedding-8B` in FP16 should *often* fit on a single 24GB GPU for short inputs, but headroom can be tight depending on:
  - max image resolution / number of images per prompt
  - max sequence length
  - attention implementation (FlashAttention reduces memory)
- With 2×3090, TP=2 is a safer “it will fit” setting.

Important deployment caveat:
- The model card examples mention vLLM pooling runner.
- There is at least one reported vLLM mismatch issue for this embedding model vs the official implementation (quality differences likely rooted in preprocessing). Treat vLLM as **"needs validation"** for embeddings until we confirm parity for our use case.

Windows note:
- Most mature multimodal serving stacks (vLLM + FlashAttention) are easiest on Linux. On Windows, plan on WSL2 or a Linux host.

## Evaluation plan (what to measure)

### Offline benchmark (fast feedback)

- Sample ~200 fonts across categories and sources.
- For each font, create glyph sheet image.
- Define ~30–50 queries representative of real users:
  - Style: “friendly geometric sans with round terminals”
  - Optical: “high contrast serif for editorial headlines”
  - Legibility: “large x-height for small UI text”
  - Utility: “monospace for coding, clear zero”
- For each query, label a small set of “good” fonts (manual, quick-and-dirty is fine).
- Compare:
  - Baseline (text-only Qwen3)
  - VL (doc: image+text; query: text)
  - Hybrid (fusion)
Metrics:
  - Recall@K (K=10,20)
  - MRR@K
  - Qualitative failure modes (confusing script/locale vs glyph shape, etc.)

### Online A/B (real feedback)

- Add an internal toggle (developer-only) to switch retrieval backend.
- Log (anonymized) query → top-N candidates and user’s click/favorite actions.
- Primary metric: click-through on top results; secondary: time-to-first-satisfactory.

## Implementation sketch (no code yet)

- Data pipeline additions:
  - Ensure we have stable font files (WOFF2/TTF/OTF) per font.
  - Render glyph sheet image deterministically.
- Embedding service:
  - Run Python service that exposes `/embed` for:
    - `{"text": "..."}`
    - `{"text": "...", "image": <bytes/url>}`
  - Backends to consider:
    - Official Qwen scripts/utilities for highest fidelity
    - vLLM pooling runner for throughput (after parity check)
- DB:
  - Option A: overwrite `fonts.embedding` with VL embeddings.
  - Option B: add `fonts.embedding_vl` and keep `fonts.embedding_text`.
- Search path:
  - Query embedding computed locally (no OpenRouter cost) OR keep OpenRouter for baseline and only local for VL until stable.

## Alternatives considered

- Improve text proxy without vision:
  - Compute measurable typography metrics (x-height ratio, width, contrast proxy, serif detection) from font outlines.
  - Store those as structured fields and include in embedding text.
  - Lower infra cost than VL; may capture some “visual” intent.

Rejected as a *replacement* because:
- Many traits are hard to robustly compute across varied font formats/styles.
- VL embedding can directly learn latent visual factors without hand-engineering.

