# Human-Reviewed Labeling Workflow (Medium Query Set, v1)

## Scope and Goal

This document defines an implementation-ready workflow for collecting fast, visual human relevance judgments and converting them into a new canonical offline-eval label set:

- `research/ab-eval/data/labels.medium.human.v1.json` (scoring-compatible canonical output)
- with migration path toward `research/ab-eval/data/labels.complex.v2.human-reviewed.json`.

This is a process/spec package only. It does not implement UI or scripts.

---

## Approach

Selected approach: **blind-first visual relevance labeling with binary 0/1 judgments, then deterministic aggregation + adjudication**.

Why this approach:

- High reviewer throughput from simple per-card actions.
- Lower anchoring risk via blinding and randomized candidate ordering.
- Fast, unambiguous signal for retrieval relevance.
- Compatible with current scoring scripts via deterministic binary export.

---

## Context Gathered

- `labels.complex.v1.json` is currently treated as scoring SSoT but is explicitly marked provisional until human review in `research/ab-eval/DECISIONS.md`.
- Existing scripts (`research/ab-eval/py/score_all_variants.py`, `research/ab-eval/py/score_retrieval.py`) load label JSON as `query_id -> [font_name]`.
- Existing human review packet (`research/ab-eval/human_review_packet_v1.md`) validates model descriptions, not retrieval relevance labels.
- Team constraint: limited reviewer time; need practical medium-complexity query set before redoing full complex labels.

---

## Target Deliverables (Data + Docs)

### Canonical data outputs

- `research/ab-eval/data/queries.medium.human.v1.json`
- `research/ab-eval/data/human/raw/judgments.medium.human.v1.jsonl`
- `research/ab-eval/data/human/raw/sessions.medium.human.v1.jsonl`
- `research/ab-eval/data/human/adjudication.medium.human.v1.json`
- `research/ab-eval/data/labels.medium.human.v1.json` (canonical scorer input)
- `research/ab-eval/data/labels.medium.human.v1.meta.json` (provenance + quality report)

### Planned future output

- `research/ab-eval/data/labels.complex.v2.human-reviewed.json`

---

## 1) Interactive Labeling Method

## Reviewer UX flow (screen-level)

### Screen A — Session setup

- Reviewer picks identity (`reviewer_id`) and session length target (20/30/45 minutes).
- Tool loads assigned query block and unfinished work.
- Tool shows quick tutorial: rubric + keyboard cheatsheet.

### Screen B — Query workspace (primary screen)

Layout:

- Left panel:
  - query text
  - query class
  - optional plain-language hints (non-expert friendly)
  - progress meter (e.g., 12/20 candidates labeled)
- Main grid:
  - candidate glyph cards (anonymous code by default, no rank/source shown)
  - each card supports quick relevance mark: 0 or 1
- Right panel:
  - filters: unlabeled / labeled / only disagreements (in adjudication mode)
  - per-query notes
  - autosave status

### Screen C — Query finalize

- Reviewer sees:
  - count of 0/1 labels
  - optional “Top picks” (up to 3 cards) for tie-breaking signal
  - confidence for the query (low/medium/high)
- Reviewer submits query and moves to next.

### Screen D — Resume / completion

- Resume from last unlabeled candidate.
- Export session checkpoint JSONL.
- End-of-session fatigue self-check (optional): “fresh / okay / fatigued”.

## High-throughput controls

### Keyboard shortcuts

- `0`, `1`: set relevance on focused card
- `J` / `K`: next/previous card
- `N` / `P`: next/previous query
- `S`: force save checkpoint
- `U`: undo last label action
- `F`: toggle unlabeled-only filter
- `T`: mark/unmark top-pick star (max 3)

### Batch actions

- Multi-select cards then apply a shared label.
- “Mark remaining as 0” confirmation action for low-fit tails.

### Progressive saving and resume

- Autosave every 15 interactions and on every query transition.
- Durable local checkpoint file + append-only session log.
- Resume logic uses latest timestamped checkpoint per reviewer.

### Fatigue reduction

- Hard cap 8–10 queries per sitting (default 6).
- Micro-break prompt every ~7 minutes or every 2 queries.
- Balanced query order to avoid class clustering.
- Timebox target per query: 90–150 seconds.

## Relevance rubric (non-expert friendly)

Primary per-card score:

- `2` = strong fit (would confidently recommend)
- `1` = partial fit (some traits match)
- `0` = not a fit

Per-query final signal:

- optional top-pick stars (up to 3)
- confidence: `low|medium|high`

Rubric simplification rules:

- Judge by visible glyph behavior first.
- Ignore personal taste; focus on query match.
- If unsure, use `1` not forced extremes.

---

## 2) Anti-Bias Strategy

## Anchoring controls

- **Blind-first UI:** no display of legacy labels, model ranks, retrieval variant name, or previous reviewer choices.
- **Anonymous card IDs** in first pass (font names hidden until adjudication).
- **No “correct answer” feedback** during labeling.

## Candidate ordering controls

- Per-reviewer deterministic randomization using `seed = hash(query_id + reviewer_id + workflow_version)`.
- Within-query shuffle preserves hidden strata quotas but randomizes presentation order.
- Different reviewer seeds prevent shared order effects.

## Constrained use of prior labels (`labels.complex.v1.json`)

Allowed:

- use as one hidden source for candidate pool seeding
- capped contribution (max 15% of shown cards per query)

Not allowed:

- showing prior labels in reviewer UI
- using prior labels as tie-break truth during adjudication
- auto-promoting prior-labeled fonts without fresh human judgment

---

## 3) Query Strategy (Medium Complexity)

## Recommended query count

- **Target:** 20 queries
- **Allowed range:** 16–24

Justification:

- 20 queries gives balanced coverage across four classes while fitting a small-team review window.
- With 18 candidates/query and 2 reviewers: 720 core judgments; high signal density with manageable effort.

## Query class allocation

- 5 × `visual_shape`
- 5 × `semantic_mood`
- 5 × `historical_context` (simplified phrasing)
- 5 × `functional_pair`

## Authoring rules

- one primary intent + at most one secondary constraint
- avoid typography jargon that requires expertise
- prefer plain language and concrete outcomes
- avoid named fonts/foundries in query text
- avoid negation-heavy phrasing
- keep text concise (roughly 8–16 words)

## Sample medium query slate (proposed)

```json
[
  { "id": "mq_001", "text": "clean geometric sans for product UI", "class": "visual_shape" },
  { "id": "mq_002", "text": "friendly rounded sans for kids app headings", "class": "visual_shape" },
  { "id": "mq_003", "text": "narrow sans for tight dashboard labels", "class": "visual_shape" },
  { "id": "mq_004", "text": "high-contrast serif for elegant headlines", "class": "visual_shape" },
  { "id": "mq_005", "text": "readable monospace with clear zero and letter O", "class": "visual_shape" },

  { "id": "mq_006", "text": "warm handwritten feel for personal notes", "class": "semantic_mood" },
  { "id": "mq_007", "text": "serious professional look for legal content", "class": "semantic_mood" },
  { "id": "mq_008", "text": "playful display style for party invitations", "class": "semantic_mood" },
  { "id": "mq_009", "text": "modern minimal tone for startup branding", "class": "semantic_mood" },
  { "id": "mq_010", "text": "rugged bold style for outdoor gear", "class": "semantic_mood" },

  { "id": "mq_011", "text": "classic book-style serif for long reading", "class": "historical_context" },
  { "id": "mq_012", "text": "retro 8-bit style for old game screens", "class": "historical_context" },
  { "id": "mq_013", "text": "art-deco inspired display look", "class": "historical_context" },
  { "id": "mq_014", "text": "swiss-style neutral sans for signage", "class": "historical_context" },
  { "id": "mq_015", "text": "typewriter-like mono for archival vibe", "class": "historical_context" },

  { "id": "mq_016", "text": "headline font pairing with neutral sans body text", "class": "functional_pair" },
  { "id": "mq_017", "text": "legible serif for editorial paragraphs", "class": "functional_pair" },
  { "id": "mq_018", "text": "compact sans for dense data tables", "class": "functional_pair" },
  { "id": "mq_019", "text": "decorative title font for short book covers", "class": "functional_pair" },
  { "id": "mq_020", "text": "reliable UI sans for responsive admin panels", "class": "functional_pair" }
]
```

---

## 4) Candidate-Pool Strategy Per Query

## Candidate count envelope

- **Default shown per query:** 18
- **Minimum:** 14
- **Maximum:** 22

## Selection strategy (coverage + diversity + uncertainty)

For each query:

- Pull top candidates from retrieval variants (`A`, `B2`, `C`, `D`) using current corpus.
- Build hidden strata:
  - `consensus`: appears in top-10 of >=2 variants
  - `uncertain`: large rank disagreement or appears high in only one variant
  - `diversity`: category/style injectors to reduce tunnel vision
  - `legacy_seed` (optional): from `labels.complex.v1.json`, capped to 15%

Default 18-card composition:

- 8 consensus
- 5 uncertain
- 3 diversity injectors
- 2 legacy_seed or curator fallback

Rules:

- no duplicate font per query
- include at least 3 category buckets per query when corpus allows
- keep one reserved slot for “out-of-distribution” sanity sample on 25% of queries

---

## 5) Data Contract + Artifacts

## 5.1 Raw judgment schema (`judgments.medium.human.v1.jsonl`)

One JSON object per card action (append-only):

```json
{
  "workflow_version": "human-label-medium.v1",
  "session_id": "sess_2026-02-10_r1_01",
  "reviewer_id": "r1",
  "query_id": "mq_001",
  "candidate_font_id": "font_abc123",
  "candidate_font_name": "Albert Sans",
  "shown_position": 7,
  "score": 2,
  "is_top_pick": true,
  "query_confidence": "high",
  "timestamp_utc": "2026-02-10T19:12:33Z",
  "ui_mode": "blind_first",
  "random_seed": "7f3f...",
  "notes": "clean curves, works for UI"
}
```

Constraints:

- `score` in `{0,1,2}`
- latest action per `(reviewer_id, query_id, candidate_font_id)` is authoritative
- all writes are immutable append events; derived state is computed downstream

## 5.2 Session checkpoint schema (`sessions.medium.human.v1.jsonl`)

```json
{
  "workflow_version": "human-label-medium.v1",
  "session_id": "sess_2026-02-10_r1_01",
  "reviewer_id": "r1",
  "status": "in_progress",
  "queries_completed": ["mq_001", "mq_002"],
  "autosave_count": 14,
  "fatigue_flag": "okay",
  "started_at_utc": "2026-02-10T18:40:01Z",
  "updated_at_utc": "2026-02-10T19:14:08Z"
}
```

## 5.3 Adjudication schema (`adjudication.medium.human.v1.json`)

```json
{
  "workflow_version": "human-label-medium.v1",
  "query_id": "mq_001",
  "candidate_font_name": "Albert Sans",
  "aggregates": {
    "mean_score": 1.33,
    "reviewer_count": 3,
    "std_dev": 0.47,
    "top_pick_votes": 2
  },
  "adjudication_status": "accepted_auto",
  "final_relevant": true,
  "adjudicator_id": null,
  "reason": "mean>=1.25 and >=2 nonzero votes"
}
```

## 5.4 Final labelset schema (canonical scorer input)

`labels.medium.human.v1.json` must remain compatible with current scorers:

```json
{
  "mq_001": ["Albert Sans", "Inter", "DM Sans"],
  "mq_002": ["Nunito", "Quicksand"]
}
```

`labels.medium.human.v1.meta.json` carries provenance and quality metadata:

```json
{
  "labelset_id": "labels.medium.human.v1",
  "queryset_id": "queries.medium.human.v1",
  "corpus_id": "corpus.200",
  "workflow_version": "human-label-medium.v1",
  "generated_at_utc": "2026-02-11T02:30:00Z",
  "input_artifacts": {
    "raw_judgments": "research/ab-eval/data/human/raw/judgments.medium.human.v1.jsonl",
    "adjudication": "research/ab-eval/data/human/adjudication.medium.human.v1.json"
  },
  "quality": {
    "weighted_kappa_overall": 0.61,
    "conflict_rate": 0.18,
    "queries_with_min_relevants": 20
  },
  "promotion_status": "candidate"
}
```

## 5.5 Deterministic conversion rules

Conversion from raw judgments to canonical labels:

- Step A: collapse latest reviewer action per candidate.
- Step B: compute aggregates per `(query_id, font)`:
  - `mean_score`, `std_dev`, `nonzero_votes`, `top_pick_votes`
- Step C: auto decisions:
  - auto-accept if `mean_score >= 1.25` and `nonzero_votes >= 2`
  - auto-reject if `mean_score <= 0.50`
  - adjudicate otherwise
- Step D: adjudication for unresolved/conflicting items.
- Step E: final query-level bounds:
  - minimum 5 relevant fonts/query
  - maximum 12 relevant fonts/query
  - if >12, keep highest `mean_score`, then `top_pick_votes`, then lexical tie-break on font name
- Step F: emit `labels.medium.human.v1.json` sorted by query id.
- Step G: emit `labels.medium.human.v1.meta.json` with input hashes and gate metrics.

## 5.6 File naming/versioning conventions

- query sets: `queries.medium.human.v<major>.json`
- raw judgments: `judgments.medium.human.v<major>.jsonl`
- canonical labels: `labels.medium.human.v<major>.json`
- provenance: `labels.medium.human.v<major>.meta.json`
- future complex reviewed target: `labels.complex.v2.human-reviewed.json`

---

## 6) Quality Gates and Adjudication

## Inter-reviewer agreement plan

- Minimum two independent reviewers on all medium queries.
- Third reviewer audits 20% stratified sample.
- Report weighted Cohen’s kappa (0/1/2) overall and by class.

Target thresholds:

- overall weighted kappa >= 0.55
- per-class weighted kappa >= 0.45
- unresolved conflict rate <= 25% pre-adjudication

## Conflict resolution workflow

- Auto-accept/auto-reject by deterministic thresholds.
- Borderline set enters adjudication board:
  - one adjudicator + one observer
  - blind evidence first (glyph + query + score distributions)
  - final decision recorded with short reason code

Reason code taxonomy:

- `VISUAL_MATCH`
- `PARTIAL_MATCH`
- `QUERY_TOO_AMBIGUOUS`
- `OUTLIER_REVIEW`
- `CORPUS_LIMITATION`

## Promotion criteria to canonical SSoT

Promote `labels.medium.human.v1.json` to canonical SSoT when all are true:

- agreement thresholds met
- every query has 5–12 final relevants
- adjudication complete with audit trail
- scorer dry run succeeds with no schema errors
- metadata provenance file completed and committed
- decision log updated to `GO_LABELSET_CANONICAL`

---

## 7) Integration Plan (with existing `research/ab-eval/` workflow)

## How to plug into current scoring scripts

Current scripts already accept custom `--queries` and `--labels`.

Planned usage once files exist:

```powershell
.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_all.py --dataset 200 --queries research/ab-eval/data/queries.medium.human.v1.json --labels research/ab-eval/data/labels.medium.human.v1.json --variant all
```

This keeps corpus fixed (`corpus.200`) while replacing query/label inputs.

## Required runbook/operator updates

- Add a dedicated “Human label generation (medium)” section to runbook.
- Add promotion gate checklist.
- Add migration playbook from medium v1 to complex v2 reviewed labels.

---

## Phased Rollout Plan (small team optimized)

## Phase 0 — Spec freeze (0.5 day)

- finalize this workflow doc
- freeze medium query authoring rubric and acceptance gates

Verification:

- docs reviewed and accepted in decision log

Dependencies:

- none

## Phase 1 — Tooling implementation brief (1.0–1.5 days)

- implement lightweight HTML labeling UI and exporter (future coding task)
- validate autosave/resume and event logging

Verification:

- pilot with 2 internal reviewers on 4 queries

Dependencies:

- Phase 0

## Phase 2 — Pilot labeling + rubric calibration (0.5 day)

- run 4-query pilot
- inspect disagreement patterns
- tune wording/rubric examples only (not thresholds unless necessary)

Verification:

- pilot weighted kappa >= 0.50

Dependencies:

- Phase 1

## Phase 3 — Full medium labeling run (1.0 day)

- run full 20-query pass with two reviewers
- collect append-only judgments and checkpoints

Verification:

- 100% query coverage and complete raw artifact set

Dependencies:

- Phase 2

## Phase 4 — Aggregation, adjudication, canonicalization (0.5 day)

- deterministic conversion
- adjudication for borderline set
- produce canonical + meta files

Verification:

- all promotion criteria satisfied

Dependencies:

- Phase 3

## Phase 5 — Complex v2 migration prep (1.0 day)

- draft complex query rewrite using medium workflow lessons
- create migration checklist to `labels.complex.v2.human-reviewed.json`

Verification:

- migration plan accepted in decision log

Dependencies:

- Phase 4

Total estimated effort: **3.5–4.5 team-days** (small team, part-time reviewers).

---

## Alternatives Considered

### A) Full 40-query complex review immediately

Pros:

- direct replacement for current complex labels

Cons:

- high reviewer fatigue
- lower consistency for non-experts

Rejected because:

- poor ROI for small-team bandwidth; likely lower label quality.

### B) Keep metadata/proxy labels only

Pros:

- fastest path

Cons:

- does not measure nuanced visual/style relevance

Rejected because:

- conflicts with current blocker (human-reviewed SSoT needed).

### C) Open-ended text annotation without fixed rubric

Pros:

- rich qualitative comments

Cons:

- inconsistent scoring and hard conversion to deterministic labels

Rejected because:

- low reproducibility and difficult integration with current scorers.

---

## Validation Strategy

- Schema validation on all generated artifacts.
- Determinism check: two conversion runs on same inputs produce byte-identical canonical label file.
- Dry run scoring with canonical medium labelset and report generation.
- Agreement and conflict metrics attached to provenance metadata.

---

## Open Risks / Questions

- corpus diversity may limit per-query relevant counts for some intents.
- blind-first anonymous cards may slow reviewers who rely on known families; evaluate in pilot.
- final threshold (`mean_score >= 1.25`) may require calibration after pilot.
- migration strategy from medium-v1 results to complex-v2 query authoring still needs final owner assignment.

