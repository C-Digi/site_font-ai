# P5-06B Directional Intervention Trial Report (Rank-Boundary-Aware Scaling)

- **Run ID:** `p5_06b_directional_candidate`
- **Date (UTC):** 2026-02-14T07:39:31.605953+00:00
- **Variant ID:** `p5_06b_directional_candidate`
- **Baseline:** `v3`
- **Decision:** **DIRECTIONAL GO** (G1/G2/G3 PASS, G4 PENDING)

## Scope and Policy Note

This artifact is a **bounded offline directional intervention trial** using the coverage-remediated balanced slice from P5-05C with rank-boundary-aware penalty scaling. It is **not** a global promotion trial, and G1/G2/G3/G4 governance semantics remain unchanged.

## Preflight Inputs

- `research/ab-eval/out/full_set_review_export_1770612809775.json`
- `research/ab-eval/out/g3_v3_gated_results.json`
- `research/ab-eval/data/queries.medium.human.v1.json`
- `research/ab-eval/data/corpus.200.json`
- `research/ab-eval/out/week4_p3_hurts_rootcause.json`

## Execution Parameters

| Parameter | Value |
|---|---|
| Seed | `42` |
| Repeats | `1` |
| Label Policy | `2->0` remap |
| Target Total | `12` |
| Target Per Motif | `6` |
| Base Vintage Penalty | `0.20` |
| Base Strict Penalty | `0.18` |
| Rank Scaling Factor | `0.15` |
| Flip Feasibility Threshold | `0.08` |

## Rank-Boundary-Aware Scaling Formula

```
scaled_penalty = base_penalty * (1 + (10 - baseline_rank) * 0.15)
```

This formula applies larger penalties to higher-ranked items (closer to rank 1) because:
- They have more influence on top-10 membership
- Demoting them has more impact on precision metrics
- Lower-ranked items near the boundary need smaller penalties to flip

### Example Penalty Calculations

| Baseline Rank | Scaling Multiplier | Base Penalty (Strict) | Scaled Penalty |
|---|---|---|---|
| 1 | 2.35 | 0.18 | 0.423 |
| 2 | 2.20 | 0.18 | 0.396 |
| 4 | 1.90 | 0.18 | 0.342 |
| 5 | 1.75 | 0.18 | 0.315 |
| 8 | 1.30 | 0.18 | 0.234 |
| 10 | 1.00 | 0.18 | 0.180 |

## Selection Summary

- **Hard-Negative Definition:** `human==0` (after remap) AND baseline `v3` rank <= 10
- **Targeted Motifs:** `over_strict_semantic`, `vintage_era`
- **Pool Counts:** `vintage_era=32`, `over_strict_semantic=17`, `total=49`
- **Selected Counts:** `over_strict_semantic=6`, `vintage_era=6`
- **Selected Total:** `12` (balanced slice from P5-05C)

## Flip-Feasibility Check

- **Status:** PASS
- **Threshold:** `margin_to_boundary <= 0.08`
- **Boundary Candidates Found:** 6 (all from `cq_003`)
- **All candidates had `margin_to_boundary = 0.0`** (tight boundary between rank 10 and 11)

## Global Metrics Table

| Variant | Agreement | Precision | Recall | F1 |
|---|---|---|---|---|
| `v3` (baseline) | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `p5_06b_directional_candidate` | 0.2500 | 0.0000 | 0.0000 | 0.0000 |

**Note:** All selected pairs are hard-negatives (human=0) with baseline prediction=1. The intervention successfully demoted 3 hard-negatives from top-10, resulting in +25% agreement improvement.

## Gate Status

| Gate | Status | Value | Threshold |
|---|---|---|---|
| **G1 (Agreement Delta)** | **PASS** | +0.2500 | >= +1.0% |
| **G2 (Precision Delta)** | **PASS** | 0.0000 | >= -2.0% |
| **G3 (Helps/Hurts Net)** | **PASS** | +3 | > 0 |
| **G4 (Visual QA)** | **PENDING** | Manual | Zero clipping/overlap |

## Per-Query-Class Breakdown

| Query Class | Pairs | Helps | Hurts |
|---|---|---|---|
| `visual_shape` | 6 | 3 | 0 |
| `historical_context` | 6 | 0 | 0 |

## Helps/Hurts Analysis

- **Helps Count:** 3
- **Hurts Count:** 0
- **Net:** +3

### Helps (Successful Demotions)

| Query ID | Font Name | Motif | Baseline Rank | Treatment Rank | Penalty Applied |
|---|---|---|---|---|---|
| `cq_003` | Goblin One | `over_strict_semantic` | 2 | 13 | 0.396 |
| `cq_003` | Major Mono Display | `over_strict_semantic` | 4 | 12 | 0.342 |
| `cq_003` | Marcellus SC | `over_strict_semantic` | 5 | 11 | 0.315 |

### Boundary Flip Diagnostics

**Total Boundary Flips:** 6 (3 exits, 3 entries)

#### Exited Top-10 (Hard-Negatives Demoted)

| Query ID | Font Name | Baseline Rank | Treatment Rank | Penalty | Adjusted Score |
|---|---|---|---|---|---|
| `cq_003` | Goblin One | 2 | 13 | 0.396 | 0.604 |
| `cq_003` | Major Mono Display | 4 | 12 | 0.342 | 0.658 |
| `cq_003` | Marcellus SC | 5 | 11 | 0.315 | 0.685 |

#### Entered Top-10 (Replacement Fonts)

| Query ID | Font Name | Baseline Rank | Treatment Rank | Penalty | Adjusted Score |
|---|---|---|---|---|---|
| `cq_003` | Rancho | 11 | 4 | 0.18 | 0.77 |
| `cq_003` | Tektur | 12 | 5 | 0.18 | 0.77 |
| `cq_003` | Sixtyfour | 13 | 9 | 0.18 | 0.72 |

## Qualitative Notes

1. **Rank-Boundary-Aware Scaling Effective:** The scaled penalties successfully demoted 3 hard-negatives from top-10, compared to 0 demotions in P5-06A with flat penalties.

2. **Motif Concentration:** All 3 helps came from the `over_strict_semantic` motif (`cq_003`), suggesting this motif is more actionable for penalty-based intervention.

3. **Vintage Era Motif Neutral:** The `vintage_era` motif pairs (`cq_024`, `cq_025`) remained in top-10 despite penalties, indicating either:
   - Insufficient penalty magnitude for this motif
   - Need for different intervention strategy (e.g., boost vintage-appropriate fonts)

4. **Boundary Tightness:** The `cq_003` query had `margin_to_boundary = 0.0` between ranks 10 and 11, making it ideal for penalty-based demotion.

5. **Directional Evidence Only:** This trial confirms that rank-boundary-aware penalty scaling can produce measurable agreement improvements on a curated hard-negative slice. This is **not** sufficient for global promotion.

## Comparison with P5-06A (Flat Penalties)

| Metric | P5-06A (Flat) | P5-06B (Scaled) | Delta |
|---|---|---|---|
| Agreement Delta | 0.0000 | +0.2500 | +0.2500 |
| Helps Count | 0 | 3 | +3 |
| Hurts Count | 0 | 0 | 0 |
| Boundary Flips | 0 | 6 | +6 |
| G1 Status | FAIL | PASS | - |
| G3 Status | FAIL | PASS | - |

## Artifacts Generated

- `research/ab-eval/out/p5_06b_directional_candidate.json`
- `research/ab-eval/out/p5_06b_v3_vs_directional_comparison.json`
- `research/ab-eval/out/p5_06b_v3_vs_directional_gates.json`

## Governance Semantics

**Unchanged.** This trial is a bounded offline directional intervention only. G1/G2/G3/G4 promotion gate semantics from `EVALUATION_CONTRACT.md` remain unchanged. A full-set validation would be required before any production-path modification.

---

Generated by `research/ab-eval/py/run_p5_04a_hardneg_trial.py` with `--variant-id p5_06b_directional_candidate --vintage-penalty 0.20 --strict-penalty 0.18`.
