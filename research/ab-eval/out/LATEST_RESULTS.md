# Latest Evaluation Results

- **Timestamp:** 2026-02-05 07:37 UTC
- **Run Command:** `py -3.12 research/ab-eval/py/run_all.py --variant all`
- **Model Used (VL):** `Qwen/Qwen3-VL-Embedding-8B` (loaded on CPU)
- **Model Used (Text):** `qwen/qwen3-embedding-8b` (via OpenRouter)

## Headline Metrics

| Variant | Recall@10 | Recall@20 | MRR@10 |
| :--- | :--- | :--- | :--- |
| A (Text) | 1.0000 | 1.0000 | 1.0000 |
| B1 (VL Image) | 1.0000 | 1.0000 | 0.7500 |
| B2 (VL Hybrid) | 1.0000 | 1.0000 | 1.0000 |
| C (Fusion 0.5) | 1.0000 | 1.0000 | 1.0000 |

## Per-Query Example (Top 10)

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

## Artifacts
- [Report (Markdown)](report_all.md)
- [Report (JSON)](report_all.json)
