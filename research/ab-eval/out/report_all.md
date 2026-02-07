# Overall Retrieval Evaluation Report

## Global Metrics

| Variant | Recall@10 | Recall@20 | MRR@10 |
| :--- | :--- | :--- | :--- |
| A | 0.1567 | 0.2900 | 0.2656 |
| B1 | 0.2200 | 0.3704 | 0.1888 |
| B2 | 0.3975 | 0.6867 | 0.5206 |
| B2-plus | 0.4575 | 0.7104 | 0.4879 |
| C (alpha=0.5) | 0.4054 | 0.6008 | 0.4562 |
| D (RRF) | 0.4079 | 0.6067 | 0.4756 |

## Per-Class Breakdown

### Class: functional_pair

| Variant | Recall@10 | Recall@20 | MRR@10 | Count |
| :--- | :--- | :--- | :--- | :--- |
| A | 0.2417 | 0.3833 | 0.3000 | 10 |
| B1 | 0.1833 | 0.3167 | 0.2333 | 10 |
| B2 | 0.4167 | 0.6583 | 0.3658 | 10 |
| B2-plus | 0.5250 | 0.8000 | 0.3436 | 10 |
| C (alpha=0.5) | 0.3667 | 0.6833 | 0.4458 | 10 |
| D (RRF) | 0.4583 | 0.6583 | 0.5736 | 10 |

### Class: historical_context

| Variant | Recall@10 | Recall@20 | MRR@10 | Count |
| :--- | :--- | :--- | :--- | :--- |
| A | 0.0917 | 0.2083 | 0.2000 | 10 |
| B1 | 0.1000 | 0.2750 | 0.0433 | 10 |
| B2 | 0.4417 | 0.6083 | 0.6333 | 10 |
| B2-plus | 0.5333 | 0.7000 | 0.5783 | 10 |
| C (alpha=0.5) | 0.4167 | 0.5750 | 0.4158 | 10 |
| D (RRF) | 0.3750 | 0.6000 | 0.4450 | 10 |

### Class: semantic_mood

| Variant | Recall@10 | Recall@20 | MRR@10 | Count |
| :--- | :--- | :--- | :--- | :--- |
| A | 0.1783 | 0.3167 | 0.3458 | 10 |
| B1 | 0.3050 | 0.4450 | 0.2644 | 10 |
| B2 | 0.2283 | 0.6883 | 0.4583 | 10 |
| B2-plus | 0.3683 | 0.6817 | 0.4986 | 10 |
| C (alpha=0.5) | 0.4017 | 0.5333 | 0.3483 | 10 |
| D (RRF) | 0.3600 | 0.5400 | 0.3436 | 10 |

### Class: visual_shape

| Variant | Recall@10 | Recall@20 | MRR@10 | Count |
| :--- | :--- | :--- | :--- | :--- |
| A | 0.1150 | 0.2517 | 0.2167 | 10 |
| B1 | 0.2917 | 0.4450 | 0.2143 | 10 |
| B2 | 0.5033 | 0.7917 | 0.6250 | 10 |
| B2-plus | 0.4033 | 0.6600 | 0.5311 | 10 |
| C (alpha=0.5) | 0.4367 | 0.6117 | 0.6150 | 10 |
| D (RRF) | 0.4383 | 0.6283 | 0.5400 | 10 |

## Hybrid Fusion Alpha Sweep (A + B2)

| Alpha | Recall@10 | MRR@10 |
| :--- | :--- | :--- |
| 0.0 | 0.3975 | 0.5206 |
| 0.1 | 0.4346 | 0.5038 |
| 0.2 | 0.4429 | 0.4880 |
| 0.3 | 0.4354 | 0.5131 |
| 0.4 | 0.4492 | 0.4969 |
| 0.5 | 0.4054 | 0.4562 |
| 0.6 | 0.3962 | 0.4478 |
| 0.7 | 0.3696 | 0.4512 |
| 0.8 | 0.3183 | 0.3906 |
| 0.9 | 0.2096 | 0.3300 |
| 1.0 | 0.1567 | 0.2656 |

## Per-Query Top 10 Results (Sample)

### Query: ultra-thin hairline serif with high contrast (`cq_001`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant D (RRF) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Comforter Brush (0.738) | Libertinus Serif Display (0.512) | Antic Slab (0.584) | Noto Serif Grantha (0.028) |
| 2 | Playwrite CA (0.726) | Quattrocento (0.506) | Bodoni Moda SC (0.566) | Literata (0.028) |
| 3 | MonteCarlo (0.724) | Noto Serif Grantha (0.506) | Literata (0.565) | Bodoni Moda SC (0.028) |
| 4 | Playwrite DE SAS (0.723) | Literata (0.503) | Quattrocento (0.558) | Artifika (0.026) |
| 5 | Playwrite US Trad Guides (0.723) | Bentham (0.503) | Libertinus Serif Display (0.556) | Petrona (0.026) |
| 6 | Playwrite NG Modern Guides (0.721) | Petrona (0.501) | Marcellus SC (0.556) | Libertinus Serif Display (0.026) |
| 7 | Playwrite CL Guides (0.720) | Artifika (0.501) | Libertinus Mono (0.555) | Antic Slab (0.026) |
| 8 | Send Flowers (0.719) | Bodoni Moda SC (0.497) | Tienne (0.555) | Tai Heritage Pro (0.025) |
| 9 | Playwrite BE VLG Guides (0.718) | Source Serif Pro (0.496) | Courier Prime (0.547) | Bentham (0.025) |
| 10 | Playwrite IN (0.713) | Tienne (0.496) | Noto Serif Lao (0.547) | Source Serif Pro (0.025) |

### Query: geometric sans with perfect circles and low stroke variation (`cq_002`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant D (RRF) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Geom (0.768) | Geom (0.600) | Geom (0.636) | Geom (0.033) |
| 2 | Sansation (0.733) | Geist Mono (0.536) | Geist Mono (0.599) | Sansation (0.031) |
| 3 | Comforter Brush (0.704) | Google Sans Code (0.521) | Oxygen (0.569) | Geist Mono (0.031) |
| 4 | MonteCarlo (0.701) | Metrophobic (0.492) | Google Sans Code (0.554) | Google Sans Code (0.031) |
| 5 | Basic (0.699) | Oxygen (0.487) | Albert Sans (0.527) | Oxygen (0.031) |
| 6 | Oxygen (0.697) | Gudea (0.484) | Kumbh Sans (0.525) | Albert Sans (0.029) |
| 7 | Material Symbols (0.696) | Sansation (0.482) | Oxygen Mono (0.521) | Lexend Giga (0.028) |
| 8 | Google Sans Code (0.695) | Lexend Giga (0.480) | Metrophobic (0.518) | Metrophobic (0.027) |
| 9 | Geist Mono (0.693) | Albert Sans (0.476) | GFS Neohellenic (0.516) | Basic (0.027) |
| 10 | Albert Sans (0.693) | Kumbh Sans (0.474) | Roboto Flex (0.514) | Kumbh Sans (0.027) |

### Query: condensed industrial sans for tight headlines (`cq_003`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant D (RRF) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Encode Sans Condensed (0.732) | Encode Sans Condensed (0.518) | Saira Extra Condensed (0.579) | Encode Sans Condensed (0.033) |
| 2 | Saira Extra Condensed (0.717) | Saira Extra Condensed (0.513) | Encode Sans Condensed (0.576) | Saira Extra Condensed (0.032) |
| 3 | Playwrite CA (0.698) | Google Sans Code (0.450) | Google Sans Code (0.497) | Sansation (0.031) |
| 4 | Playwrite DE SAS (0.694) | Sansation (0.443) | Oxygen (0.487) | Google Sans Code (0.029) |
| 5 | Sansation (0.693) | Albert Sans (0.441) | Albert Sans (0.484) | Albert Sans (0.027) |
| 6 | Playwrite US Trad Guides (0.689) | Macondo (0.436) | Encode Sans Expanded (0.474) | Oxygen (0.027) |
| 7 | MonteCarlo (0.689) | Sixtyfour Convergence (0.433) | Ubuntu Sans Mono (0.472) | Material Symbols (0.027) |
| 8 | Playwrite IN (0.686) | Kumbh Sans (0.432) | Cousine (0.470) | Kumbh Sans (0.025) |
| 9 | Playwrite CL Guides (0.686) | Material Symbols (0.431) | Kumbh Sans (0.469) | Lexend Giga (0.024) |
| 10 | Comforter Brush (0.683) | Iceberg (0.423) | Material Symbols (0.468) | Encode Sans Expanded (0.024) |

