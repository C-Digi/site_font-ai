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
  source: string;
  files: Record<string, string>;
}

interface EnrichedFont extends RawFont {
  description: string;
  tags: string[];
}

async function validateUrl(url: string): Promise<boolean> {
  try {
    const res = await fetch(url, { method: 'HEAD' });
    return res.ok;
  } catch {
    return false;
  }
}

async function enrichFontsWithAI(fonts: RawFont[]): Promise<EnrichedFont[]> {
  const prompt = `
    You are a typography expert. I will provide a list of fonts from various sources. 
    For EACH font, provide:
    1. A rich description (2 sentences) describing its visual characteristics, history, and best use cases.
    2. A list of 5-8 semantic tags (e.g., "geometric", "friendly", "high-contrast", "display", "coding").
    
    Return a JSON object with a "fonts" array matching the input order.
    
    Input Fonts:
    ${JSON.stringify(fonts.map(({ name, category, source }) => ({ name, category, source })))}
  `;

  try {
    const result = await model.generateContent(prompt);
    const text = result.response.text();
    const cleanJson = text.replace(/^```json\n?|\n?```$/g, '');
    const response = JSON.parse(cleanJson);
    
    return fonts.map(f => {
      const aiData = response.fonts.find((aiF: any) => aiF.name === f.name);
      return {
        ...f,
        description: aiData?.description || `A popular ${f.category} font from ${f.source}.`,
        tags: aiData?.tags || [f.category]
      };
    });
  } catch (error) {
    console.error("AI Enrichment failed for batch, using fallbacks:", error);
    return fonts.map(f => ({
      ...f,
      description: `A popular ${f.category} font family from ${f.source}.`,
      tags: [f.category]
    }));
  }
}

async function seed() {
  const GOOGLE_FONTS_API_KEY = process.env.GOOGLE_FONTS_API_KEY;
  let rawFonts: RawFont[] = [];

  // 1. Fetch Google Fonts
  if (GOOGLE_FONTS_API_KEY) {
    console.log('Fetching fonts from Google Fonts API...');
    try {
      const response = await fetch(`https://www.googleapis.com/webfonts/v1/webfonts?sort=popularity&key=${GOOGLE_FONTS_API_KEY}`);
      const data = await response.json();
      if (data.items) {
        const googleFonts = data.items.map((f: any) => ({
          name: f.family,
          category: f.category,
          source: 'Google Fonts',
          files: f.files || {}
        }));
        rawFonts = [...rawFonts, ...googleFonts];
        console.log(`Added ${googleFonts.length} fonts from Google Fonts.`);
      }
    } catch (err) {
      console.error('Error fetching Google Fonts:', err);
    }
  }

  // 2. Fetch Fontsource (Open Source aggregator)
  console.log('Fetching fonts from Fontsource API...');
  try {
    const response = await fetch('https://api.fontsource.org/v1/fonts');
    const data = await response.json();
    if (Array.isArray(data)) {
      // Fontsource list API doesn't include files by default, we'd need to fetch individual font data
      // For speed in this seed, we'll construct the common Fontsource URL pattern if files are missing
      const fontsourceFonts = data.slice(0, 500).map((f: any) => ({
        name: f.family,
        category: f.category || 'sans-serif',
        source: 'Fontsource',
        // Fontsource usually has a standard structure: https://cdn.jsdelivr.net/npm/@fontsource/[id]/files/[id]-latin-400-normal.woff2
        files: f.files || {
          "400": `https://api.fontsource.org/v1/fonts/${f.id}` // Placeholder link to their info page
        }
      }));
      const uniqueFontsource = fontsourceFonts.filter(f => !rawFonts.find(rf => rf.name === f.name));
      rawFonts = [...rawFonts, ...uniqueFontsource];
      console.log(`Added ${uniqueFontsource.length} unique fonts from Fontsource.`);
    }
  } catch (err) {
    console.error('Error fetching Fontsource:', err);
  }

  // 3. Manual Fontshare List
  const fontshareFonts: RawFont[] = [
    { name: 'Satoshi', category: 'sans-serif', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/satoshi" } },
    { name: 'General Sans', category: 'sans-serif', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/general-sans" } },
    { name: 'Sentient', category: 'serif', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/sentient" } },
    { name: 'Zodiak', category: 'serif', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/zodiak" } },
    { name: 'Expose', category: 'display', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/expose" } },
    { name: 'Cabinet Grotesk', category: 'sans-serif', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/cabinet-grotesk" } },
    { name: 'Telma', category: 'display', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/telma" } },
    { name: 'Chillax', category: 'sans-serif', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/chillax" } },
    { name: 'Gambarino', category: 'serif', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/gambarino" } },
    { name: 'Clash Display', category: 'display', source: 'Fontshare', files: { "400": "https://api.fontshare.com/v2/fonts/download/clash-display" } }
  ];
  const uniqueFontshare = fontshareFonts.filter(f => !rawFonts.find(rf => rf.name === f.name));
  rawFonts = [...rawFonts, ...uniqueFontshare];
  console.log(`Added ${uniqueFontshare.length} unique fonts from Fontshare.`);

  if (rawFonts.length === 0) {
    console.log('No fonts fetched, using minimal mock list...');
    rawFonts = [
      { name: 'Roboto', category: 'sans-serif', source: 'Google Fonts', files: {} },
      { name: 'Playfair Display', category: 'serif', source: 'Google Fonts', files: {} }
    ];
  }

  console.log(`Starting enrichment for ${rawFonts.length} total fonts...`);

  // 4. Process in Batches
  const BATCH_SIZE = 10;
  for (let i = 0; i < rawFonts.length; i += BATCH_SIZE) {
    const batch = rawFonts.slice(i, i + BATCH_SIZE);
    console.log(`Processing batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(rawFonts.length / BATCH_SIZE)}...`);

    // A. Filter out fonts already in DB to save on AI costs
    const { data: existingFonts } = await supabase
      .from('fonts')
      .select('name')
      .in('name', batch.map(f => f.name));
    
    const existingNames = new Set(existingFonts?.map(f => f.name) || []);
    const newFonts = batch.filter(f => !existingNames.has(f.name));

    if (newFonts.length === 0) {
      console.log(`Skipping batch ${Math.floor(i / BATCH_SIZE) + 1} (all fonts exist).`);
      continue;
    }

    // B. Enrich with AI
    const enrichedBatch = await enrichFontsWithAI(newFonts);

    // C. Generate Embeddings & Upsert
    for (const font of enrichedBatch) {
      try {
        // Only seed fonts with valid file URLs if they exist
        if (font.files && Object.values(font.files).length > 0) {
          const firstUrl = Object.values(font.files)[0];
          const isValid = await validateUrl(firstUrl);
          if (!isValid) {
            console.log(`\n⚠️ Skipping ${font.name} due to invalid file URL: ${firstUrl}`);
            continue;
          }
        }

        const contextString = `Name: ${font.name}. Category: ${font.category}. Tags: ${font.tags.join(", ")}. Description: ${font.description}`;
        
        const embedding = await generateEmbedding(contextString);

        const { error } = await supabase
          .from('fonts')
          .upsert({
            name: font.name,
            category: font.category,
            description: font.description,
            tags: font.tags,
            source: font.source,
            files: font.files,
            embedding: embedding
          }, { onConflict: 'name' });

        if (error) throw error;
        process.stdout.write('.');
      } catch (err) {
        console.error(`\n❌ Failed to seed ${font.name}:`, err);
      }
    }
    console.log('\nBatch complete.');
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  console.log('Seeding complete!');
}
seed();