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
- **Offline A/B canonical artifacts:** prefer `research/ab-eval/out/report_all.md` + `research/ab-eval/out/report_all.json` as source-of-truth for completed runs.
- **Partial artifact caveat:** `report_complex.*` may exist as interrupted/stale outputs; do not use as final decision inputs unless explicitly designated as canonical for a run.
- **Visual Spot-Check**: After benchmarks/AB tests, generate a compact HTML grid (see `research/ab-eval/out/visual-spot-check.html`).
  - Use `@font-face` to load CDN binaries and render "Abg" or "Sphinx" glyphs.
  - Prioritize extreme vertical density for rapid human review of retrieval variants.
- **Visual Test Artifacts (Human Review)**: Intern reviewers validate visual outputs from grids, screenshots, or HTML artifacts. Add concise review/validation instructions directly inside the HTML artifact guide so anyone can follow it without external docs.

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

- **Canonical spec root:** `.lightspec/`
- **Core capability spec:** `.lightspec/font-search-rag.md`
- **Decision records:** `.lightspec/decisions/`
- **Usage rule:** For new features or significant changes, define/update requirements in `.lightspec/*.md` before implementation and record major decisions as ADRs in `.lightspec/decisions/`.
- **Legacy Migration:** All active decisions and specs previously in `research/prod-rollout/` and `research/ab-eval/` have been migrated to `.lightspec/`.

## 12. Core Decisions to Preserve (SSoT: .lightspec/decisions/)

- **Production Default:** B2 (`Qwen/Qwen3-VL-Embedding-8B`) with 4096-dimensional vectors. See [DEC-20260206-01-production-b2-migration.md](.lightspec/decisions/DEC-20260206-01-production-b2-migration.md).
- **JIT Seeding:** Queue-based and non-blocking.
- **Retrieval Path:** Semantic cache -> Vector Search -> LLM.
- **Evaluation:** B2 significantly outperforms text-only baseline (Variant A). See [DEC-20260207-01-complex-eval-b2-promotion.md](.lightspec/decisions/DEC-20260207-01-complex-eval-b2-promotion.md).
- **Research Gate:** Quality-first experiment sequence (specimen v2, schema v2) is required before further production default changes. See [DEC-20260208-03-quality-first-experiment-plan.md](.lightspec/decisions/DEC-20260208-03-quality-first-experiment-plan.md).
