# Instruction Feedback

## Ambiguities
- "Blocked" is not explicitly defined (interpreted as prior smoke run failing to produce comparable scorable outputs, typically due to quota/429 behavior).
- "Use key rotation input if available" does not specify a required keys-file path (example only: `--keys-file key.md`).
- Small-sample size is a range (`--max-fonts` 4-8) without a mandated exact value.

## Missing Inputs
- No confirmed keys-file location for rotation.
- No explicit canonical smoke command for this rerun in the task body.
- No explicit stale/canonical designation for pre-existing smoke artifacts.

## Conflicts
- "Before any other action" conflicts with normal discovery-first workflow.
- Scope limits edited paths, while reruns may emit additional files; interpreted as allowed only when outputs match `research/ab-eval/out/week1_smoke_*`.

## Resolution Choices
- Overwrite this file first.
- Reuse established repo smoke command pattern.
- Select a midpoint sample size in-range when not prescribed.
- Use `--keys-file` if discoverable; otherwise run once without it and document evidence/blocker.
- Treat result as directional/informational only (non-promotional).
