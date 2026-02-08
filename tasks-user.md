# Production Rollout: B2 (Qwen3-VL)
- SSoT Location: [`research/prod-rollout/`](research/prod-rollout/)
- Status: Initialized (Week 1 Prep)
- Next: Implement B2 embedding logic & JIT queue.

---

how can we ground our answer-key properly? 
- my thoughts to scale on our small human-team
  - see my plans for testing/improvements below - 'VL input for text-description' - 'feed each glyph render to the VL model to generate a vision-grounded description'
  - this is intended for A/C hybrid embedding testing, but perhaps we could
    - do this testing first. include human-heavy scoring/ranking/spot-checks
    - determine best-performance (not necessarly same as production, due to cost/speed) VL model
    - use SOTA VL model to generate a sample answer key
    - human-review the answer key
    - use SOTA model to generate full key
    - human spot-check full key
- thoughts? suggestions? ROI?
- alternatives? 
---

research candidate models to use. must include at least 2x qwen3-vl models, they have 8b, 30b, 32b, gguf, fp8, fp16... https://huggingface.co/collections/Qwen/qwen3-vl . must also include gemini-3-flash-preview (recent release) and gemini-2.5-flash-lite-preview-09-2025. GEMINI_API_KEY and OPENROUTER_API_KEY are already populated in root .env - prefer gemini provider but openrouter can be fallback. test 4-6 models total. 


---
## test improvements

### test top-level grounding for scoring
- need manual (human) input
- need clear, streamlined, quantitave scoring method for human to 'score' variations of our scoring method (automated test scoring)
-  `labels.complex.v1.json`, assuming this is SSoT for scoring against
   -  how was this generated - by memory/knowledge of the developer who wrote it?

### text-input for embeddings
- remove font name, it can be misleading/conflicting
- consider appending category value into tags as tag#1 as category is essentially a characteristic, aka tag
- Description
  - remove oem-metadata description, e.g. "A monospace font from Google Fonts."
    - see `research\ab-eval\data\corpus.200.json`
    - no value added, `monospace` should already be a tag/category
  - replace with vision-grounded AI-generated description below


### VL input for text-description (A/C)
- research image/VL models
  - gemini
  - qwen
  - remote SOTA
  - local under 48gb vram
- feed each glyph render to the VL model to generate a vision-grounded description
- full round of testing - basic and complex queries
- compare different models, compare with/without LLM-vision step, quantify production costs for each model to seed db


---

- human-review SSoT
- check deep research options
- test more models 
  - openai/gpt-5.2
  - 

see results from a deep-research session:
@ 


what do you recommend at this point. we are in no rush to get to production. please prioritize improving and validating core-functionality quality through experimentation




to be clear - i do not want it to categorize by name or assign/guess font name -  iwill feed the AI an image of alphabet/number/glyph rendered from a single font (for each font) , AI receives image only plus instructions, target output is visual attributes of the font. 
this info that AI outputs will be used to seed a RAG db for a semantic/vibe font-search - i dont need assistance on that side. only the AI-generation of visual font characteristics based off the rendered font. RAG vector will not get the font-name as they can be misleading.

FasterViT - classifies fonts by family name; it does not directly output descriptive attributes
- not useful to me then
fontclip - characterize a font’s style in semantic terms (e.g. serif, elegant, bold, playful)  .... scores can be turned into tags like “serif: yes, monospace: no, cursive: no, weight: medium, contrast: high, friendly: moderately, special: slashed-zero ”, etc.... 
- sounds perfect
Total Disentanglement - this sounds great, but at scale for 2000+ fonts, would that mean a crazy amt of training ? ref to 'By training on all letters A–Z of a font'




SCOPE CHECK
- vibe search is easy - test to get best models/methods
- characteristic search - needs tons of testing/validation




## Would tag-format, or natural-language description, be better for a RAG db? 
tag-format concept
- list of binary tags, e.g. serif: yes, monospace: no, cursive: no
- list of weighted tags, e.g. warmth: high, contrast: high, friendly: medium...
worth testing? 





## AI-Assist UX
- consider what A/B tests we should implement for the AI-assist feature, what metrics to consider, etc.
  - LLM models - performance metrics, speed, cost, etc.
  - enhancement/additions to system prompt  
  - others?


## Uncategorized

research\prod-rollout\PHASE-0-rag-core-ai-assist-product-plan.md

research\prod-rollout\PHASE-A-query-suggestion-chips-plan.md





## UI Design 

- Current UI is leftover from the MVP. we need to completely redo it from the ground up. use frontend skill.
---

- implement light/dark mode
- our logo uses #00baf0 primarily - use this in the color scheme
---

copy the logos into the codebase and apply them to UI

Logo - type-hype.com
"C:\Users\Casey\CloudStorage\TypeHype\Logos\logo_01\logo-typehype_01-darkmode.png"
"C:\Users\Casey\CloudStorage\TypeHype\Logos\logo_01\logo-typehype_01-lightmode.png"

---

- add a popup modal for each font after clicking the card
  - a large preview area showing the full alphanumeric set (upper, lower, numbers, symbols, etc) plus the preview-text, which can be edited from the modal
  - full-featured preview options in integrated menu, incl any present in the main UI plus more
  - 
---

add a slow-scrolling looping list of suggested prompts below the chat input box, clickable to input to the chat. entire section disappears from view after first chat message is sent by user.
- subtly elegant wedding invitation
- modern minimalist tech blog
- kids halloween party flyer 
- playful children's book
- boho-chic wall art
- retro 1980s arcade game
- prohibition-era speak-easy
- vintage circus poster
- sleek corporate powerpoint

---

- for the preview text input box
  - on page load, have it pre-populated with a relevant string (e.g. "The quick brown fox jumps over the lazy dog." but more unique and interesting).
  - once clicked into the box, the pre-filled text should be automatically deleted so the user doesn't have to manually clear it out.
  - If the user sends the AI a chat message while the preview text input is still empty (not modified by user, preset selected), have AI insert a relevant string

---

Favorites
- add favorites toggle button on font cards
- add a RH collapsible sidebar with Favs list
  - subtle animation when a font is added/removed to favs
  - persist between sessions, even when not signed in


---







add a dismissable banner: `Leaving this page or closing the tab will clear the chat history.`



## analytics
- critical metrics to collect
  - top queries, keywords, patterns, font results, fonts clicked, downloaded, etc



## Possible Color Schemes

--text: #050708;
--background: #f5f9fb;
--primary: #33a2d2;
--secondary: #80d0f2;
--accent: #48c7fe;


--text: #09130e;
--background: #f1faf6;
--primary: #47cd92;
--secondary: #8be8bf;
--accent: #62eaae;


--text: #071313;
--background: #effbfb;
--primary: #30dfdc;
--secondary: #7bf4f2;
--accent: #4ffcf7;


--text: #eaf6f2;
--background: #020303;
--primary: #33c1a0;
--secondary: #187c63;
--accent: #14a380;


--text: #0c1518;
--background: #f0f8fa;
--primary: #49adc5;
--secondary: #98d7e6;
--accent: #64cbe3;

--text: #0c151d;
--background: #f4f8fb;
--primary: #568ac2;
--secondary: #9abcdf;
--accent: #72a2d5;

--text: #0d0f16;
--background: #f3f4f9;
--primary: #5468b3;
--secondary: #a0acdb;
--accent: #7185d2;

--text: #050505;
--background: #f6f9f7;
--primary: #54ab64;
--secondary: #98dda4;
--accent: #6be180;


## Address Options 

type-hype.com

find-a-font.com
tip-tap-type.com
font-fetcher.com
font-fetch.com



## example/competition
https://www.myfonts.com/pages/ai-search
- no free fonts, no free filter
- 



## decided against


For those we 'hide' for premium, could we still render the font to preview and entice, but block the download button, name, and any revealing data? 
 - dont do this - its more enticing not seeing them, and risks the locked fonts discouraging them from using/spending




# Test Variations

[`B2`](research/ab-eval/py/score_all_variants.py:207) uses a real embedding input payload; [`C (alpha=0.5)`](research/ab-eval/py/score_all_variants.py:222) does **not** create new embeddings and therefore has no separate text prompt.

- B2 doc input is built in [`text_desc`](research/ab-eval/py/embed_qwen3_vl_batch.py:60) as:
  - `"Font: {name}. Category: {category}. Tags: {tag1, tag2, ...}."`
- B2 query input is raw query text via [`query_items = [{"text": q["text"]} for q in queries]`](research/ab-eval/py/embed_qwen3_vl_batch.py:87).

Actual example (from corpus):
- Font fields for `Geom` come from [`corpus.200.json`](research/ab-eval/data/corpus.200.json:17) / [`category`](research/ab-eval/data/corpus.200.json:18) / [`tags`](research/ab-eval/data/corpus.200.json:20).
- So B2 text input becomes exactly:
  - `"Font: Geom. Category: sans-serif. Tags: greek, latin, latin-ext."` (from [`text_desc`](research/ab-eval/py/embed_qwen3_vl_batch.py:60))
- If glyph exists, that same item also includes an image path via [`item["image"] = glyph_path`](research/ab-eval/py/embed_qwen3_vl_batch.py:63).

For [`C`](research/ab-eval/py/score_all_variants.py:212):
- C is score fusion only: [`fused_scores = alpha * all_scores["A"] + (1 - alpha) * all_scores["B2"]`](research/ab-eval/py/score_all_variants.py:218).
- So C reuses:
  - A scores from [`all_scores["A"] = cosine_similarity_matrix(a_queries_mtx, a_docs_mtx)`](research/ab-eval/py/score_all_variants.py:201), where A doc text is built as [`context = f"Name: ... Category: ... Tags: ... Description: ..."`](research/ab-eval/py/embed_openrouter_text.py:52).
  - B2 scores from [`all_scores["B2"] = cosine_similarity_matrix(vl_queries, b2_docs)`](research/ab-eval/py/score_all_variants.py:207).

So, short answer: B2 has its own text+image embedding input; C has no new text input, only weighted blending of A and B2 similarity scores.


[`A`](research/ab-eval/py/score_all_variants.py:201) is **text-only** embedding input from [`embed_openrouter_text.py`](research/ab-eval/py/embed_openrouter_text.py:1).

- Doc input template is built in [`context`](research/ab-eval/py/embed_openrouter_text.py:52):
  - `"Name: {font['name']}. Category: {font['category']}. Tags: {', '.join(font['tags'])}. Description: {font['description']}"`
- Query input is raw query text in [`get_embedding(q['text'], api_key)`](research/ab-eval/py/embed_openrouter_text.py:69).
- Embedding model for A is set in [`payload['model'] = 'qwen/qwen3-embedding-8b'`](research/ab-eval/py/embed_openrouter_text.py:26).

Concrete doc example (from [`Geom`](research/ab-eval/data/corpus.200.json:17)):
- `"Name: Geom. Category: sans-serif. Tags: greek, latin, latin-ext. Description: A sans-serif font from Google Fonts."`

Concrete query example (from [`cq_029`](research/ab-eval/data/queries.complex.v1.json:30)):
- `"classic typewriter font"`

Source of `description` in Variant A comes from corpus generation, not per-font prose metadata.

- The field is created in [`build_corpus_google_fonts.py`](research/ab-eval/py/build_corpus_google_fonts.py:115) with a template string based on category.
- That generated value is then stored in [`corpus.200.json`](research/ab-eval/data/corpus.200.json) (example at [`"description": "A sans-serif font from Google Fonts."`](research/ab-eval/data/corpus.200.json:10)).
- Variant A embeds a doc context that includes that field via [`context = f"Name: ... Description: {font['description']}"`](research/ab-eval/py/embed_openrouter_text.py:52).

Implication: in this eval, `description` is synthetic and mostly uniform by category, unless the corpus file is manually enriched later.