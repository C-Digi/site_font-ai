# Project Coding Rules & Guidelines for AI Assistant (GEMINI.md)

## 1. Project Overview

- **Project Name:** `site_font-ai` (AI Font Explorer)
- **Description:** An AI-powered font discovery tool that uses semantic search and RAG to recommend fonts based on user descriptions.
- **Primary Goal:** Provide a seamless, intelligent interface for finding fonts that match specific moods, use cases, or styles.

## 2. Technology Stack

- **Language:** `TypeScript 5.7.3`
- **Framework:** `Next.js 15.1.6` (App Router)
- **UI Library:** `React 19`, `Tailwind CSS 4`, `Lucide React`
- **State Management:** React state, `next-themes` for theme management.
- **Database/Vector:** `Supabase` (with `pgvector`)
- **AI/LLM:** `Gemini 2.0 Flash Lite` (via `@google/generative-ai`)
- **Embeddings:** `OpenRouter` (`qwen/qwen3-embedding-8b`, 4096 dimensions)
- **Package Manager:** `npm`

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
  1. **Query Embedding:** Generate vector for user input using OpenRouter.
  2. **Semantic Cache:** Check `searches` table for high-similarity hits (threshold > 0.95).
  3. **Vector Search:** Query `fonts` table using `match_fonts` RPC (threshold > 0.5).
  4. **LLM Generation:** Send query + retrieved font context to Gemini with a strict JSON system prompt.
  5. **JIT Seeding:** If Gemini suggests fonts not in DB, seed them asynchronously.
  6. **Caching:** Save the final response in the `searches` table.
- **Database Interactions:** Use `supabase.rpc` for vector similarity searches.
- **Server-Side API:** API routes in `src/app/api` handle the heavy lifting (AI, DB).

## 6. Important Constraints

- **Vector Dimension:** Must use 4096 dimensions for embeddings (matching `qwen/qwen3-embedding-8b`).
- **AI Response Format:** Always return a raw JSON string from the LLM, following the schema defined in `SYSTEM_PROMPT`.
- **API Keys:** Requires `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `NEXT_PUBLIC_SUPABASE_URL`, and `SUPABASE_SERVICE_ROLE_KEY`.

## 7. Development Environment

- **Start Command:** `npm run dev`
- **Build Command:** `npm run build`
- **Lint Command:** `npm run lint`
- **Environment Variables:** Use `.env.local` for local secrets.

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

## 9. Testing Guidelines

- No formal test suite established yet. Standard practice should be to verify API responses and UI components manually during development.

## 10. General Dos and Don'ts

- **DO:** Co-locate component-specific logic where possible.
- **DO:** Use `supabase.rpc` for vector-based queries.
- **DO:** Ensure all environment variables are present before calling AI/DB services.
- **DON'T:** Commit `.env.local` or other sensitive keys.
- **DON'T:** Use markdown blocks in AI-generated JSON responses; keep it raw for parsing.

