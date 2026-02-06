import * as dotenv from "dotenv";
dotenv.config({ path: ".env.local", override: true });

/**
 * Generate text embeddings using OpenRouter (Fallback/Legacy)
 */
export async function generateTextEmbedding(text: string): Promise<number[]> {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    throw new Error("OPENROUTER_API_KEY is not set");
  }

  const response = await fetch("https://openrouter.ai/api/v1/embeddings", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "qwen/qwen3-embedding-8b",
      input: text,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(`OpenRouter Embedding Error: ${JSON.stringify(error)}`);
  }

  const result = await response.json();
  if (!result.data?.[0]?.embedding) {
    throw new Error(`OpenRouter Embedding Error: No embedding in response: ${JSON.stringify(result)}`);
  }
  return result.data[0].embedding;
}

/**
 * Generate B2 Multimodal Embeddings (Production Default)
 * Supports text-only queries and multimodal (image + text) seeding.
 */
export async function generateB2Embedding(params: { text: string; image?: string }): Promise<number[]> {
  const endpoint = process.env.VL_EMBEDDING_ENDPOINT;
  const apiKey = process.env.VL_EMBEDDING_API_KEY;

  if (!endpoint) {
    throw new Error("VL_EMBEDDING_ENDPOINT is not set");
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      ...(apiKey ? { "Authorization": `Bearer ${apiKey}` } : {}),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(`B2 Embedding Error (Status ${response.status}): ${JSON.stringify(error)}`);
  }

  const result = await response.json();
  // Support both { embedding: [...] } and OpenAI-style { data: [ { embedding: [...] } ] }
  const embedding = result.embedding || result.data?.[0]?.embedding;
  
  if (!embedding || !Array.isArray(embedding)) {
    throw new Error(`B2 Embedding Error: Invalid embedding format in response: ${JSON.stringify(result)}`);
  }

  if (embedding.length !== 4096) {
    console.warn(`Warning: B2 embedding dimension mismatch. Expected 4096, got ${embedding.length}`);
  }

  return embedding;
}

/**
 * Main embedding entry point with robust fallback logic.
 * Defaults to B2 if configured, otherwise falls back to OpenRouter text embeddings.
 */
export async function generateEmbedding(text: string): Promise<number[]> {
  // Try B2 first if endpoint is configured
  if (process.env.VL_EMBEDDING_ENDPOINT) {
    try {
      return await generateB2Embedding({ text });
    } catch (error) {
      console.error("B2 Embedding failed, falling back to text-only:", error);
      // Fall through to text-only
    }
  }

  // Fallback to OpenRouter text-only
  return await generateTextEmbedding(text);
}
