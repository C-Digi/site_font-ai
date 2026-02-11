# Instruction Feedback

## Ambiguities
- The task says "work only in research/ab-eval outputs/reports plus .temp/instruction-feedback.md"; interpreted as allowing command execution that reads existing runner scripts but limiting file writes to `research/ab-eval/` report/output artifacts and `.temp/instruction-feedback.md` only.
- "Adjust names if needed" is open-ended; interpreted as preserving suggested filenames unless blocked by script argument constraints.
- "Early directional read for G1/G3 risk" with smoke sample is non-promotional; interpreted as trend-only and not gate-pass evidence.

## Missing Inputs
- No explicit required sample size was mandated beyond small max-fonts; selected `--max-fonts 8` from suggested command.
- No fixed output directory override argument was provided; assumed runner defaults or provided filenames under `research/ab-eval/out` are valid.
- No explicit timeout/retry policy was specified for smoke runs; will use script defaults.

## Conflicts
- Generic governance emphasizes promotion gates, while this task explicitly requests a low-cost smoke and states informational only.
- Scope restriction avoids broad reruns, but acceptance still expects comparison artifact; resolved by running exactly two small arms plus one compare command.

## Resolution Choices
- Run exactly two production trial commands with identical model/gate/max-fonts and differing prompt (`v3` vs `v3_2`).
- Use `week1_`-prefixed artifact names as required naming convention.
- Generate comparison artifact only if both arms succeed; otherwise record blocker in report.
- Create concise smoke report with commands, coverage, metric deltas, caveats, and explicit GO/NO-GO statement set to informational-only (non-promotional).
