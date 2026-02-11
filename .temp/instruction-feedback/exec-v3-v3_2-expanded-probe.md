# Instruction Feedback — exec-v3-v3_2-expanded-probe

## First-step compliance
- Overwrote this task-scoped feedback file before any other task action.

## Readiness self-check (source of truth applied)
- Preflight decision consumed as authoritative:
  - status: READY
  - confidence: 0.95
  - risk_level: low
  - assumptions: model=`gemini-3-pro-preview`, specimen=`specimens_v3`, `key.md` has valid keys
- Immediate execution stance: proceed unless a critical assumption is proven false by runtime checks/errors.

## Ambiguities identified
- `key.md` validity cannot be fully proven offline without executing probe scripts.
- `near-zero scored coverage` threshold is not numerically defined.
- `run_production_trial.py` may write outputs relative to either CWD or `research/ab-eval/out/` depending on implementation.

## Missing inputs (non-blocking)
- No numeric definition for near-zero scored coverage.
- No explicit required schema fields for per-arm report table beyond totals/metrics.

## Conflicts and resolutions
- No scope conflict detected.
- Runtime rule adopted for insufficient signal:
  - compare `common_coverage < 20` => insufficient signal (explicit).
  - additionally flag per-arm coverage as near-zero if the script output shows effectively minimal scored rows; report raw values transparently.
- Execute exact provided commands and artifact names.
- Update report with an informational/non-promotional Expanded Probe section.
