# DEC-20260208-02-lightspec-initialization

## Status
Accepted

## Context
The project introduced LightSpec and needs a canonical requirements/decision workspace in-repo. Existing guidance and decision context already exist across rollout/eval docs, but there was no initialized `.lightspec/` structure to serve as the formal source-of-truth for forward requirement tracking.

## Decision
Initialize LightSpec with a root index, one core capability spec (`font-search-rag.md`), and an ADR record to anchor governance.

## Rationale
- Establishes immediate, low-friction structure for future requirement-first changes.
- Aligns with current project architecture where B2 is default and queue-based JIT seeding is non-blocking.
- Creates a traceable entry point for future superseding decisions.

## Alternatives Considered
- Defer LightSpec creation until next feature cycle — rejected because it delays requirement hygiene and creates drift risk.
- Create many specs upfront — rejected because it front-loads overhead before validating spec boundaries.

## Consequences
- Positive: Requirements and major decisions can now be tracked in a consistent format.
- Tradeoff: Team must keep `.lightspec/` updated during ongoing work to preserve usefulness.

## Related Specs
- [font-search-rag](../font-search-rag.md)

## Related R&D
- [Offline A/B decision log](../../../research/ab-eval/DECISIONS.md)
- [Production rollout decision log](../../../research/prod-rollout/DECISIONS.md)

## Supersedes
- N/A

## Superseded By
- N/A

