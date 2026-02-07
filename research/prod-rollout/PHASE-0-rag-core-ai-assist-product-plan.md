# Phase 0 Plan — RAG-First Product Direction (Optional AI Assist)

## Starting Point

This plan starts from your prompt:

- “since we have a semantic RAG db, could we potentially remove the AI chat interface ...”

It consolidates what we covered and decided across product direction, retrieval architecture, AI Assist scope, and rollout sequence.

## Approach

- Make **semantic retrieval the primary UX path**.
- Keep **AI Assist optional/on-demand** as a premium refinement layer.
- Preserve a **single-container, low-clutter UI** with one prominent search bar.
- Continue B2 retrieval migration as the quality foundation.

## Context Gathered

- B2 rollout SSoT exists in [`research/prod-rollout/README.md`](research/prod-rollout/README.md).
- Current search flow combines retrieval + LLM in [`POST /api/search`](../../src/app/api/search/route.ts:40).
- Current embedding + fallback path is in [`generateEmbedding()`](../../src/lib/ai/embeddings.ts:1).
- Suggestion chips plan exists in [`research/prod-rollout/PHASE-A-query-suggestion-chips-plan.md`](research/prod-rollout/PHASE-A-query-suggestion-chips-plan.md).
- Core migration decisions are in [`research/prod-rollout/DECISIONS.md`](research/prod-rollout/DECISIONS.md).

## Decisions Captured (So Far)

- Product modes remain:
  - Fast Search
  - Style Match
  - AI Assist
- AI is **not mandatory** for initial results.
- AI Assist is **value-add guidance**, not the default funnel.
- Keep UI calm; avoid busy continuous motion under input.
- Inspiration pattern: compact static chips + optional “More ideas” panel.
- Premium direction: show limited high-value previews and gate deeper guided outputs.
- Continue B2 retrieval as technical default direction.

## Alternatives Considered

### A) AI-first mandatory chat

- **Pros:** rich conversational guidance.
- **Cons:** slower path, higher cost, overlap with retrieval results.
- **Rejected Because:** conflicts with fast discovery goal.

### B) Retrieval-only (no AI Assist)

- **Pros:** simplest architecture and lowest cost.
- **Cons:** weaker refinement flow and monetization differentiation.
- **Rejected Because:** removes advanced value users asked for.

### C) RAG-first + optional AI Assist (**Selected**)

- **Pros:** fast default, premium depth when needed, better clarity.
- **Cons:** requires careful UX to avoid duplicate-feeling outputs.
- **Selected Because:** best balance of UX, cost, and monetization.

## Implementation Plan

### Step 1: Lock Product Contract (Modes + Entitlements)

- Define exact behavior for each mode and free/pro limits.
- Define when AI Assist appears and what unique value it adds.
- Define policy for 1–2 premium previews (best-fit + diverse alternative).

- **Verification:** matrix added to [`tasks-user.md`](../../tasks-user.md).
- **Dependencies:** none.

### Step 2: Finalize Single-Container UX Blueprint

- Keep one prominent input.
- Add compact inspiration chips (no ticker/marquee).
- Add optional “More ideas” popover with categories.
- Keep AI Assist as lightweight inline panel/drawer on demand.

- **Verification:** UX section approved in this doc + linked from [`research/prod-rollout/README.md`](research/prod-rollout/README.md).
- **Dependencies:** Step 1.

### Step 3: Define AI Assist Differentiation Rules

- AI Assist should add:
  - rationale/explanations,
  - targeted refinements,
  - next-query suggestions.
- Continue Phase A suggestion chips plan in [`research/prod-rollout/PHASE-A-query-suggestion-chips-plan.md`](research/prod-rollout/PHASE-A-query-suggestion-chips-plan.md).
- Keep overlap explicit: AI grounds on retrieved context in [`route.ts`](../../src/app/api/search/route.ts).

- **Verification:** contract documented with edge-case examples.
- **Dependencies:** Steps 1–2.

### Step 4: Align Technical Rollout With Product Direction

- Keep B2 migration cutover gates from [`research/prod-rollout/RUNBOOK.md`](research/prod-rollout/RUNBOOK.md).
- Keep queue-based non-blocking JIT seeding.
- Preserve fallback path until quality gates are met.

- **Verification:** rollout checklist remains green and gated in [`research/prod-rollout/PROGRESS.md`](research/prod-rollout/PROGRESS.md).
- **Dependencies:** Step 3.

### Step 5: Define Measurement + A/B Plan (Product + AI)

- Core metrics:
  - search-to-click rate,
  - second-query/session depth,
  - favorite/save rate,
  - download intent,
  - AI Assist invocation + suggestion-chip CTR,
  - latency and cost per request.
- Include complex-query evaluation set continuation from [`research/ab-eval/DECISIONS.md`](../ab-eval/DECISIONS.md).

- **Verification:** metric definitions and event names documented before implementation.
- **Dependencies:** Steps 1–4.

### Step 6: Add Foundational Platform Streams (High-Level)

- **Payments (high-level):**
  - Select billing provider and subscription model for Free vs Pro.
  - Define entitlement mapping to product limits (Style Match limits, AI Assist limits, favorites/collections caps).
  - Add lifecycle events plan: trial/activation/cancel/failed payment/grace period.

- **User Auth (high-level):**
  - Select auth approach (email/social/magic link) aligned with Supabase + Next.js architecture.
  - Define guest-to-account upgrade path to preserve favorites/history.
  - Define account security baseline (session handling, reset flow, abuse/rate-limit policy).

- **Other Core Features (high-level):**
  - Favorites persistence and sync strategy (guest local persistence + signed-in cloud sync).
  - Collections (create/share/export-import) rollout sequence.
  - Analytics baseline for funnel + monetization events.
  - Admin/operator basics (feature flags, quota controls, health dashboards).

- **Verification:** approved platform roadmap added as a short follow-on phase in [`tasks-user.md`](../../tasks-user.md).
- **Dependencies:** Steps 1–5.

## Validation Strategy

- Product validation:
  - user can complete discovery without AI in primary flow,
  - AI Assist visibly improves refinement when invoked.
- Technical validation:
  - B2 quality gates (Recall@10 target and queue health) remain satisfied.
- UX validation:
  - no clutter regression from inspiration module,
  - no major latency/regression in search path.

## Open Questions (To Resolve Before Build)

- Exact free/pro limits for Style Match and AI Assist rate caps.
- Final premium lock behavior (how many previews, when to prompt upgrade).
- Whether “Fast Search” and “Style Match” are separate surfaces or one adaptive surface.
- Which analytics provider/event schema is source of truth for monetization experiments.
