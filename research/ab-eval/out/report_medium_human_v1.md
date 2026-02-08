# Overall Retrieval Evaluation Report

## Global Metrics

| Variant | Recall@10 | Recall@20 | MRR@10 |
| :--- | :--- | :--- | :--- |
| A | 0.1214 | 0.2163 | 0.3808 |
| B1 | 0.2138 | 0.3164 | 0.2739 |
| B2 | 0.3523 | 0.5065 | 0.6465 |
| B2-plus | 0.3797 | 0.5175 | 0.5625 |
| C (alpha=0.5) | 0.2998 | 0.4911 | 0.4996 |
| D (RRF) | 0.2690 | 0.4910 | 0.4851 |

## Per-Class Breakdown

### Class: functional_pair

| Variant | Recall@10 | Recall@20 | MRR@10 | Count |
| :--- | :--- | :--- | :--- | :--- |
| A | 0.2071 | 0.3571 | 0.4167 | 5 |
| B1 | 0.2286 | 0.3476 | 0.4333 | 5 |
| B2 | 0.4440 | 0.5810 | 0.7222 | 5 |
| B2-plus | 0.4607 | 0.6095 | 0.6333 | 5 |
| C (alpha=0.5) | 0.3405 | 0.6012 | 0.7250 | 5 |
| D (RRF) | 0.3738 | 0.5476 | 0.7400 | 5 |

### Class: historical_context

| Variant | Recall@10 | Recall@20 | MRR@10 | Count |
| :--- | :--- | :--- | :--- | :--- |
| A | 0.0000 | 0.0000 | 0.0000 | 5 |
| B1 | 0.2500 | 0.4400 | 0.2200 | 5 |
| B2 | 0.4700 | 0.6200 | 0.4952 | 5 |
| B2-plus | 0.5600 | 0.6900 | 0.4667 | 5 |
| C (alpha=0.5) | 0.3900 | 0.6600 | 0.2352 | 5 |
| D (RRF) | 0.2300 | 0.6600 | 0.1586 | 5 |

### Class: semantic_mood

| Variant | Recall@10 | Recall@20 | MRR@10 | Count |
| :--- | :--- | :--- | :--- | :--- |
| A | 0.1821 | 0.3052 | 0.6667 | 5 |
| B1 | 0.1433 | 0.2044 | 0.1471 | 5 |
| B2 | 0.2302 | 0.4448 | 0.7000 | 5 |
| B2-plus | 0.2532 | 0.4634 | 0.5250 | 5 |
| C (alpha=0.5) | 0.2924 | 0.4182 | 0.5733 | 5 |
| D (RRF) | 0.3090 | 0.4182 | 0.4167 | 5 |

### Class: visual_shape

| Variant | Recall@10 | Recall@20 | MRR@10 | Count |
| :--- | :--- | :--- | :--- | :--- |
| A | 0.0964 | 0.2030 | 0.4400 | 5 |
| B1 | 0.2334 | 0.2734 | 0.2952 | 5 |
| B2 | 0.2650 | 0.3803 | 0.6686 | 5 |
| B2-plus | 0.2450 | 0.3069 | 0.6250 | 5 |
| C (alpha=0.5) | 0.1765 | 0.2850 | 0.4650 | 5 |
| D (RRF) | 0.1631 | 0.3384 | 0.6250 | 5 |

## Hybrid Fusion Alpha Sweep (A + B2)

| Alpha | Recall@10 | MRR@10 |
| :--- | :--- | :--- |
| 0.0 | 0.3523 | 0.6465 |
| 0.1 | 0.3665 | 0.5921 |
| 0.2 | 0.3493 | 0.5819 |
| 0.3 | 0.3277 | 0.5979 |
| 0.4 | 0.3277 | 0.5614 |
| 0.5 | 0.2998 | 0.4996 |
| 0.6 | 0.2568 | 0.4619 |
| 0.7 | 0.2188 | 0.4746 |
| 0.8 | 0.1680 | 0.4685 |
| 0.9 | 0.1438 | 0.4283 |
| 1.0 | 0.1214 | 0.3808 |

## Per-Query Top 10 Results (Sample)

### Query: geometric sans with perfect circles and low stroke variation (`cq_002`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant D (RRF) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Geom (0.767) | Geom (0.600) | Geom (0.636) | Geom (0.033) |
| 2 | Sansation (0.734) | Geist Mono (0.536) | Geist Mono (0.598) | Sansation (0.031) |
| 3 | Comforter Brush (0.705) | Google Sans Code (0.521) | Oxygen (0.570) | Geist Mono (0.031) |
| 4 | MonteCarlo (0.699) | Metrophobic (0.493) | Google Sans Code (0.554) | Google Sans Code (0.031) |
| 5 | Basic (0.698) | Oxygen (0.487) | Albert Sans (0.527) | Oxygen (0.031) |
| 6 | Oxygen (0.697) | Gudea (0.483) | Kumbh Sans (0.525) | Albert Sans (0.029) |
| 7 | Material Symbols (0.696) | Sansation (0.481) | Oxygen Mono (0.521) | Lexend Giga (0.028) |
| 8 | Google Sans Code (0.694) | Lexend Giga (0.480) | Metrophobic (0.519) | Metrophobic (0.027) |
| 9 | Geist Mono (0.693) | Albert Sans (0.477) | GFS Neohellenic (0.516) | Basic (0.027) |
| 10 | Albert Sans (0.692) | Kumbh Sans (0.474) | Roboto Flex (0.514) | Material Symbols (0.027) |

### Query: condensed industrial sans for tight headlines (`cq_003`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant D (RRF) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Encode Sans Condensed (0.735) | Encode Sans Condensed (0.518) | Saira Extra Condensed (0.579) | Encode Sans Condensed (0.033) |
| 2 | Saira Extra Condensed (0.717) | Saira Extra Condensed (0.513) | Encode Sans Condensed (0.576) | Saira Extra Condensed (0.032) |
| 3 | Playwrite CA (0.699) | Google Sans Code (0.450) | Google Sans Code (0.498) | Sansation (0.031) |
| 4 | Playwrite DE SAS (0.694) | Sansation (0.443) | Oxygen (0.488) | Google Sans Code (0.029) |
| 5 | Sansation (0.694) | Albert Sans (0.441) | Albert Sans (0.484) | Albert Sans (0.027) |
| 6 | Playwrite US Trad Guides (0.689) | Macondo (0.436) | Encode Sans Expanded (0.474) | Oxygen (0.027) |
| 7 | MonteCarlo (0.688) | Sixtyfour Convergence (0.433) | Ubuntu Sans Mono (0.471) | Material Symbols (0.027) |
| 8 | Playwrite CL Guides (0.686) | Kumbh Sans (0.432) | Cousine (0.470) | Kumbh Sans (0.025) |
| 9 | Playwrite IN (0.686) | Material Symbols (0.431) | Kumbh Sans (0.469) | Encode Sans Expanded (0.023) |
| 10 | Comforter Brush (0.684) | Iceberg (0.424) | Material Symbols (0.469) | Lexend Giga (0.023) |

### Query: heavy blackletter style for gothic impact (`cq_008`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant D (RRF) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Playwrite DE SAS (0.766) | Goblin One (0.466) | Goblin One (0.505) | Grenze Gotisch (0.028) |
| 2 | Playwrite CA (0.756) | Black And White Picture (0.464) | Elsie Swash Caps (0.481) | Grand Hotel (0.027) |
| 3 | Send Flowers (0.755) | Grenze Gotisch (0.457) | Marcellus SC (0.477) | Playwrite DE SAS (0.026) |
| 4 | Comforter Brush (0.755) | Rubik Storm (0.457) | Black And White Picture (0.477) | Gochi Hand (0.026) |
| 5 | Playwrite NG Modern Guides (0.755) | Holtwood One SC (0.446) | Grenze Gotisch (0.474) | MonteCarlo (0.025) |
| 6 | Playwrite US Trad Guides (0.755) | Macondo (0.445) | Gochi Hand (0.470) | Black And White Picture (0.025) |
| 7 | Playwrite CL Guides (0.753) | Ga Maamli (0.445) | Rubik Storm (0.468) | Send Flowers (0.025) |
| 8 | Playwrite BE VLG Guides (0.752) | Elsie Swash Caps (0.440) | Federant (0.467) | Holtwood One SC (0.024) |
| 9 | MonteCarlo (0.748) | Love Ya Like A Sister (0.440) | Holtwood One SC (0.466) | Babylonica (0.024) |
| 10 | Playwrite CZ Guides (0.746) | Ruthie (0.438) | Overlock SC (0.466) | Birthstone Bounce (0.024) |

