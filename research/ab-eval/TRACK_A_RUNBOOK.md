# Track A Runbook: Reproducing Quality-First Results

This runbook describes how to execute the Track A pipeline for specimen rendering and description generation.

## Prerequisites
- Python environment with `PIL`, `requests`, `dotenv`.
- Valid `OPENROUTER_API_KEY` in `.env.local`.

## Step 1: Render Specimen v2
To render the upgraded 1024x1024 specimens:

```bash
python research/ab-eval/py/render_specimen_v2.py --corpus research/ab-eval/data/corpus.toy.json --out research/ab-eval/out/specimens_v2_toy
```

## Step 2: Generate Descriptions (Schema v2)
To generate the vision-grounded descriptions using Schema v2 and GPT-5.2:

```bash
python research/ab-eval/py/gen_font_descriptions.py \
  --corpus research/ab-eval/data/corpus.toy.json \
  --glyph-dir research/ab-eval/out/specimens_v2_toy \
  --prompt-template research/ab-eval/py/prompt_v2.txt \
  --models openai/gpt-5.2 \
  --out research/ab-eval/out/test_v2_real.jsonl
```

Note: The script automatically detects `schema_version: 2` if the prompt template name contains `v2`. You can also force it with `--schema-version 2`.

## Step 3: Verify Output
Check the resulting `.jsonl` file and the generated `.summary.md` for performance metrics and extraction quality.
```bash
cat research/ab-eval/out/test_v2_real.jsonl | head -n 2
```
