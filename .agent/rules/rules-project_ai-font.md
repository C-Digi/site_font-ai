# Project Coding Rules & Guidelines for AI Assistant (GEMINI.md)

## 1. Project Overview

- **Project Name:** `site_font-ai` (AI Font Explorer)
- **Domain:** `type-hype.com`
- **Description:** An AI-powered font discovery tool that uses semantic search and RAG to recommend fonts based on user descriptions.
- **Primary Goal:** Provide a seamless, intelligent interface for finding fonts that match specific moods, use cases, or styles.

## 2. Technology Stack

- **Language:** `TypeScript 5.7.3`
- **Framework:** `Next.js 15.1.6` (App Router)
- **UI Library:** `React 19`, `Tailwind CSS 4`, `Lucide React`
- **State Management:** React state, `next-themes` for theme management.
- **Database/Vector:** `Supabase` (with `pgvector`)
- **AI/LLM:** `gemini-2.0-flash-lite` (Search), `gemini-3-pro-preview` (Seeding)
- **Embeddings (Production Default):** `Qwen/Qwen3-VL-Embedding-8B` (B2 multimodal strategy, 4096 dimensions)
- **Embedding Fallback:** OpenRouter text embedding (`qwen/qwen3-embedding-8b`) for resilience/debug only
- **Embedding Context (B2):** `Glyph Sheet Image` + short structured text (`Name`, `Category`, `Tags`)
- **Embedding Context (Not Default):** Long descriptions (`B2-plus`) and Hybrid fusion (`C`) are research/ablation options, not production default
- **Package Manager:** `npm`
- **Seeding:** `scripts/seed-fonts.ts` + queue-based async seeding (`seed_jobs` + worker scripts)

## 3. Coding Style & Conventions

- **Naming Conventions:**
  - `Components`: `PascalCase` filenames and component names (e.g., `src/components/FontCard.tsx`).
  - `Functions`: `camelCase` (e.g., `generateEmbedding`, `cn`).
  - `Files/Folders`: `kebab-case` or standard Next.js names (e.g., `layout.tsx`, `page.tsx`).
- **Styling:** Use Tailwind CSS utility classes. Use the `cn` utility from `src/lib/utils.ts` for conditional class merging.
- **Types:** Use TypeScript strictly. Define interfaces in `src/lib/types.ts` or close to usage.

## 4. Directory Structure

- `src/app/`: Next.js App Router (pages, layouts, API routes).
- `src/components/`: Reusable UI components.
- `src/lib/`: Shared utilities, types, and AI logic.
- `src/lib/ai/`: AI-specific logic like embedding generation.
- `supabase/migrations/`: Database schema and function definitions.
- `public/`: Static assets.

## 5. Architecture & Patterns

- **RAG (Retrieval-Augmented Generation):**
  1. **Query Embedding (Default):** Generate B2 query vector via configured VL embedding endpoint.
  2. **Semantic Cache:** Check `searches` table for high-similarity hits (threshold > 0.95).
  3. **Vector Search:** Query `fonts` table using `match_fonts` RPC (threshold > 0.5).
  4. **LLM Generation:** Send query + retrieved font context to Gemini with a strict JSON system prompt.
  5. **JIT Seeding (Non-Blocking):** If a recommended font is missing/unseeded, enqueue a `seed_jobs` record and return the response immediately.
  6. **Background Processing:** Worker claims jobs, generates B2 embeddings, upserts font records, retries failures with max-attempt policy.
  7. **Caching:** Save the final response in the `searches` table.
- **Database Interactions:** Use `supabase.rpc` for vector similarity searches.
- **Server-Side API:** API routes in `src/app/api` handle the heavy lifting (AI, DB).
- **Queue Pattern:** Request path enqueues work only; heavy embedding tasks run in background worker scripts.

## 6. Important Constraints

- **Vector Dimension:** Must use 4096 dimensions for production embeddings (matching `Qwen/Qwen3-VL-Embedding-8B`).
- **AI Response Format:** Always return a raw JSON string from the LLM, following the schema defined in `SYSTEM_PROMPT`.
- **Seeding Idempotency:** Always check for existing fonts by name before running AI enrichment or embedding generation to save API costs.
- **Font Availability:** Never display a font card if it both fails to render AND lacks a download link.
- **Link Validation:** Use `HEAD` requests to validate font file URLs during seeding.
- **JIT Request Path:** Must remain non-blocking; queue seeding jobs instead of embedding inline in API responses.
- **Font Hosting:** Continue external font hosting (Google/Fontsource/Fontshare). Do not self-host binary font files by default.
- **Worker Reliability:** Use retry policy and max attempts for failed queue jobs; log `last_error` for triage.
- **API Keys / Env:** Requires `GEMINI_API_KEY`, `NEXT_PUBLIC_SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY`; plus embedding/queue config such as `VL_EMBEDDING_ENDPOINT`, `VL_EMBEDDING_API_KEY`, and queue controls.
- **LLM Provider Policy:** ALWAYS use `GEMINI_API_KEY` and the gemini provider for all gemini models. NEVER use OpenRouter for Gemini. Use OpenRouter (`OPENROUTER_API_KEY`) for all other models.
- **Offline A/B Eval Env (Python harness):**
  - Variant A (text) requires `OPENROUTER_API_KEY` (typically from `.env.local`).
  - Local VL eval scripts (`research/ab-eval/py/*`) do **not** require `VL_EMBEDDING_ENDPOINT` / `VL_EMBEDDING_API_KEY`.
  - Set `HF_TOKEN` or `HUGGINGFACE_HUB_TOKEN` when model pull/auth issues occur.

## 7. Frontend Error Handling

- **Rendering Check:** Use `document.fonts.load()` to verify font renderability.
- **Toggles:** Provide subtle UI toggles (disabled by default) to "Include rendering issues" and "Include missing downloads."
- **Logging:** Console log hidden fonts (double-failure) with `%c` styling for visibility during debugging.

## 8. Development Environment

- **Start Command:** `npm run dev`
- **Build Command:** `npm run build`
- **Lint Command:** `npm run lint`
- **Environment Variables:** Use `.env.local` for local secrets.
- **Queue Worker Command:** `npx tsx scripts/worker-seed-jobs.ts`
- **Backfill Command:** `npx tsx scripts/backfill-b2-embeddings.ts`
- **Queue Health Command:** `npx tsx scripts/queue-health.ts`
- **Offline A/B Eval Interpreter (GPU):** use `\.venv-ab-eval\Scripts\python` for evaluation runs.
- **Complex Round Command (canonical):** `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_all.py --dataset complex --variant all`
- **OEM Adjudication UI Command:** `.\.venv-ab-eval\Scripts\python research/ab-eval/py/gen_oem_labeling_ui.py`
- **OEM Gate Runner Command:** `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_oem_gating.py`
- **GPU/Env readiness reference:** `research/ab-eval/READY_STATE_GPU_ENV_2026-02-07.md`

## 8. API Conventions

- **Search API:** `POST /api/search`
  - Body: `{ message: string, history: ChatMessage[] }`
  - Response: JSON containing a short reply and a list of font objects.
- **Response Shape:**
  ```json
  {
    "reply": "string",
    "fonts": [
      {
        "name": "Font Name",
        "desc": "Description",
        "category": "serif|sans-serif|...",
        "tags": ["tag1"],
        "source": "Google Fonts|...",
        "files": { "400": "url" }
      }
    ]
  }
  ```

## 9. Testing & Validation Guidelines

- No formal test suite established yet; verify API and UI manually.
- **Evaluation Governance (Canonical):** follow `research/ab-eval/EVALUATION_CONTRACT.md` for all offline A/B promotion decisions.
- **Offline A/B canonical artifacts:**
  - Primary baseline: `research/ab-eval/out/report_medium_human_v1.json`
  - Secondary baseline (Complex v1): `research/ab-eval/out/report_all.json`
- **Amended Human SSoT (current eval source):** `research/ab-eval/out/full_set_review_export_1770612809775.json`
- **Partial artifact caveat:** `report_complex.*` may exist as interrupted/stale outputs; do not use as final decision inputs unless explicitly designated as canonical for a run.
- **Visual Spot-Check**: After benchmarks/AB tests, generate a compact HTML grid (see `research/ab-eval/out/visual-spot-check.html`).
  - Use `@font-face` to load CDN binaries and render "Abg" or "Sphinx" glyphs.
  - Prioritize extreme vertical density for rapid human review of retrieval variants.
- **Visual Test Artifacts (Human Review)**: Intern reviewers validate visual outputs from grids, screenshots, or HTML artifacts. Add concise review/validation instructions directly inside the HTML artifact guide so anyone can follow it without external docs.

### 9.1 Promotion Gates (Required)

- Promotion decisions must pass all gates from `research/ab-eval/EVALUATION_CONTRACT.md`:
  - **G1 Agreement Delta:** `>= +1.0%`
  - **G2 Precision Regression:** `<= -2.0%`
  - **G3 Helps/Hurts Net:** `> 0`
  - **G4 Visual QA:** zero clipping/overlap on required specimen checks.
- **Non-binary label policy:** eval label `2` must be remapped to `0` for primary promotion metrics.
- **Tie-break order:** Agreement -> Recall@10 -> Precision@10 -> MRR@10.

### 9.2 Reproducibility & Quota Standards (Required)

- Follow `research/ab-eval/REPRODUCIBILITY.md` for all eval runs.
- **Default seed:** `42`
- **Repeat policy:**
  - `repeats=1` for standard deterministic retrieval runs.
  - `repeats=3` for new model/prompt probes.
- **Quota strategy:** use retry/backoff + resumable runs; for long Gemini runs, apply documented key-rotation workflow.
- **Artifact naming contract:**
  - `week1_` = prompt/model probes
  - `week2_` = specimen/visual changes
  - `week3_` = calibration/fusion/tuning

### 9.3 Specimen Renderer Regression Safeguard

- Any change to specimen rendering requires manual visual QA before promotion.
- Required regression files to inspect (latest regenerated versions):
  - `research/ab-eval/out/specimens_v3_1/Red_Hat_Mono_top.png`
  - `research/ab-eval/out/specimens_v3_1/Red_Hat_Mono_bottom.png`
  - `research/ab-eval/out/specimens_v3_1/Playwrite_BE_WAL_Guides_top.png`
  - `research/ab-eval/out/specimens_v3_1/Playwrite_BE_WAL_Guides_bottom.png`
- Also inspect at least 8 additional edge-case font families and report explicit pass/fail findings.

### 9.4 Current Week 4 Governance Snapshot (Onboarding/Frequent Reference)

- **Current champion remains:** `v3`.
- **`v5_1` status:**
  - OEM slice (`week4_p2`) produced a **targeted GO**.
  - Full-set validation (`week4_p3`) produced **NO-GO** due to G1 shortfall (`+0.40%`, threshold `>= +1.0%`).
- **Promotion rule clarification:** OEM-slice wins are valid directional signals, but are **not sufficient alone** for production-default promotion.
- **Latest prompt-line decision:** Pause `v5_x` single-variable prompt iteration unless a dominant (>50%) actionable failure motif emerges.
- **Primary Week 4 references:**
  - `research/ab-eval/REPORT_WEEK4_P2_OEM_GATING.md`
  - `research/ab-eval/REPORT_WEEK4_P3_V5_1_FULLSET.md`
  - `research/ab-eval/REPORT_WEEK4_P3_HURTS_ROOTCAUSE.md`
  - `.lightspec/decisions/DEC-20260213-02-v5-1-oem-slice-go-fullset-no-go.md`

## 10. General Dos and Don'ts

- **DO:** Co-locate component-specific logic where possible.
- **DO:** Use `supabase.rpc` for vector-based queries.
- **DO:** Ensure all environment variables are present before calling AI/DB services.
- **DO:** Keep B2 as production default retrieval path; keep text embedding as fallback path only.
- **DO:** Keep JIT seeding asynchronous through queue and worker processing.
- **DO:** Update LightSpec SSoT docs when architecture/process changes (`.lightspec/`).
- **DON'T:** Commit `.env.local` or other sensitive keys.
- **DON'T:** Use markdown blocks in AI-generated JSON responses; keep it raw for parsing.
- **DON'T:** Block user search requests on embedding generation or enrichment tasks.
- **DON'T:** Assume a local dev GPU machine is a 24/7 production dependency.

## 11. LightSpec Source of Truth (SSoT)

- **Core capability spec:** `.lightspec/font-search-rag.md`
- **Usage rule:** For new features or significant changes, define/update requirements in `.lightspec/*.md` before implementation and record major decisions as ADRs in `.lightspec/decisions/`.
- **Legacy Migration:** All active decisions and specs previously in `research/prod-rollout/` and `research/ab-eval/` have been migrated to `.lightspec/`.

## 12. Core Decisions to Preserve (SSoT: .lightspec/decisions/)

- **Production Default:** B2 (`Qwen/Qwen3-VL-Embedding-8B`) with 4096-dimensional vectors. See [DEC-20260206-01-production-b2-migration.md](.lightspec/decisions/DEC-20260206-01-production-b2-migration.md).
- **JIT Seeding:** Queue-based and non-blocking.
- **Retrieval Path:** Semantic cache -> Vector Search -> LLM.
- **Evaluation:** B2 significantly outperforms text-only baseline (Variant A). See [DEC-20260207-01-complex-eval-b2-promotion.md](.lightspec/decisions/DEC-20260207-01-complex-eval-b2-promotion.md).
- **Research Gate:** Quality-first experiment sequence (specimen v2, schema v2) is required before further production default changes. See [DEC-20260208-03-quality-first-experiment-plan.md](.lightspec/decisions/DEC-20260208-03-quality-first-experiment-plan.md).
- **Evaluation Governance Lock:** Canonical contract/gates/reproducibility are mandatory for promotion decisions. See [DEC-20260211-01-evaluation-governance-lock.md](.lightspec/decisions/DEC-20260211-01-evaluation-governance-lock.md).
- **Specimen/Prompt governance path:** Specimen V3.1 + Prompt V3 were validated in the quality optimization cycle; follow contract gates for any replacement.
- **Week 4 Prompt-Line Decision:** `v5_1` is **not promotion-ready** globally despite OEM-slice GO; keep `v3` champion and pause prompt-only `v5_x` iterations pending stronger motif concentration. See [DEC-20260213-02-v5-1-oem-slice-go-fullset-no-go.md](.lightspec/decisions/DEC-20260213-02-v5-1-oem-slice-go-fullset-no-go.md).
