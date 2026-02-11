# Execution Feedback: v3 vs v3_3 Expanded Probe

- status: preflight-written
- execution_mode: CONTINUE_SAFE

## Ambiguities Identified
- Reuse criteria for existing control artifact is implied but not fully explicit.
  - resolution: Treat control artifact as reusable only if it is present and parameter-matched (`prompt=v3`, `model=gemini-3-pro-preview`, `gate=0.9`, `specimens=specimens_v3`, `max_fonts=40`) and structurally valid for comparison.
- Prompt parity requirement references both trial and intervention runners without defining exact parity behavior.
  - resolution: Add `v3_3` option in both files with equivalent prompt body/selection behavior so either path resolves the same prompt text.
- Atomic commit checkpoint requirement could conflict if no net changes occur in a checkpoint.
  - resolution: Create checkpoint commits only when there are staged changes for that checkpoint; preserve atomicity by grouping prompt/parity code first, then artifacts/report second.

## Missing Inputs / Assumptions
- `key.md` location is not explicitly scoped beyond command examples.
  - resolution: Use exactly `--keys-file key.md` from workspace root command context, matching provided command.
- Existing control artifact validity is unknown at preflight.
  - resolution: Inspect artifact existence and metadata before deciding rerun.

## Potential Conflicts
- Instruction to avoid unnecessary control rerun vs requirement to produce comparable output.
  - resolution: Reuse control only if comparable; otherwise rerun once with matching params.
- Quota limits may truncate treatment run.
  - resolution: Preserve raw/treatment partial artifacts, log exact errors, continue to comparison/report with caveats when possible.

## Critical Blocker Check
- None discovered at preflight.
- decision: CONTINUE_SAFE
