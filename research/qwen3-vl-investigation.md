# Investigation: Qwen3-VL-Embedding-8B for site_font-ai

## Overview
The task was to investigate if implementing `Qwen3-VL-Embedding-8B` over the current text-based RAG method would be an improvement.

## The "Visual RAG" Pivot
While the model enables user-facing "Search by Image", its primary value for this project is **Grounding Embeddings in Reality**.

The current method relies on text metadata (tags, categories, descriptions) which are prone to AI hallucinations and manual tagging errors. By switching to `Qwen3-VL-Embedding-8B` and embedding **rendered images** of the fonts, we ensure the search index is based on how the font actually looks.

## Findings

### 1. Eliminating Hallucinations
By rendering a "Visual Fingerprint" (e.g., "Quick brown fox..." + Alphanumeric set) for each font and embedding the resulting image, the vector representation becomes a factual record of the font's design. This removes the "middleman" of text descriptions during the retrieval phase.

### 2. Cross-Modal Semantic Retrieval
`Qwen3-VL-Embedding-8B` maps text and images into the **same vector space**.
- A text query like *"heavy display font with sharp corners"* will map directly to the visual characteristics captured in the font images.
- This is far more robust than matching the text query against potentially incomplete or incorrect text tags.

### 3. Technical Compatibility
- **Dimensions**: Both models support up to **4096 dimensions**. Our current Supabase schema (`vector(4096)`) is already compatible.
- **MRL Support**: Both support Matryoshka Representation Learning, allowing for flexible output dimensions if needed for performance.

### 4. Implementation Requirements
- **Re-embedding**: Because the vector space is different, all existing fonts must be re-embedded. To leverage the VL model, we should embed **images** of the fonts (rendered previews) rather than just metadata strings.
- **Rendering Pipeline**: We would need a utility to render font files into preview images for the embedding process.
- **Cache Invalidation**: The current semantic cache (`searches` table) would need to be cleared.

## Recommendation
**Highly Recommended.**
Switching to `Qwen3-VL-Embedding-8B` solves the fundamental problem of metadata quality. It allows the RAG system to "see" the fonts, creating a search experience that is based on visual reality rather than fallible text descriptions.

---

## Implementation Plan

```yaml
task: Implement "Visual RAG" using Qwen3-VL-Embedding-8B
approach: Ground font embeddings in visual truth by embedding rendered font samples instead of text descriptions.

context_gathered:
  - Current embedding: Text-only Qwen3-Embedding-8B (4096 dims).
  - Proposed model: Qwen3-VL-Embedding-8B (4096 dims, Multimodal).
  - Problem: Text-only descriptions are prone to hallucinations and inaccuracies.

implementation_plan:
  - step: Update `src/lib/ai/embeddings.ts` to use `qwen/qwen3-vl-embedding-8b` and support image/multimodal payloads.
    verification: Test embedding a simple text string vs a base64 image.
    dependencies: Model availability on OpenRouter.

  - step: Develop a "Visual Fingerprint" generator. This script should take a font file and render a standardized image containing uppercase/lowercase letters, numbers, and a pangram ("The quick brown fox...").
    verification: Manually inspect generated images for a variety of font styles.
    dependencies: `canvas` or similar rendering library in Node.js.

  - step: Re-index the database. For each font, generate its visual fingerprint, embed the image, and update the `embedding` column in Supabase.
    verification: Vector similarity search returns visually similar fonts even without tags.
    dependencies: Fingerprint generator.

  - step: Reset semantic cache. Clear the `searches` table as old text-to-text embeddings will no longer align with the new vision-language space.
    verification: `searches` table is cleared.
    dependencies: None

  - step: Refine Search API. Ensure the query generation still uses the same VL model (in text mode) so that natural language queries map correctly to the visual embeddings.
    verification: Queries like "bubbly round font" return correct results without relying on the "bubbly" tag.
    dependencies: Re-indexing.

alternatives_considered:
  - approach: Dual-embedding (keep text model, add vision model separately).
    pros: Keeps high-precision text search.
    cons: Doubles storage and cost; complicates retrieval logic.
    rejected_because: Qwen3-VL-Embedding-8B is designed to be a unified model for both.

validation_strategy:
  - Benchmarking: Compare retrieval accuracy for text queries against the old model.
  - Visual Test: Upload a screenshot of "Inter" and ensure "Inter" or similar sans-serifs are returned.
```

## Open Questions
1. **Model ID**: Confirm the exact model ID for `Qwen3-VL-Embedding-8B` on OpenRouter (it was recently released).
2. **Rendering**: What text should be used for the preview images? (e.g., "The quick brown fox", the font name, or a character set?)
