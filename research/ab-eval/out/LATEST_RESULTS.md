# Latest Evaluation Results (200-Font Dataset)

- **Timestamp:** 2026-02-06
- **Dataset:** 200 fonts (corpus.200.json)
- **VL Model Used:** Qwen/Qwen3-VL-Embedding-2B (CPU)
- **Note:** Labels are metadata-derived proxy labels (category/subsets).

## Headline Metrics

| Variant | Recall@10 | Recall@20 | MRR@10 | Description |
| :--- | :--- | :--- | :--- | :--- |
| **A** | 0.1764 | 0.3454 | 0.7000 | Text-only (OpenRouter) |
| **B1** | 0.0800 | 0.1776 | 0.4729 | Vision-only (Image) |
| **B2** | 0.2893 | 0.4657 | 0.9222 | Vision-augmented (Image + Text) |
| **C (α=0.5)** | 0.3170 | 0.5127 | 0.9667 | Hybrid (A + B2) |
| **C (Best α=0.4)** | **0.3326** | - | **1.0000** | Optimized Hybrid |

## Alpha Sweep (Hybrid A + B2)

| Alpha | Recall@10 | MRR@10 |
| :--- | :--- | :--- |
| 0.0 (B2 only) | 0.2893 | 0.9222 |
| 0.4 (Best) | 0.3326 | 1.0000 |
| 0.5 | 0.3170 | 0.9667 |
| 1.0 (A only) | 0.1764 | 0.7000 |

## Sample Queries

### 1. serif fonts (q_001)
| Rank | Variant A | Variant B2 | Variant C (0.5) |
| :--- | :--- | :--- | :--- |
| 1 | Source Serif Pro | Cormorant | Literata |
| 2 | IM Fell French Canon | Libertinus Serif Display | Source Serif Pro |
| 3 | Bodoni Moda SC | Literata | Artifika |
| 10 | Marcellus SC | Spectral SC | Peralta |

### 2. sans-serif fonts (q_002)
| Rank | Variant A | Variant B2 | Variant C (0.5) |
| :--- | :--- | :--- | :--- |
| 1 | Basic | Google Sans Code | Sansation |
| 2 | Sansation | Sixtyfour | Basic |
| 3 | MonteCarlo | Sansation | Google Sans Code |
| 10 | Playwrite NG Modern | Metrophobic | Sometype Mono |

### 3. display fonts (q_003)
| Rank | Variant A | Variant B2 | Variant C (0.5) |
| :--- | :--- | :--- | :--- |
| 1 | Playwrite CL Guides | Micro 5 | Libertinus Serif Display |
| 2 | MonteCarlo | Major Mono Display | Micro 5 |
| 3 | Playwrite CA | Libertinus Serif Display | Major Mono Display |
| 10 | Comforter Brush | Ga Maamli | Libre Barcode 128 |

---

# GPU 8B Run (Qwen/Qwen3-VL-Embedding-8B)

- **Timestamp:** 2026-02-06
- **Machine:** Local Workstation (2× RTX 3090 Ti)
- **Model:** Qwen/Qwen3-VL-Embedding-8B (FP16)
- **Dataset:** 200 fonts (corpus.200.json)

## Headline Metrics

| Variant | Recall@10 | Recall@20 | MRR@10 | Description |
| :--- | :--- | :--- | :--- | :--- |
| **A** | 0.1783 | 0.3437 | 0.7000 | Text-only (OpenRouter Qwen3-8B) |
| **B1** | 0.1112 | 0.2016 | 0.5194 | Vision-only (Image) |
| **B2** | 0.3604 | 0.5549 | 1.0000 | Vision-augmented (Image + Text) |
| **C (α=0.0)** | **0.3604** | **0.5549** | **1.0000** | Best variant (B2 only) |
| **C (α=0.5)** | 0.3587 | 0.5693 | 1.0000 | Hybrid (A + B2) |

## Alpha Sweep (Hybrid A + B2)

| Alpha | Recall@10 | MRR@10 |
| :--- | :--- | :--- |
| 0.0 (Best) | 0.3604 | 1.0000 |
| 0.1 - 0.5 | 0.3587 | 1.0000 |
| 1.0 (A only) | 0.1783 | 0.7000 |

## Qualitative Observations (8B vs 2B)

- **Vision Strength**: B2 jumped from 0.2893 (2B) to 0.3604 (8B), a ~25% relative improvement.
- **Hybrid Necessity**: With the 2B model, the hybrid (C) was strictly better than B2. With 8B, B2 alone (Alpha=0) or very low Alpha is optimal, suggesting the vision model has become the primary source of truth.
- **MRR**: MRR@10 reached 1.0000 for the sample queries, indicating perfect top-rank retrieval for these categories.

## B2 vs B2-plus Ablation (200 Fonts)

- **Ablation Goal**: Test if adding full descriptions (A-equivalent) to the VL doc embedding improves retrieval over the lighter B2 payload.
- **B2 Payload**: Name + Category + Tags + Image.
- **B2-plus Payload**: Name + Category + Tags + Description + Image.

| Variant | Recall@10 | Recall@20 | MRR@10 |
| :--- | :--- | :--- | :--- |
| **B2** | **0.3604** | 0.5549 | 1.0000 |
| **B2-plus** | 0.3509 | **0.5579** | 1.0000 |

**Outcome**: Adding descriptions (B2-plus) resulted in a slight regression in Recall@10 (-2.6% relative) and a negligible gain in Recall@20 (+0.5%). The vision model appears to derive most of its semantic signal from the visual features and short-form metadata; longer descriptions may be introducing noise or diluting the visual signal in the shared embedding space.
