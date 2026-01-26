## FEATURE
- **AI-Powered Font Exploration**: A Next.js (App Router) web application allowing users to discover fonts via natural language (e.g., "modern UI vibe").
- **RAG-Enhanced Performance (Supabase Vector)**: 
    - Uses Supabase Vector to cache and reuse results when queries exceed a "Balanced" semantic threshold.
    - **Embedding Model**: OpenRouter `qwen/qwen3-embedding-8b`.
    - **AI Model**: `google/gemini-2.5-flash-lite-preview-09-2025` handles unique requests when cache misses occur, with results saved to the vector cache.
    - **Developer Control**: Hidden setting for adjusting the semantic threshold.
- **Monetization & Growth**:
    - **Free Tier**: 5 searches/day, 15/week.
    - **Guest Mode**: Reduced limits for unauthenticated users, enforced via IP-based tracking and FingerprintJS.
    - **Credit System**: Bundle-based refills (e.g., $5 for 50, $10 for 150) via **Lemon Squeezy**. No subscriptions.
    - **Donations**: Integrated link to **BuyMeACoffee.com**.
- **Advanced Filtering**: UI filters for Price (Free/Paid), License (OFL/Commercial), and Category (Serif/Sans/Display), operating independently of AI search.
- **Dynamic UI**: 
    - Chat-like interface with AI responses.
    - Font list updates with animated transitions and "Load More" appending.
    - **Optional Toggle**: User-controlled font pairing suggestions.

## DOCUMENTATION
- **Next.js App Router**: [https://nextjs.org/docs](https://nextjs.org/docs)
- **Supabase (Auth/DB/Vector)**: [https://supabase.com/docs](https://supabase.com/docs)
- **Lemon Squeezy API**: [https://docs.lemonsqueezy.com/api](https://docs.lemonsqueezy.com/api)
- **OpenRouter API**: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- **Google Fonts API**: [https://developers.google.com/fonts/docs/developer_api](https://developers.google.com/fonts/docs/developer_api)
- **Gemini 2.5 Flash Lite**: [https://ai.google.dev/models/gemini](https://ai.google.dev/models/gemini)

## OTHER CONSIDERATIONS
- **User Perception**: The RAG/caching layer must be invisible; users should perceive all results as "live" AI generation.
- **Rate Limiting**: Robust tracking for unauthenticated users (IP + FingerprintJS) vs. Supabase Auth for paid users.
- **Credit Management**: Secure handling of Lemon Squeezy webhooks for credit fulfillment.
- **SEO & Performance**: Fast loading of font previews and responsive design using Tailwind CSS.
- **License Filtering**: Ensure the font list update respects the selected license filters (OFL vs Commercial).
