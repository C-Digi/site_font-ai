---
name: lightspec
description: A lightweight specification framework for managing requirements directly in a .lightspec/ directory with implementation tracking, plus decision records for core/critical specifications and major design choices. MANDATORY for all new project features or significant changes.
---

# LightSpec Skill

## Overview

LightSpec is a streamlined specification framework designed to maintain a "single source of truth" for requirements within a project-level `.lightspec/` directory. It provides a direct, low-friction method for tracking granular requirements and their implementation status, ensuring alignment between documentation and code without complex overhead.

- **When to Use:**
  - **MANDATORY** for all new features or significant modifications.
  - When you need precise, verifiable requirements tracking with minimal procedural friction.
  - At the outset of any task involving functional changes or additions.
- **Key Features:**
  - All specifications reside in `.lightspec/*.md`.
  - Implementation status is tracked by moving requirements from "Requirements" to "Completed" sections.
  - Major architectural and product decisions are tracked in decision records with explicit rationale.
  - Decision changes are preserved through supersession, never destructive overwrite.
  - Lightweight and self-contained.

## Skill Structure

- **`.lightspec/`**: Root directory for all specification files.
  - `[capability].md`: Individual specification files organized by feature or capability.
  - `decisions/`: Decision records (ADR-style) documenting major choices, tradeoffs, and consequences.
  - `research/`: Optional research notes, experiments, and findings that informed decisions.

## Instructions

### 1. Initial Setup
Ensure the `.lightspec/` directory exists at the project root. If missing, create it immediately before proceeding with any requirements documentation.

Ensure the following subdirectories also exist:
- `.lightspec/decisions/`
- `.lightspec/research/` (optional but recommended for non-trivial design work)

### 2. Perform Compatibility Analysis
Before drafting or modifying specifications, conduct a thorough cross-reference of the existing `.lightspec/` directory:
- **Scan Existing Specs:** Read all files in `.lightspec/` to identify overlapping features or potential conflicts.
- **Scan Existing Decisions:** Review `.lightspec/decisions/` for prior rationale, constraints, and superseded choices that may still affect implementation.
- **Analyze Dependencies:** Determine if your changes impact existing capabilities or rely on requirements defined in other spec files.
- **Ensure Integrity:** Verify that new requirements maintain system consistency and do not contradict established specifications or accepted decisions.

### 3. Create or Refine Specifications
- **File Organization:** Use descriptive, kebab-case filenames (e.g., `user-authentication.md`) for each major capability.
- **Iterative Updates:** If a feature is already documented, refine the existing file rather than creating a duplicate.
- **Decision Backlinks:** Include links to relevant decision records for core/critical specs, or whenever a major decision materially affects the capability.

### 4. Apply Specification Format
Maintain a consistent structure for every spec file. Requirement descriptions must begin on a new line for maximum clarity:

```markdown
# [Capability Name]

## Requirements

### [Requirement 1 Title]
[Requirement 1 Description - Clear and verifiable]

## Completed

### [Requirement 2 Title]
[Requirement 2 Description - Clear and verifiable]

## Decision Links (Optional)
- Required for core/critical specs; optional for routine changes.
- [DEC-YYYYMMDD-short-title](./decisions/DEC-YYYYMMDD-short-title.md)

## Scenarios
- [Scenario 1 - Narrative or Structured validation step]
```

### 5. Document Major Decisions and Rationale
For any major product, architecture, API, data model, security, or UX flow choice, create or update a decision record in `.lightspec/decisions/`.

Use this decision format:

```markdown
# DEC-YYYYMMDD-short-title

## Status
Accepted

## Context
[Problem framing, constraints, assumptions]

## Decision
[What was decided]

## Rationale
[Why this path was selected]

## Alternatives Considered
- [Alternative A + reason not chosen]
- [Alternative B + reason not chosen]

## Consequences
- [Positive impacts]
- [Tradeoffs / risks]

## Related Specs
- [capability-a](../capability-a.md)
- [capability-b](../capability-b.md)

## Related R&D
- [research-note](../research/research-note.md)

## Supersedes
- N/A

## Superseded By
- N/A
```

### 6. Preserve Decision History When Changes Occur
When a previously accepted decision changes:
- **Do Not Delete Legacy Decisions:** Never remove or overwrite old decision files.
- **Create a New Decision Record:** Add a new `DEC-...` file describing the new direction and rationale.
- **Link the Chain:**
  - In the new file, set `## Supersedes` to the old decision.
  - In the old file, update `## Status` to `Superseded` and set `## Superseded By` to the new decision.
- **Preserve Original Arguments:** Keep the original `Context`, `Decision`, and `Rationale` text intact for historical reference.
- **Update Spec Backlinks:** Revise each affected spec's `## Decision Links` section so it points to the active decision and, where useful, includes the superseded one for traceability.

### 7. Surface Core Specs in Project Rules for Onboarding and Reuse
For specs that are essential for onboarding, frequent reference, or core project understanding:
- Add a link and/or short excerpt in agent-facing rule entry points so the guidance is easy to discover.
- Prefer project rule surfaces such as:
  - `.kilocode/rules/*.md`
  - `CLAUDE.md`
  - `GEMINI.md`
- Keep excerpts concise and stable; link back to the canonical `.lightspec/*.md` spec to avoid duplication drift.

### 8. Track Implementation Progress
- **Move on Completion:** As requirements are implemented and verified, move the entire requirement block (title and description) from the `## Requirements` section to the `## Completed` section.
- **Section Definition:**
  - `## Requirements`: Contains requirements that are defined and approved but not yet present or fully functional in the codebase.
  - `## Completed`: Contains requirements that are fully implemented, tested, and verified against the defined scenarios.

## Success Criteria
- All requirements are documented in the `.lightspec/` directory before implementation.
- Specification files adhere strictly to the defined format.
- Major decisions are documented in `.lightspec/decisions/` with explicit rationale and alternatives.
- Core/critical spec files include `## Decision Links` backlinks to relevant decision records.
- Specs needed for onboarding, frequent reference, or core understanding are linked and/or excerpted in project rule entry files (for example, `.kilocode/rules/*.md`, `CLAUDE.md`, `GEMINI.md`).
- Decision changes preserve legacy records through a supersession chain.
- Compatibility analysis is performed to prevent requirements drift or conflict.
- Implementation status accurately and transparently reflects the state of the codebase.
