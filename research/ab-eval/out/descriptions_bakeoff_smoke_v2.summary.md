# Font Description Bakeoff Summary

- **Run Date:** 2026-02-07 13:29:37
- **Input Artifact:** `descriptions_bakeoff_smoke_v2.jsonl`
- **Total Rows Attempted:** 50
- **Total Success:** 49
- **Total Failures:** 1
- **Total Resumed/Skipped:** 0

## Model Performance & Availability

| Model | Provider | Status | Success | Failure | Avg Latency (s) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| gemini-3-flash-preview | gemini | 🟡 | 9 | 1 | 8.16 |
| gemini-2.5-flash-lite-preview-09-2025 | gemini | 🟢 | 10 | 0 | 1.37 |
| Qwen/Qwen3-VL-8B-Instruct | local_qwen | 🟢 | 10 | 0 | 12.6 |
| Qwen/Qwen3-VL-4B-Instruct | local_qwen | 🟢 | 10 | 0 | 10.04 |
| qwen/qwen3-vl-8b-instruct | openrouter | 🟢 | 10 | 0 | 2.65 |

## Cost Estimate (Rough)

- **Gemini Primary:** ~$0.001 - $0.005 per font (including image overhead).
- **Local Qwen:** $0.00 (Compute only).
- **OpenRouter Fallback:** ~$0.002 per font.

## Error Sample (Last 5)

- `Gemini HTTP 503: {
  "error": {
    "code": 503,
    "message": "The model is overloaded. Please try again later.",
    "status": "UNAVAILABLE"
  }
}
`
