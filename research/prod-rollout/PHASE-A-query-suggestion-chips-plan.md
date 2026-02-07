# Phase A Plan — Query Suggestion Chips (AI Assist Value Add)

## Goal

Add a lightweight, high-utility enhancement to AI Assist: each AI response should include clickable “next query” suggestions that users can run immediately in Style Match.

This increases practical value without introducing major complexity or a disruptive UI pattern.

## Scope (Phase A only)

- Extend AI response schema to optionally include `suggestedQueries`.
- Render suggestion chips in the existing results flow.
- Clicking a chip submits a new search query directly.
- Keep current response contract backward-compatible.
- Do **not** implement multi-query fan-out, advanced iterative actions, or pairing intelligence in this phase.

## Non-Goals

- No separate page/tab for AI.
- No additional retrieval index changes.
- No paywall implementation changes in this phase.
- No new model providers.

## Current Baseline (for context)

- Search API currently returns `reply` + `fonts` from [`POST /api/search`](../../src/app/api/search/route.ts).
- UI chat/search flow is orchestrated from [`FontExplorer`](../../src/components/FontExplorer.tsx).
- Existing AI response shape is typed in [`SearchResponse`](../../src/lib/types.ts).

## Proposed API Schema Update (Backward-Compatible)

Add optional field to response payload:

```ts
interface SearchResponse {
  reply: string;
  fonts: Font[];
  suggestedQueries?: string[]; // optional, 0..6
}
```

Guidelines for `suggestedQueries`:

- 3 to 6 chips preferred.
- Max 60 chars each.
- Must be concrete, user-runnable style prompts.
- Must avoid duplicates and near-duplicates.
- Should include diversity bands:
  - 1 strict refinement
  - 1 adjacent variation
  - 1 exploratory contrast

## Prompt/Generation Contract

Update system instruction used by search API so AI returns:

- `reply`
- `fonts`
- `suggestedQueries` (optional but expected)

Quality constraints for query suggestions:

- Avoid generic noise (“more fonts”, “best fonts”).
- Include clear stylistic intent (“more geometric sans with neutral tone”).
- Keep phrasing plain-English for non-technical users.
- Keep safe and policy-compliant.

## UI/UX Plan

Placement:

- Show chips directly beneath AI status/reply area in the existing single-container flow.
- Label section as: **Try refining your search**.

Behavior:

- Chip click triggers same send flow as manual input.
- Add chip text to history as user message for continuity.
- Keep chips collapsible if more than 4 (show 4 + “more”).

Visual design:

- Small rounded neutral chips with subtle hover and selected states.
- Keep style aligned with existing control density.
- Avoid bright “AI” badges; prioritize approachability.

Accessibility:

- Keyboard-focusable chips.
- `aria-label` includes full suggested text.
- Preserve Enter behavior in existing input.

## Analytics / Instrumentation

Track these events:

- `suggested_query_shown` (count + query/session id)
- `suggested_query_clicked` (which index/text)
- `suggested_query_clickthrough_rate`
- downstream conversion signals:
  - additional searches per session
  - save/favorite actions
  - premium CTA clicks (if present)

## Rollout Strategy

1. Ship behind feature flag: `FEATURE_QUERY_SUGGESTION_CHIPS`.
2. Internal dogfood with flag ON.
3. 10% rollout to users.
4. Full rollout if success criteria met.

## Success Criteria

- +15% or better increase in second-query rate per session.
- +10% or better increase in session depth (queries/session).
- No significant latency regression in API path.
- No increase in parse failures from model response schema.

## Risks and Mitigations

- **Risk:** Suggestions are repetitive or low quality.
  - **Mitigation:** Diversity constraints + de-dup post-processing.

- **Risk:** Response schema parse errors increase.
  - **Mitigation:** Optional field + tolerant parser + fallback to empty array.

- **Risk:** UI clutter.
  - **Mitigation:** max visible chips + compact style + optional collapse.

## Implementation Work Breakdown (Phase A)

- API / prompt
  - Extend response schema contract and parser.
  - Add suggestion quality guardrails and sanitization.

- Types
  - Add optional `suggestedQueries` in shared type.

- UI
  - Add chip container component in chat/search area.
  - Wire click action to existing send handler.

- Observability
  - Add analytics hooks for impressions/clicks.

- QA
  - Manual test matrix: no suggestions, 1 suggestion, 6 suggestions, duplicates, long text.

## Brief References for Later Phases

- **Phase B (Guided Iteration Actions):** one-click transforms like “more geometric”, “less playful”, “higher readability”.
- **Phase C (Parallel Multi-RAG Fan-out):** bounded 2–3 query expansions, merged for diversity/coverage.
- **Phase D (Pairing Intelligence):** heading/body pair recommendations with rationale and usage context.

These are intentionally deferred; Phase A should stay small and shippable.

## Definition of Done (Phase A)

- API can return optional `suggestedQueries` without breaking old clients.
- UI displays chips when present and gracefully hides when absent.
- Chip click executes a new search with no special-case errors.
- Feature flag allows safe rollback.
- Basic metrics are visible for adoption and CTR.
