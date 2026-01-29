import { createClient } from '@supabase/supabase-js';
import { GoogleGenerativeAI } from "@google/generative-ai";
import { generateEmbedding } from '../src/lib/ai/embeddings';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local', override: true });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
const model = genAI.getGenerativeModel({
  model: "gemini-3-pro-preview",
  generationConfig: { responseMimeType: "application/json" }
});

interface RawFont {
  name: string;
  category: string;
}

interface EnrichedFont extends RawFont {
  description: string;
  tags: string[];
}

async function enrichFontsWithAI(fonts: RawFont[]): Promise<EnrichedFont[]> {
  const prompt = `
    You are a typography expert. I will provide a list of Google Fonts. 
    For EACH font, provide:
    1. A rich description (2 sentences) describing its visual characteristics, history, and best use cases.
    2. A list of 5-8 semantic tags (e.g., "geometric", "friendly", "high-contrast", "display", "coding").
    
    Return a JSON object with a "fonts" array matching the input order.
    
    Input Fonts:
    ${JSON.stringify(fonts)}
  `;

  try {
    const result = await model.generateContent(prompt);
    const response = JSON.parse(result.response.text());
    
    // Merge AI result with original data
    return fonts.map(f => {
      const aiData = response.fonts.find((aiF: any) => aiF.name === f.name);
      return {
        ...f,
        description: aiData?.description || `A popular ${f.category} font.`, 
        tags: aiData?.tags || [f.category]
      };
    });
  } catch (error) {
    console.error("AI Enrichment failed for batch, using fallbacks:", error);
    return fonts.map(f => ({
      ...f,
      description: `A popular ${f.category} font family.`, 
      tags: [f.category]
    }));
  }
}

async function seed() {
  const GOOGLE_FONTS_API_KEY = process.env.GOOGLE_FONTS_API_KEY;
  let rawFonts: RawFont[] = [];

  // 1. Fetch Basic Data
  if (GOOGLE_FONTS_API_KEY) {
    console.log('Fetching fonts from Google Fonts API...');
    try {
      const response = await fetch(`https://www.googleapis.com/webfonts/v1/webfonts?sort=popularity&key=${GOOGLE_FONTS_API_KEY}`);
      const data = await response.json();
      if (data.items) {
        rawFonts = data.items.slice(0, 100).map((f: any) => ({ // Start with top 100 for safety/speed testing
          name: f.family,
          category: f.category,
        }));
      }
    } catch (err) {
      console.error('Error fetching API:', err);
    }
  }

  if (rawFonts.length === 0) {
    console.log('Using mock fonts list...');
    rawFonts = [
      { name: 'Roboto', category: 'sans-serif' },
      { name: 'Playfair Display', category: 'serif' },
      { name: 'Montserrat', category: 'sans-serif' },
      { name: 'Open Sans', category: 'sans-serif' },
      { name: 'Lato', category: 'sans-serif' },
      { name: 'Poppins', category: 'sans-serif' },
      { name: 'Inter', category: 'sans-serif' },
      { name: 'Oswald', category: 'sans-serif' },
      { name: 'Raleway', category: 'sans-serif' },
      { name: 'Ubuntu', category: 'sans-serif' },
      { name: 'Merriweather', category: 'serif' },
      { name: 'Lora', category: 'serif' },
      { name: 'PT Serif', category: 'serif' },
      { name: 'Crimson Text', category: 'serif' },
      { name: 'Abril Fatface', category: 'display' },
      { name: 'Bebas Neue', category: 'display' },
      { name: 'Roboto Mono', category: 'monospace' },
      { name: 'Fira Code', category: 'monospace' },
      { name: 'Caveat', category: 'handwriting' },
      { name: 'Pacifico', category: 'handwriting' }
    ];
  }

  console.log(`Starting enrichment for ${rawFonts.length} fonts...`);

  // 2. Process in Batches
  const BATCH_SIZE = 10;
  for (let i = 0; i < rawFonts.length; i += BATCH_SIZE) {
    const batch = rawFonts.slice(i, i + BATCH_SIZE);
    console.log(`Processing batch ${i / BATCH_SIZE + 1}...`);

    // A. Enrich with AI
    const enrichedBatch = await enrichFontsWithAI(batch);

    // B. Generate Embeddings & Upsert
    for (const font of enrichedBatch) {
      try {
        // Create a rich context string for the embedding
        const contextString = `Name: ${font.name}. Category: ${font.category}. Tags: ${font.tags.join(", ")}. Description: ${font.description}`;
        
        const embedding = await generateEmbedding(contextString);

        const { error } = await supabase
          .from('fonts')
          .upsert({
            name: font.name,
            category: font.category,
            description: font.description,
            tags: font.tags,
            embedding: embedding
          }, { onConflict: 'name' });

        if (error) throw error;
        process.stdout.write('.'); // Progress dot
      } catch (err) {
        console.error(`\n❌ Failed to seed ${font.name}:`, err);
      }
    }
    console.log('\nBatch complete.');
    // Small delay to avoid rate limits
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  console.log('Seeding complete!');
}

seed();