# Overall Retrieval Evaluation Report

## Global Metrics

| Variant | Recall@10 | Recall@20 | MRR@10 |
| :--- | :--- | :--- | :--- |
| A | 0.1764 | 0.3454 | 0.7000 |
| B1 | 0.0800 | 0.1776 | 0.4729 |
| B2 | 0.2893 | 0.4657 | 0.9222 |
| C (alpha=0.5) | 0.3170 | 0.5127 | 0.9667 |

## Hybrid Fusion Alpha Sweep (A + B2)

| Alpha | Recall@10 | MRR@10 |
| :--- | :--- | :--- |
| 0.0 | 0.2893 | 0.9222 |
| 0.1 | 0.3003 | 0.9333 |
| 0.2 | 0.3064 | 0.9333 |
| 0.3 | 0.3159 | 0.9333 |
| 0.4 | 0.3326 | 1.0000 |
| 0.5 | 0.3170 | 0.9667 |
| 0.6 | 0.3152 | 0.9667 |
| 0.7 | 0.3149 | 0.9667 |
| 0.8 | 0.2914 | 0.9111 |
| 0.9 | 0.2082 | 0.8333 |
| 1.0 | 0.1764 | 0.7000 |

## Per-Query Top 10 Results (Sample)

### Query: serif fonts (`q_001`)

| Rank | Variant A | Variant B2 | Variant C (0.5) |
| :--- | :--- | :--- | :--- |
| 1 | Source Serif Pro (0.823) | Cormorant (0.615) | Literata (0.700) |
| 2 | IM Fell French Canon (0.812) | Libertinus Serif Display (0.611) | Source Serif Pro (0.699) |
| 3 | Bodoni Moda SC (0.812) | Literata (0.590) | Artifika (0.693) |
| 4 | Literata (0.811) | Artifika (0.589) | Cormorant (0.692) |
| 5 | Playwrite CL Guides (0.803) | Source Serif Pro (0.575) | Libertinus Serif Display (0.691) |
| 6 | Playwrite DE SAS (0.801) | Peralta (0.574) | Antic Slab (0.681) |
| 7 | MonteCarlo (0.799) | Sixtyfour (0.571) | IM Fell French Canon (0.676) |
| 8 | Playwrite US Trad Guides (0.798) | Bentham (0.567) | Bentham (0.676) |
| 9 | Manuale (0.796) | Antic Slab (0.566) | Baskervville SC (0.675) |
| 10 | Marcellus SC (0.796) | Spectral SC (0.562) | Peralta (0.675) |

### Query: sans-serif fonts (`q_002`)

| Rank | Variant A | Variant B2 | Variant C (0.5) |
| :--- | :--- | :--- | :--- |
| 1 | Basic (0.796) | Google Sans Code (0.625) | Sansation (0.694) |
| 2 | Sansation (0.789) | Sixtyfour (0.606) | Basic (0.693) |
| 3 | MonteCarlo (0.782) | Sansation (0.599) | Google Sans Code (0.683) |
| 4 | Playwrite CL Guides (0.780) | Ubuntu Sans Mono (0.595) | Metrophobic (0.669) |
| 5 | Playwrite DE SAS (0.779) | Ubuntu Mono (0.594) | Noto Sans PhagsPa (0.669) |
| 6 | Playwrite US Trad Guides (0.775) | Sometype Mono (0.591) | Oxygen (0.668) |
| 7 | Send Flowers (0.775) | JetBrains Mono (0.589) | Actor (0.661) |
| 8 | Playwrite CA (0.773) | Basic (0.589) | Albert Sans (0.658) |
| 9 | Comforter Brush (0.773) | Actor (0.589) | Sixtyfour (0.655) |
| 10 | Playwrite NG Modern Guides (0.772) | Metrophobic (0.589) | Sometype Mono (0.653) |

### Query: display fonts (`q_003`)

| Rank | Variant A | Variant B2 | Variant C (0.5) |
| :--- | :--- | :--- | :--- |
| 1 | Playwrite CL Guides (0.833) | Micro 5 (0.634) | Libertinus Serif Display (0.685) |
| 2 | MonteCarlo (0.814) | Major Mono Display (0.608) | Micro 5 (0.677) |
| 3 | Playwrite CA (0.814) | Libertinus Serif Display (0.593) | Major Mono Display (0.673) |
| 4 | Playwrite US Trad Guides (0.813) | Bitcount Single (0.584) | Bitcount Single (0.669) |
| 5 | Playwrite CZ Guides (0.812) | Sixtyfour (0.583) | Federant (0.659) |
| 6 | Playwrite NG Modern Guides (0.811) | Tektur (0.583) | Tektur (0.656) |
| 7 | Send Flowers (0.811) | VT323 (0.578) | Workbench (0.647) |
| 8 | Playwrite DE SAS (0.810) | Federant (0.578) | Playwrite CZ Guides (0.646) |
| 9 | Playwrite RO Guides (0.810) | Black And White Picture (0.569) | Sixtyfour (0.645) |
| 10 | Comforter Brush (0.805) | Ga Maamli (0.561) | Libre Barcode 128 (0.644) |

