# Instruction Feedback — exec-promotion-rerun-v3-v3_3-repeats
- Timestamp (UTC): 2026-02-11T17:27:20.708Z
- Task status received: READY
- Confidence received: 0.95
- Initial execution mode decision: CONTINUE_SAFE (preflight)

## Ambiguities identified
- Whether `run_production_trial.py` supports `--repeats` in current checkout is unknown.
- Whether manual G4 evidence from `QA_SPECIMEN_V3_1.md` is acceptable for this exact rerun timestamp context may require conservative interpretation.

## Missing inputs
- None critical at preflight; required paths/commands are provided.
- Git branch target for commits not explicitly stated (will commit on current branch).

## Potential conflicts
- Must avoid non-scope edits while still producing aggregate artifact and report.
- Must include manual G4 in gate input artifact to avoid pending status; if evidence insufficient, must set non-pass transparently.

## Chosen resolutions
- Start with capability check for `--repeats`.
- If unsupported, execute explicit r1/r2/r3 per arm.
- Enforce paired fairness by fresh runs for both arms with matched model/prompt/gate/spec-dir/keys-file.
- Build strict provenance aggregate JSON from per-repeat comparison artifacts only (no fabricated metrics).
- Inject manual `visual_qa` from `QA_SPECIMEN_V3_1.md` with explicit evidence and confidence notes.
- Apply quality stop conditions:
  - invalidate near-zero-coverage repeats,
  - require >=2 valid repeats,
  - else `RETURN_RETRY` with exact blocker details.
- Complete mandatory atomic commit checkpoints:
  - CP1: run artifacts + per-repeat comparisons
  - CP2: aggregate + gate results + report
