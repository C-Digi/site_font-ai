# Report: v4_2 Directional Audit

## Executive Summary
- **Outcome:** NO-GO
- **Recommendation:** iterate
- **Reason:** Material regression in agreement and precision (-5.8% agreement delta). Guardrail `v4_2` failed to recover `v3` performance and introduced new hurts.

---

## Part A: Fault Attribution Audit (`v4_1`)

The following table summarizes the "hurts" from the `v4_1` segmented routing experiment vs the `v3` baseline.

| Query | Candidate Font | Outcome | `v4_1` rationale/evidence snippet | Primary Trigger | Corrective Logic Hypothesis |
|-------|----------------|---------|-----------------------------------|-----------------|-----------------------------|
| geometric sans with perfect circles and low stroke variation | Holtwood One SC | hurt | The 'O' and 'Q' are nearly perfect circles, and the stroke weight is consistent throughout the glyphs. | Section 5 Category Consistency | Prioritize technical modifiers (e.g., monoline) over category. |
| geometric sans with perfect circles and low stroke variation | LXGW WenKai Mono TC | hurt | The 'o' is a perfect circle, and the stroke variation is minimal across all glyphs. | Section 5 Category Consistency | Enforce technical modifier precedence. |
| soft rounded sans for a friendly children's brand | Sometype Mono | hurt | The rounded terminals and simple letterforms give it a friendly, approachable feel suitable for a children's brand. | Section 5 Category Consistency | Do not ignore 'sans' vs 'mono' distinction. |
| coding font with clear distinctions between 0 and O | Goblin One | hurt | The specimen shows clear distinctions between '0' and 'O', as well as 'l' and '1'. | Section 4 Vibe Over-extension | Stricter structural novelty requirement. |
| elegant and sophisticated serif for luxury branding | Marcellus SC | hurt | The high contrast and refined details in the uppercase letters (e.g., 'A', 'B', 'G') and the ampersand (&) suggest elegance and sophistication suitable for luxury branding. | Section 5 Category Consistency | Verify formal serif structure. |
| soft rounded sans for a friendly children's brand | Nova Mono | hurt | The rounded terminals and simple geometric shapes make it friendly and approachable, suitable for a children's brand. | Section 5 Category Consistency | Technical modifiers (proportional vs mono) must take precedence. |
| gentle script for wedding invitations | Rancho | hurt | The font has a gentle, flowing script style that would be appropriate for wedding invitations. | Other | Human sensitivity to 'gentle' vs 'casual'. |

### Observation Facts
- 71% of hurts (5/7) were triggered by `Section 5 Category Consistency`.
- `v3_4` (used in `v4_1`) appears to have lowered the model's threshold for technical mismatches (e.g., monospace vs proportional) by over-emphasizing architectural category consistency over specific query constraints.

---

## Part B: `v4_2` Directional Results

### Configuration
- **Treatment:** `v4_2` (Technical Modifier Precedence)
- **Control:** `v3` (Champion)
- **Context:** `specimens_v3_1`
- **Sample Size:** $n=20$ fonts (51 query-font pairs)

### Governance Gate Results

| Gate | Status | Value | Threshold |
|------|--------|-------|-----------|
| **G1 (Agreement Delta)** | **FAIL** | -0.0588 | >= 0.01 |
| **G2 (Precision Delta)** | **FAIL** | -0.0948 | >= -0.02 |
| **G3 (Helps/Hurts Net)** | **FAIL** | -3 | > 0 |
| **G4 (Visual QA)** | **PASS** | specimens_v3_1 used | Zero clipping |

### Metric Comparison

| Variant | Agreement | Precision | Recall | F1 | Helps | Hurts |
|---------|-----------|-----------|--------|----|-------|-------|
| `v3` (A) | 0.8235 | 0.7059 | 0.7500 | 0.7273 | - | - |
| `v4_2` | 0.7647 | 0.6111 | 0.6875 | 0.6471 | 3 | 6 |

### Hypotheses & Analysis
- `v4_2` successfully recovered 3 helps compared to `v3`, but introduced 6 new hurts.
- The instruction "Technical modifiers take precedence" may be confusing the model or causing it to misinterpret what a "primary technical modifier" is.
- In many cases, the model still ignores explicit "sans" vs "serif" or "mono" vs "proportional" constraints if it finds a "monoline" or "geometric" match.

## Final Recommendation
**NO-GO**. Advance to promotion candidate is rejected. 
The intervention `v4_2` failed all governance gates.
Further work should focus on decoupling the "Technical Modifiers" from the "Category Consistency" instructions or significantly simplifying the prompt back towards the `v3` baseline with only surgical additions.
