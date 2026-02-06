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
