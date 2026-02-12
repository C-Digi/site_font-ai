# Preflight Readiness Validation: v3 vs v3_3

## 1. Ambiguities & Missing Inputs
- **Metadata**: Missing run_id, timestamp, commit_hash in automated outputs.
- **Repeats**: repeats=3 required for Week 1 but missing from script args.

## 2. Conflicts & Blockers
- **Schema Mismatch (BLOCKER)**: compare script output incompatible with validate_gates script.
- **Label Remapping Leak (BLOCKER)**: Label 2 not treated as 0 in Precision/Recall.

## 3. Resolution Assumptions
- Fresh paired rerun required for repeats=3 consistency.

## 4. Quota Risk
- **Ready**: key.md exists, backoff implemented.
