# Track A Review Packet: Quality-First Research (Specimen v2 & Schema v2)

## Overview
This packet contains the outputs of Track A (Steps A, B, and C) as defined in `.lightspec/progress.md`. 
The goal of this track was to improve the retrieval quality by upgrading the input representation (specimen) and the descriptor ontology (schema).

## Generated Artifacts
- **Specimen v2 Renderer**: `research/ab-eval/py/render_specimen_v2.py`
- **Attribute Schema v2 Prompt**: `research/ab-eval/py/prompt_v2.txt`
- **Updated Generator**: `research/ab-eval/py/gen_font_descriptions.py` (added V2 support, OpenRouter `gpt-5.2` routing, and high-reasoning mode).
- **Test Specimen**: `research/ab-eval/out/specimens_v2_toy/Playfair_Display.png` (1024x1024 deterministic layout).
- **Test Output (V2)**: `research/ab-eval/out/test_v2_real.jsonl` (contains the GPT-5.2 generated description with scored blocks and uncertainty discipline).
- **Summary Report**: `research/ab-eval/out/test_v2_real.summary.md`

## Key Improvements
1. **Specimen v2**: Higher resolution (1024x1024) and deterministic layout with character coverage and micro-tell strips (legibility pairs and contrast strips).
2. **Schema v2**: 
   - Moved from free-form lists to **scored blocks** (0.0-1.0) for moods and use-cases.
   - Introduced **Uncertainty Discipline**: Explicit reporting of low-evidence attributes and reasoning.
   - **Machine-Auditable**: Normalized JSON structure ensures downstream consumption reliability.
3. **Model Upgrade**: Routed through `openai/gpt-5.2` via OpenRouter with `include_reasoning: true` for deep visual analysis.

## How to Inspect
1. **Visual Check**: Open `research/ab-eval/out/specimens_v2_toy/Playfair_Display.png` and verify the new layout.
2. **Data Check**: Open `research/ab-eval/out/test_v2_real.jsonl` and inspect the `parsed_json` field for the scored blocks and uncertainty reasoning.
3. **Runbook**: See `research/ab-eval/TRACK_A_RUNBOOK.md` to reproduce these results.

## Known Caveats
- Some fonts in the toy corpus (e.g., Roboto) have stale URLs in the source JSON; specimen rendering for these will fail until the corpus is refreshed.
- `openai/gpt-5.2` is currently used as the primary vision model; ensure OpenRouter API keys are active.
