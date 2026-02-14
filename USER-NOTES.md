

---



---
.lightspec\progress.md
2026-02-14T01-44-09_handoff.md

---
---
---


what does next phase look like?
and when should we do other components of the app like embeddings, user-facing AI, build up the UI, auth, payment system, etc?? 
what file if any is the SSoT for these plans?


do HITL check of latest test data
- use a yes/no/skip scoring method. i will choose to 'skip' some edge cases where i can see decisions going either way acceptably. 
`research\ab-eval\human_labeling_medium_v1.html` as example





## VL-embedding value
now that we are using VL to generate good data to feed to RAG
- test and compare if the VL-embedding adds any value over the text-only version, if its worth still using












## Links

research\ab-eval\DECISIONS.md
research\prod-rollout\DECISIONS.md
research\prod-rollout\PHASE-0-rag-core-ai-assist-product-plan.md
research\prod-rollout\PHASE-A-query-suggestion-chips-plan.md





## AI-Assist UX
- consider what A/B tests we should implement for the AI-assist feature, what metrics to consider, etc.
  - LLM models - performance metrics, speed, cost, etc.
  - enhancement/additions to system prompt  
  - others?
- models to test
  - oss-120b
  - google/gemma-3-27b-it




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


## potential later features
- user-selectable attributes to make a 2D visualizer of fonts on a plot, e.g. business vs party on X scale, bold vs thin on Y scale
  - hover or zoom in to see previews of each point/font









## decided against


For those we 'hide' for premium, could we still render the font to preview and entice, but block the download button, name, and any revealing data? 
 - dont do this - its more enticing not seeing them, and risks the locked fonts discouraging them from using/spending


