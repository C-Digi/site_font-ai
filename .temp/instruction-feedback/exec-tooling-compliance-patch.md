# Instruction Feedback — exec-tooling-compliance-patch

## Preflight Decision (Source of Truth)
- status: READY
- confidence: 0.95
- risk_level: low
- adopted_as_authoritative: true

## Required First-Step Confirmation
- action: Overwrite this task-scoped feedback file before any other action.
- result: completed by this write operation.

## Ambiguities Detected
- Commit scope says all file changes must be committed, while primary scope-in names only three files; validation commands are expected to produce artifacts under `research/ab-eval/out/` outside scope-in.
- Treatment key can be any non-`A` variant key, but `B` is the most validator-friendly canonical key.

## Missing Inputs
- none blocking implementation.

## Conflict Checks
- No critical contradiction with preflight READY state.
- Task-specific precedence is internally consistent for requested scope.

## Chosen Resolutions
- Enforce label remap policy (`casey_label == 2` -> `0`) in scoped metrics ingest/compute paths.
- Emit comparison schema compatible with gate validator including:
  - `variants["A"]` (control)
  - `variants["B"]` (treatment)
  - `helps_hurts` object with `helps_count` and `hurts_count`
- Preserve existing useful fields when possible while ensuring validator compatibility.
- Run only requested lightweight validation commands; no model/eval runs.
- Apply mandatory atomic commit strategy:
  - checkpoint 1: scoped Python patches
  - checkpoint 2: regenerated comparison/gate artifacts if changed/generated

## Early-Exit Condition
- If an unresolvable critical schema contradiction emerges within scoped files, return `RETURN_RETRY` with exact blocker.
