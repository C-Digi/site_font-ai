



   1. Get a Google Fonts API Key from the Google Cloud Console
      (https://console.cloud.google.com/).
   2. Add GOOGLE_FONTS_API_KEY=your_key to your .env.local.

   3. Run the SQL migration in supabase/migrations/004_add_source_column.sql.
   4. Run npx tsx scripts/seed-fonts.ts to build your massive, multi-source font library.

---




UI - find examples
add a popup modal for each font after clicking the card, with a larger preview area and full-featured preview options


---



@/supabase/migrations/005_add_files_column.sql 

@/scripts/seed-fonts.ts 

30 fonts are hardcoded - is this all the db will have? 
explain to me:
- our strategy for seeding fonts
- our sources for fonts
- how many are expected to be seeded
- what factors/information go into the embeddings for each font 
- the strategy for in-production
  - RAG / LLM logic
  - RAG process
  - LLM input/output



is all of this fully implemented? there was a session interruption and I am unsure if any gaps were left. 

font.source - is there any value to using this specific field for embedding? if not then remove it as an embedding factor. 

are we already getting and saving in the db a field for each font to use as a direct download link?  
if so do we have any detection or handling (e.g. UX, backend dev notification like sentry/email or otherwise) of broken/outdated links? 

when similarity > 0.95
- what is the user-facing response in the chat window - is it the previously used LLM response verbatim? 
- for continued messages in the chat after this, are the cache-responses included in the chat session history for the LLM to reference later in the conversation?


---

- hybrid web-scrape:
  - https://gemini.google.com/app/f08332b6047a2dd1

include in rag factors
- visual attributes, e.g., `fonts with a large x-height and open counters for low-legibility environments`


---

https://qwen.ai/blog?id=qwen3-vl-embedding
https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B
investigate if implementing this over our current rag embedding method would be an improvement, e.g. instead of using the only the ai-generated description to feed embedding model, use also a rendered image of full alphanumeric set plus a pangram.
also - can this embedding be done locally on 2x rtx 3090's with nvlink? 








## Visual Identity
- https://gemini.google.com/app/2ad7e25f4747f6db
- 

Logo - type-hype.com
"C:\Users\Casey\CloudStorage\TypeHype\Logos\logo_01\logo-typehype_01-darkmode.png"
"C:\Users\Casey\CloudStorage\TypeHype\Logos\logo_01\logo-typehype_01-lightmode.png"

light/dark mode

---

## add features


if preview text empty, have AI insert a relevant string

add a dismissable banner: `Leaving this page or closing the tab will clear the chat history.`

Favorites
- add favorites buttons on font cards 
- add a RH sidebar with Favs list


add a slow-scrolling looping list of suggested prompts below the chat input box, clickable to input to the chat
- subtly elegant wedding invitation
- modern minimalist tech blog
- kids halloween party flyer 
- playful children's book
- boho-chic wall art
- retro 1980s arcade game
- prohibition-era speak-easy
- vintage circus poster
- sleek corporate powerpoint


add a button to open a modal which shows the entire alphanumeric set (upper, lower, numbers, symbols, etc)



example/competition:
https://www.myfonts.com/pages/ai-search
- no free fonts, no free filter
- 



--text: #071313;
--background: #effbfb;
--primary: #30dfdc;
--secondary: #7bf4f2;
--accent: #4ffcf7;

--text: #09130e;
--background: #f1faf6;
--primary: #47cd92;
--secondary: #8be8bf;
--accent: #62eaae;


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

--text: #050708;
--background: #f5f9fb;
--primary: #33a2d2;
--secondary: #80d0f2;
--accent: #48c7fe;

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



