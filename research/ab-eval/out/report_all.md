# Overall Retrieval Evaluation Report

## Global Metrics

| Variant | Recall@10 | Recall@20 | MRR@10 |
| :--- | :--- | :--- | :--- |
| A | 1.0000 | 1.0000 | 1.0000 |
| B1 | 1.0000 | 1.0000 | 0.7500 |
| B2 | 1.0000 | 1.0000 | 1.0000 |
| C (alpha=0.5) | 1.0000 | 1.0000 | 1.0000 |

## Hybrid Fusion Alpha Sweep (A + B2)

| Alpha | Recall@10 | MRR@10 |
| :--- | :--- | :--- |
| 0.0 | 1.0000 | 1.0000 |
| 0.1 | 1.0000 | 1.0000 |
| 0.2 | 1.0000 | 1.0000 |
| 0.3 | 1.0000 | 1.0000 |
| 0.4 | 1.0000 | 1.0000 |
| 0.5 | 1.0000 | 1.0000 |
| 0.6 | 1.0000 | 1.0000 |
| 0.7 | 1.0000 | 1.0000 |
| 0.8 | 1.0000 | 1.0000 |
| 0.9 | 1.0000 | 1.0000 |
| 1.0 | 1.0000 | 1.0000 |

## Per-Query Top 10 Results (Sample)

### Query: clean modern sans serif for a website (`q1`)

| Rank | Variant A | Variant B2 | Variant C (0.5) |
| :--- | :--- | :--- | :--- |
| 1 | Roboto (0.711) | Roboto (0.692) | Roboto (0.702) |
| 2 | Playfair Display (0.560) | Playfair Display (0.435) | Playfair Display (0.498) |
| 3 | - | - | - |
| 4 | - | - | - |
| 5 | - | - | - |
| 6 | - | - | - |
| 7 | - | - | - |
| 8 | - | - | - |
| 9 | - | - | - |
| 10 | - | - | - |

### Query: elegant serif for luxury brand (`q2`)

| Rank | Variant A | Variant B2 | Variant C (0.5) |
| :--- | :--- | :--- | :--- |
| 1 | Playfair Display (0.807) | Playfair Display (0.613) | Playfair Display (0.710) |
| 2 | Roboto (0.554) | Roboto (0.575) | Roboto (0.564) |
| 3 | - | - | - |
| 4 | - | - | - |
| 5 | - | - | - |
| 6 | - | - | - |
| 7 | - | - | - |
| 8 | - | - | - |
| 9 | - | - | - |
| 10 | - | - | - |

