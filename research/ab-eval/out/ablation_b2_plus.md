# Overall Retrieval Evaluation Report

## Global Metrics

| Variant | Recall@10 | Recall@20 | MRR@10 |
| :--- | :--- | :--- | :--- |
| A | 0.1783 | 0.3437 | 0.7000 |
| B1 | 0.1112 | 0.2016 | 0.5194 |
| B2 | 0.3604 | 0.5549 | 1.0000 |
| B2-plus | 0.3509 | 0.5579 | 1.0000 |
| C (alpha=0.5) | 0.3587 | 0.5693 | 1.0000 |

## Hybrid Fusion Alpha Sweep (A + B2)

| Alpha | Recall@10 | MRR@10 |
| :--- | :--- | :--- |
| 0.0 | 0.3604 | 1.0000 |
| 0.1 | 0.3587 | 1.0000 |
| 0.2 | 0.3587 | 1.0000 |
| 0.3 | 0.3587 | 1.0000 |
| 0.4 | 0.3587 | 1.0000 |
| 0.5 | 0.3587 | 1.0000 |
| 0.6 | 0.3536 | 1.0000 |
| 0.7 | 0.3250 | 1.0000 |
| 0.8 | 0.2967 | 0.8778 |
| 0.9 | 0.2149 | 0.8000 |
| 1.0 | 0.1783 | 0.7000 |

## Per-Query Top 10 Results (Sample)

### Query: serif fonts (`q_001`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant C (0.5) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Source Serif Pro (0.823) | Tienne (0.549) | Source Serif Pro (0.609) | Source Serif Pro (0.681) |
| 2 | IM Fell French Canon (0.812) | Artifika (0.541) | Marcellus SC (0.601) | Artifika (0.669) |
| 3 | Bodoni Moda SC (0.812) | Source Serif Pro (0.539) | Tienne (0.595) | Tienne (0.667) |
| 4 | Literata (0.811) | Noto Serif Armenian (0.533) | Holtwood One SC (0.592) | Noto Serif Armenian (0.662) |
| 5 | Playwrite CL Guides (0.803) | Holtwood One SC (0.525) | Artifika (0.589) | Noto Serif Grantha (0.657) |
| 6 | Playwrite DE SAS (0.800) | Marko One (0.522) | Antic Slab (0.585) | Marcellus SC (0.656) |
| 7 | MonteCarlo (0.799) | Noto Serif Grantha (0.518) | Baskervville SC (0.584) | IM Fell French Canon (0.654) |
| 8 | Playwrite US Trad Guides (0.798) | Noto Serif Lao (0.518) | Bodoni Moda SC (0.582) | Noto Serif Lao (0.653) |
| 9 | Marcellus SC (0.797) | Quattrocento (0.517) | Noto Serif Lao (0.581) | Manuale (0.652) |
| 10 | Manuale (0.797) | Marcellus SC (0.516) | Literata (0.578) | Baskervville SC (0.652) |

### Query: sans-serif fonts (`q_002`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant C (0.5) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Basic (0.796) | Sansation (0.546) | Oxygen (0.589) | Sansation (0.668) |
| 2 | Sansation (0.790) | Aldrich (0.523) | Sansation (0.586) | Basic (0.649) |
| 3 | MonteCarlo (0.782) | Albert Sans (0.521) | Albert Sans (0.575) | Albert Sans (0.641) |
| 4 | Playwrite CL Guides (0.780) | Noto Sans Balinese (0.506) | Basic (0.575) | Oxygen (0.625) |
| 5 | Playwrite DE SAS (0.778) | Basic (0.502) | Cairo (0.560) | Noto Sans Balinese (0.622) |
| 6 | Send Flowers (0.775) | Oxygen (0.502) | Aldrich (0.559) | Noto Sans PhagsPa (0.621) |
| 7 | Playwrite US Trad Guides (0.775) | Cairo (0.495) | Noto Sans PhagsPa (0.554) | Metrophobic (0.617) |
| 8 | Playwrite CA (0.773) | Noto Sans Nag Mundari (0.492) | Kumbh Sans (0.550) | Belleza (0.615) |
| 9 | Comforter Brush (0.773) | Kumbh Sans (0.492) | Noto Sans Balinese (0.536) | Aldrich (0.613) |
| 10 | Playwrite NG Modern Guides (0.772) | Gudea (0.488) | Encode Sans Condensed (0.536) | Kumbh Sans (0.611) |

### Query: display fonts (`q_003`)

| Rank | Variant A | Variant B2 | Variant B2-plus | Variant C (0.5) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Playwrite CL Guides (0.833) | Black And White Picture (0.554) | Micro 5 (0.592) | Libertinus Serif Display (0.652) |
| 2 | MonteCarlo (0.814) | Macondo (0.537) | Libertinus Serif Display (0.574) | Black And White Picture (0.632) |
| 3 | Playwrite CA (0.814) | Micro 5 (0.536) | Faster One (0.571) | Bungee Inline (0.631) |
| 4 | Playwrite US Trad Guides (0.813) | Jersey 20 (0.535) | Jersey 20 (0.569) | Micro 5 (0.629) |
| 5 | Playwrite CZ Guides (0.812) | Goblin One (0.531) | Goblin One (0.566) | Bitcount Single (0.628) |
| 6 | Send Flowers (0.811) | Libertinus Serif Display (0.525) | Black And White Picture (0.563) | Libre Barcode 128 (0.627) |
| 7 | Playwrite NG Modern Guides (0.811) | Sarina (0.524) | Calistoga (0.562) | Faster One (0.626) |
| 8 | Playwrite RO Guides (0.810) | Faster One (0.522) | Libre Barcode 128 (0.561) | Sarina (0.621) |
| 9 | Playwrite DE SAS (0.809) | Iceberg (0.522) | Elsie Swash Caps (0.557) | Flow Block (0.617) |
| 10 | Comforter Brush (0.806) | Kumar One (0.520) | Bitcount Single (0.556) | Londrina Sketch (0.617) |

