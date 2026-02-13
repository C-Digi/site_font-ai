# Week4 Phase3 Hurts Root-Cause Analysis

## 4. Loss Type Distribution
| Loss Type | Count | Share |
|-----------|-------|-------|
| TP_LOST | 3 | 43% |
| FP_INTRODUCED | 4 | 57% |

**Interpretation:** v5_1 is slightly more conservative (loses some TPs) but also introduces new FPs. The net effect is marginally negative for recall but positive for precision.

---

## 5. Query Class Distribution
| Query Class | Count | Share |
|-------------|-------|-------|
| ``use_case`` | 4 | 57% |
| ``semantic_history`` | 2 | 29% |
| ``visual_shape`` | 1 | 14% |

**Observation:** `use_case` queries dominate the hurts, but the underlying motifs within this class are heterogeneous.

---

## 6. Detailed Hurts Analysis

### 6.1 TP_LOST Cases (Treatment rejected, Human accepted)

#### H1: cq_003 - Encode Sans Condensed
- **Query:** 'condensed industrial sans for tight headlines'
- **v5_1 Evidence:** 'The font features a double-story a and g with organic, humanist curves... which contradicts the rigid, mechanical, or geometric aesthetic required for a true industrial classification.'
- **Motif:** Over-strict semantic interpretation
- **Analysis:** v5_1's Diagnostic Neutrality guardrail required explicit evidence for 'industrial' classification. The model correctly identified humanist curves but over-applied the guardrail.

#### H2: cq_009 - LXGW WenKai Mono TC
- **Query:** 'soft rounded sans for a friendly children''s brand'
- **v5_1 Evidence:** 'The font is a monospaced typewriter style with slab serifs... failing the technical classification of a soft rounded sans.'
- **Motif:** Questionable human label
- **Analysis:** The model correctly identified this as a monospace slab-serif font. The human label of 1 may be an error.

#### H4: cq_012 - Esteban
- **Query:** 'stern and authoritative serif for a law firm'
- **v5_1 Evidence:** 'The prominent ball terminals on the y, f, and r create a soft, friendly, and humanist texture that directly contradicts the stern and rigid vibe requested.'
- **Motif:** Over-strict semantic interpretation
- **Analysis:** v5_1 rejected Esteban for 'stern' due to ball terminals. The guardrail over-weighted the semantic constraint.

### 6.2 FP_INTRODUCED Cases (Treatment accepted, Human rejected)

#### H3: cq_010 - Ga Maamli
- **Query:** 'traditional calligraphic hand with varying line weight'
- **v5_1 Evidence:** 'sharp transitions between thick downstrokes and thinner connecting strokes, strictly adhering to the mechanics of a broad-nib calligraphic tool.'
- **Motif:** Calligraphy vs. Casual Script
- **Analysis:** v5_1 saw calligraphic features and accepted. Human rejection suggests Ga Maamli is more decorative than 'traditional calligraphic.'

#### H5: cq_015 - Suravaram
- **Query:** 'cold and sterile monospace for a terminal interface'
- **v5_1 Evidence:** 'perfectly equidistant vertical markers... confirming the strict monospacing required for a terminal interface.'
- **Motif:** Monospace Hallucination
- **Analysis:** v5_1 claimed monospacing based on visual analysis. Human rejection suggests Suravaram may not be monospaced or lacks the 'cold and sterile' aesthetic.

#### H6: cq_019 - Reem Kufi Fun
- **Query:** 'nostalgic and vintage display font for a 1920s poster'
- **v5_1 Evidence:** 'geometric construction... aligns perfectly with the Bauhaus and Art Deco typography styles that defined the late 1920s.'
- **Motif:** Vintage/Era Hallucination
- **Analysis:** v5_1 attributed 1920s era based on geometric construction. Reem Kufi Fun is a modern font with no actual 1920s provenance.

#### H7: cq_021 - Bentham
- **Query:** '19th century victorian style display serif'
- **v5_1 Evidence:** 'high contrast, vertical stress, and ball terminals... definitive hallmarks of 19th-century Victorian display typography.'
- **Motif:** Vintage/Era Hallucination
- **Analysis:** v5_1 attributed Victorian era based on visual features. Human rejection suggests Bentham is not considered a genuine Victorian display serif.

---

## 7. Fact vs. Hypothesis Separation

### Facts (Evidence-Based)
- 7 hurts identified from v3 vs v5_1 comparison
- Top motif share is 29% (below 50% threshold)
- TP_LOST and FP_INTRODUCED are nearly balanced (3 vs 4)
- `use_case` queries account for 57% of hurts
- P2 localization identified similar failure buckets

### Hypotheses (Require Validation)
- H2 (cq_009) human label may be incorrect
- H5 (cq_015) Suravaram may not actually be monospaced
- Over-strict semantic interpretation may be a side effect of Diagnostic Neutrality guardrail
- Vintage/Era hallucinations may require metadata integration

---

## 8. Decision Rationale

### Why NO_ACTIONABLE_SINGLE_VARIABLE?

1. **No Dominant Motif:** Top motif accounts for only 29% of hurts, below the 50% threshold.

2. **Opposite Intervention Directions:** The two leading motifs require opposite interventions:
   - Over-strict semantic interpretation - guardrails
   - Vintage/Era Hallucination - evidence requirements

3. **Known Unaddressable Buckets:** P2 localization identified 'Vintage/Era Hallucination' as not addressable via prompt alone (requires metadata).

---

## 9. Stop Recommendation

**Recommendation:** Pause single-variable prompt iteration for v5_x series.

**Alternative Paths:**
1. Multi-variable intervention: Combine relaxed semantic guardrails with strengthened era-classification evidence
2. Metadata integration: Add provenance/era metadata
3. Human label audit: Review cq_009 label

---

## 10. Governance Compliance

- [x] All 7 hurts classified by query class, motif, and loss type
- [x] Motif distribution quantified with threshold check
- [x] Fact vs. hypothesis separation documented
- [x] One-variable-at-a-time discipline maintained
- [x] Decision logic applied per method requirements

---

## 11. Artifacts
| Artifact | Path |
|----------|------|
| This Report | ``research/ab-eval/REPORT_WEEK4_P3_HURTS_ROOTCAUSE.md`` |
| JSON Summary | ``research/ab-eval/out/week4_p3_hurts_rootcause.json`` |
| Source Comparison | ``research/ab-eval/out/week4_v3_vs_v5_1_fullset_comparison.json`` |
| P2 Localization | ``research/ab-eval/out/p2_failure_localization_summary.json`` |
