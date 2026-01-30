



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




Logo - type-hype.com

UI revamp

light/dark mode







## Address Options 

type-hype.com

find-a-font.com
tip-tap-type.com
font-fetcher.com
font-fetch.com




