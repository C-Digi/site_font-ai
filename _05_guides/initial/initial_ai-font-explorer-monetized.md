## FEATURE
- **AI-Powered Font Exploration**: A web application that allows users to discover fonts using natural language descriptions (e.g., "modern UI vibe", "elegant serif for wedding").
- **RAG-Enhanced Performance (Supabase Vector)**: Implements Retrieval-Augmented Generation (RAG) using Supabase Vector to cache and reuse results when queries exceed a semantic threshold. AI (Gemini) is used as a fallback for unique requests, with results then stored in the vector cache.
- **Monetization & Growth**:
    - **Free Tier**: 5 searches per day, 15 per week.
    - **Credit System**: Bundle-based credit refills (e.g., $5 for 50 credits, $10 for 150 credits). No recurring subscriptions.
    - **Donations**: "Buy me a coffee" integration for additional support.
- **Advanced Filtering**: Independent UI filters for price (free/paid), license type (Free for Personal Use, Free for Commercial Use), and category, operating independently of the AI search.
- **Dynamic UI**: Real-time font list updates and AI-generated responses in a chat-like interface. The AI response includes both a user-facing message and a structured font list update.

## EXAMPLES
- **Pattern 1**: [To be created] Semantic similarity caching logic using Supabase Vector and pgvector.
- **Pattern 2**: [To be created] Credit-based usage tracking logic with daily (5) and weekly (15) limits stored in Supabase/PostgreSQL.

## DOCUMENTATION
- **Google Fonts API**: [https://developers.google.com/fonts/docs/developer_api](https://developers.google.com/fonts/docs/developer_api)
- **Gemini API**: [https://ai.google.dev/docs](https://ai.google.dev/docs)
- **Supabase Vector**: [https://supabase.com/docs/guides/ai](https://supabase.com/docs/guides/ai)
- **Supabase Auth & Database**: [https://supabase.com/docs/guides/database](https://supabase.com/docs/guides/database)

## OTHER CONSIDERATIONS
- **User Perception**: The RAG/caching layer must be invisible; users should perceive all results as "live" AI generation.
- **Rate Limiting**: Robust tracking of daily/weekly limits for free users using Supabase functions or middleware.
- **Credit Management**: Secure handling of credit purchases and consumption.
- **SEO & Performance**: Fast loading of font previews and responsive design using Tailwind CSS.
- **License Filtering**: Ensure the font list update respects the selected license filters (Personal vs Commercial).

---

## Refinement Survey (Comprehensive)

To finalize the technical architecture and business logic, please provide answers to the following:

*   **What is the preferred frontend framework for this project?**
    > * Next.js (App Router, React Server Components)

*   **Which payment provider should handle the credit refills and "Buy me a coffee" integration?**
    > * Lemon Squeezy (Handles tax/MoR, good for simple products)

*   **Which embedding model should be used for the RAG semantic threshold?**
    > * OpenRouter qwen/qwen3-embedding-8b

*   **How should the "semantic threshold" for RAG be determined?**
    > * Balanced (Reuse for similar vibes/keywords)

*   **What is the preferred method for "Buy me a coffee" integration?**
    > * Simple external link to Buymeacoffee.com

*   **Should the application support user accounts/login?**
    > * Optional (Guest mode for free tier, Supabase Auth for paid)
        - reduced free-tier limits when not signed in

*   **How should the font list update be handled in the UI?**
    > * Animated transition/filtering
        AND
    > * "Load More" style appending to current results

---

## Refinement Survey (Phase 2)

To further refine the technical implementation, please provide answers to the following questions:

*   **How should the semantic threshold for RAG be determined?**
    > * User-adjustable (hidden developer setting)

*   **What is the preferred tech stack for the frontend and backend?**
    > * Next.js (App Router) + Supabase (Auth/DB/Edge Functions)

*   **How should the "Buy me a coffee" and credit refills be handled?**
    > * lemonsqueezy (for credits) + BuyMeACoffee.com link

*   **What specific "common filters" should be prioritized in the UI?**
    > * Price (Free/Paid), License (OFL/Commercial), Category (Serif/Sans/Display)

*   **How should the 5-per-day/15-per-week limits be enforced for unauthenticated users?**
    > * IP-based tracking 
        OR
    > * FingerprintJS / Browser fingerprinting
        YOUR CHOICE

*   **Should the AI response include font pairing suggestions?**
    > * Optional toggle for the user