# Comparison Report: Qwen3-VL Large Models vs Smoke Baseline

## Overview
This report compares the performance of large-scale Qwen3-VL models (32B and 235B) against the initial smoke test models (8B and Gemini variants) for generating vision-grounded font descriptions.

## Model Reliability & Success Rate
| Model | Success (Smoke) | Success (50-font) | Notes |
| :--- | :--- | :--- | :--- |
| **qwen/qwen3-vl-235b-a22b-instruct** | **100% (10/10)** | **100% (50/50)** | Extremely stable via OpenRouter. |
| **qwen/qwen3-vl-32b-instruct** | **100% (10/10)** | **100% (50/50)** | Extremely stable via OpenRouter. |
| qwen/qwen3-vl-8b-instruct (OR) | 100% (10/10) | N/A | High stability. |
| gemini-2.5-flash-lite-preview | 100% (10/10) | N/A | Very stable and fast. |
| gemini-3-flash-preview | 90% (9/10) | N/A | Occasionally overloaded (503). |

## Performance Metrics (Averages)
| Model | Avg Latency (s) | Provider | Est. Cost / Font |
| :--- | :--- | :--- | :--- |
| **qwen/qwen3-vl-32b-instruct** | **3.18s** | OpenRouter (Together) | ~$0.0005 |
| **qwen/qwen3-vl-235b-a22b-instruct** | **5.85s** | OpenRouter (DeepInfra) | ~$0.0003 |
| qwen/qwen3-vl-8b-instruct | 2.65s | OpenRouter (Together) | ~$0.0002 |
| gemini-2.5-flash-lite-preview | 1.37s | Gemini API | ~$0.0001 |
| gemini-3-flash-preview | 8.16s | Gemini API | ~$0.0020 |

## Qualitative Findings
*   **Precision**: The 32B and 235B models provide more nuanced descriptions of stroke terminals and geometry. For example, 32B identifies "closed, rounded terminals" where 8B might just say "rounded".
*   **Conciseness**: The 235B model tends to be more formal and structured, while 32B is slightly more descriptive in its summary field.
*   **Consistency**: Both large models showed higher internal consistency in mood tags compared to the 8B variants, which occasionally mixed conflicting moods.

## Conclusion
The **Qwen3-VL-235B** model via OpenRouter (DeepInfra) offers the best balance of depth and stability with acceptable latency (~6s) and very low cost. It is recommended for high-quality background description generation.
