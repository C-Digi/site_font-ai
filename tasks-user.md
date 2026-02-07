# Production Rollout: B2 (Qwen3-VL)
- SSoT Location: [`research/prod-rollout/`](research/prod-rollout/)
- Status: Initialized (Week 1 Prep)
- Next: Implement B2 embedding logic & JIT queue.

---


- fast search
- vibe search
- ai assist


## A/B testing


the test queries used in previous testing were quite simple - 
  1. Category Proxies (q_001 to q_010): These test standard font categories and styles:
    - serif fonts, sans-serif fonts, display fonts, handwriting fonts, monospace fonts.
    - Combined descriptors like elegant serif, modern sans-serif, decorative display, cursive style, and fixed-width
   coding font.
  2. Subset Proxies (q_011 to q_015): These test multi-language/script support:
    - cyrillic support, greek support, vietnamese language support, korean fonts, and japanese fonts.
  - we should do another round of testing with more complex queries to validate the results hold for more complex queries as well
  - consider if we should still bother testing A variant, or if we should also try additional variants / methods






## Next
research\prod-rollout\PHASE-0-rag-core-ai-assist-product-plan.md

research\prod-rollout\PHASE-A-query-suggestion-chips-plan.md

- we also still need to implement:
  - payment system
  - user auth
  - other core features?
add these in the plan but keep them high-level




### AI 

- testing
  - if using Hybrid embedding method, test
    - 'inherent knowledge' test for LLM models, for model selection of font-descriptor seeding
      - have each LLM, single response, list all known, verifiable font names, a json file, each incl some basic characterics about it, so we can run it through ran and quantify results from each LLM and see which has the best inherent font knowledge. 
  - consider what A/B tests we should implement for the AI-assist feature, what metrics to consider, etc.
    - LLM models - performance metrics, speed, cost, etc.
    - system prompt topics
    - others?
- 




## monetization
Free - implement now
  Quick Find: unlimited
  Style Match: limited daily/monthly queries
  Save up to 5 favorites
Pro (Creator) - implement now
  Unlimited Style Match
  Guided Picks (AI assist/refinement)
    - apply tiered rate limiting per-user
  Collections, export/import, share
  NOT 'compare lists'
Team 
 - do not implement now or later









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

