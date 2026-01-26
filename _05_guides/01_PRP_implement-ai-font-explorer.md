# Implementation Plan: AI Font Explorer with RAG & Monetization

## Overview
A monetized, AI-powered font discovery tool using Next.js, Supabase Vector, and Gemini 2.5. It features RAG caching for performance, a tiered credit system via Lemon Squeezy, and a generous free tier enforced by FingerprintJS.

## Requirements Summary
- AI Search: Natural language font discovery using Gemini 2.5 Flash Lite.
- RAG Caching: Semantic caching with OpenRouter qwen3-embedding-8b and Supabase Vector.
- Monetization: Credit bundles (Lemon Squeezy) and Donations (BuyMeACoffee).
- Usage Limits: 5/day (Guests), tracked via FingerprintJS & IP.
- Filtering: Independent filters for License (OFL), Category, and Price.

## Research Findings
### Best Practices
- Vector Search: Use vector extension in Postgres; dimensions must match model (4096 or 1024 for Qwen).
- Rate Limiting: Validate FingerprintJS requestId server-side to prevent spoofing.
- Font Data: Cache Google Fonts list server-side; don't fetch from API on every request.

### Technology Decisions
- Next.js App Router: For robust API routes and server components.
- Supabase: Unified Auth, Database, and Vector store.
- Lemon Squeezy: Simplifies tax/MoR for credit packs.
- Gemini 2.5 Flash Lite: Cost-effective, high-speed generation.

## Implementation Tasks

### Phase 1: Foundation & Data
1. Project Setup
   - Description: Initialize Next.js project with Tailwind CSS and Supabase client.
   - Files: package.json, .env.local, lib/supabase/client.ts
   - Dependencies: next, tailwindcss, @supabase/supabase-js
   - Effort: 2 hours

2. Database Schema & Vector Setup
   - Description: Enable vector extension, create fonts table with embedding column, and users table for credits.
   - Files: supabase/migrations/001_init.sql
   - Dependencies: pgvector
   - Effort: 3 hours

3. Font Data Ingestion Script
   - Description: Script to fetch Google Fonts, generate embeddings via OpenRouter, and seed Supabase.
   - Files: scripts/seed-fonts.ts
   - Dependencies: node-fetch, openai (for OpenRouter client)
   - Effort: 4 hours

### Phase 2: Core Logic (AI & RAG)
4. RAG Service Implementation
   - Description: Service to generate query embedding, search Supabase Vector, and determine cache hit/miss.
   - Files: lib/ai/rag.ts, lib/ai/embeddings.ts
   - Effort: 5 hours

5. Gemini Integration
   - Description: Fallback generation using Gemini 2.5 Flash Lite with structured JSON output.
   - Files: lib/ai/gemini.ts
   - Dependencies: @google/generative-ai
   - Effort: 3 hours

6. Search API Route
   - Description: POST /api/search handling RAG check -> Gemini fallback -> Result return.
   - Files: app/api/search/route.ts
   - Effort: 3 hours

### Phase 3: Monetization & Limits
7. Guest Rate Limiting
   - Description: Middleware using FingerprintJS to track guest usage (5/day).
   - Files: middleware.ts, lib/rate-limit.ts
   - Dependencies: @fingerprintjs/fingerprintjs-pro-server-api
   - Effort: 4 hours

8. Credit System & Webhooks
   - Description: Lemon Squeezy webhook handler to top up user credits upon purchase.
   - Files: app/api/webhooks/lemon-squeezy/route.ts
   - Effort: 4 hours

### Phase 4: UI/UX
9. Chat Interface & Font Grid
   - Description: Interactive chat component and responsive font grid with "Load More".
   - Files: components/Chat.tsx, components/FontGrid.tsx
   - Effort: 6 hours

10. Independent Filters
    - Description: Client-side filtering for License, Category, and Price.
    - Files: components/Filters.tsx
    - Effort: 3 hours

## Codebase Integration Points
### New Files to Create
- lib/ai/rag.ts - Core RAG logic
- app/api/search/route.ts - Main entry point for search
- supabase/migrations/001_init.sql - Database schema

## Success Criteria
- [ ] Search queries reuse cached results when semantic similarity > 0.85.
- [ ] Guests are blocked after 5 searches/day.
- [ ] Purchasing a credit pack via Lemon Squeezy correctly updates the user's balance.
- [ ] UI shows relevant fonts with accurate previews.

## Notes
- Cache Strategy: Semantic cache should expire or be re-validated if font data updates significantly (rare for Google Fonts).
- Security: Ensure Lemon Squeezy secret is secure and signature is verified.