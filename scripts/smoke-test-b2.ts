import { generateEmbedding, generateB2Embedding } from '../src/lib/ai/embeddings';
import * as dotenv from 'dotenv';
import path from 'path';

// Load from .env.local
dotenv.config({ path: path.resolve(process.cwd(), '.env.local'), override: true });

async function main() {
  console.log("--- B2 Smoke Test ---");
  
  const query = "elegant serif font for a wedding invitation";
  
  console.log(`Testing query: "${query}"`);
  console.log(`Endpoint: ${process.env.VL_EMBEDDING_ENDPOINT || 'NOT SET'}`);
  
  try {
    const embedding = await generateEmbedding(query);
    console.log(`✅ Success! Embedding generated.`);
    console.log(`Dimensions: ${embedding.length}`);
    
    if (embedding.length === 4096) {
      console.log("✅ Dimension match (4096) - B2 is likely active.");
    } else {
      console.log(`⚠️ Dimension is ${embedding.length}. Likely fell back to text-only embedding.`);
    }

    // Try explicit B2 if configured
    if (process.env.VL_EMBEDDING_ENDPOINT) {
      console.log("\nTesting explicit B2 multimodal call...");
      try {
        const b2Emb = await generateB2Embedding({ text: query });
        console.log(`✅ Explicit B2 Success! Dimensions: ${b2Emb.length}`);
      } catch (e: any) {
        console.error(`❌ Explicit B2 call failed: ${e.message}`);
      }
    } else {
      console.log("\nSkipping explicit B2 test (VL_EMBEDDING_ENDPOINT not set)");
    }

    console.log("\n--- Smoke Test Complete ---");
  } catch (error: any) {
    console.error("❌ Smoke test failed:", error.message);
    process.exit(1);
  }
}

main();
