import { createClient } from '@supabase/supabase-js';
import { GoogleGenerativeAI } from "@google/generative-ai";
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local', override: true });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
const embedModel = genAI.getGenerativeModel({ model: "embedding-001" });

async function seed() {
  console.log('Fetching Google Fonts...');
  // You would typically fetch from: 
  // https://www.googleapis.com/webfonts/v1/webfonts?key=${GOOGLE_FONTS_API_KEY}
  
  const mockFonts = [
    { name: 'Roboto', category: 'sans-serif', description: 'Modern, geometric yet friendly. Great for readability.' },
    { name: 'Playfair Display', category: 'serif', description: 'Elegant, high-contrast serif inspired by the Enlightenment.' },
    { name: 'Montserrat', category: 'sans-serif', description: 'Clean, urban geometric typeface with a Spanish vibe.' },
    // Add more here or fetch from API
  ];

  for (const font of mockFonts) {
    console.log(`Generating embedding for ${font.name}...`);
    
    try {
      const result = await embedModel.embedContent(`${font.name} ${font.category} ${font.description}`);
      const embedding = result.embedding.values;

      const { error } = await supabase
        .from('fonts')
        .upsert({
          name: font.name,
          category: font.category,
          description: font.description,
          embedding: embedding
        }, { onConflict: 'name' });

      if (error) throw error;
      console.log(`✅ Seeded ${font.name}`);
    } catch (err) {
      console.error(`❌ Failed to seed ${font.name}:`, err);
    }
  }

  console.log('Seeding complete!');
}

seed();
