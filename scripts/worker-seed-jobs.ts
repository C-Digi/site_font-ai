import * as dotenv from 'dotenv';
import { claimSeedJob, completeSeedJob, failSeedJob } from '../src/lib/jobs';
import { generateB2Embedding } from '../src/lib/ai/embeddings';
import { supabase } from '../src/lib/supabase';
import { GoogleGenerativeAI } from "@google/generative-ai";

dotenv.config({ path: '.env.local', override: true });

const POLL_INTERVAL = parseInt(process.env.JIT_QUEUE_POLL_INTERVAL_MS || '5000', 10);
const WORKER_ENABLED = process.env.WORKER_ENABLED !== 'false';
const WORKER_ID = `worker-${Math.random().toString(36).substring(2, 9)}`;

const stats = {
  claimed: 0,
  completed: 0,
  failed: 0,
  retried: 0
};

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");
const aiModel = genAI.getGenerativeModel({
  model: "gemini-3-pro-preview",
  generationConfig: { responseMimeType: "application/json" }
});

async function validateUrl(url: string): Promise<boolean> {
  try {
    const res = await fetch(url, { method: 'HEAD' });
    return res.ok;
  } catch {
    return false;
  }
}

async function enrichFontWithAI(fontName: string, category: string, source: string): Promise<{ description: string, tags: string[] }> {
  const prompt = `
    You are a typography expert. Provide details for the font "${fontName}" from ${source}.
    Provide:
    1. A rich description (2 sentences) describing its visual characteristics, history, and best use cases.
    2. A list of 5-8 semantic tags (e.g., "geometric", "friendly", "high-contrast", "display", "coding").
    
    Return a JSON object:
    {
      "description": "string",
      "tags": ["tag1", "tag2", ...]
    }
  `;

  try {
    const result = await aiModel.generateContent(prompt);
    const text = result.response.text();
    const cleanJson = text.replace(/^```json\n?|\n?```$/g, '');
    return JSON.parse(cleanJson);
  } catch (error) {
    console.error(`AI Enrichment failed for ${fontName}:`, error);
    return {
      description: `A popular ${category} font family from ${source}.`,
      tags: [category]
    };
  }
}

async function processJob() {
  // Snapshot queue depth
  const { count: pendingCount } = await supabase
    .from('seed_jobs')
    .select('*', { count: 'exact', head: true })
    .eq('status', 'pending');

  console.log(`[${WORKER_ID}] Stats: ${stats.completed} done, ${stats.failed} failed, ${stats.retried} retried. Queue depth: ${pendingCount || 0}`);
  console.log(`[${WORKER_ID}] Polling for jobs...`);
  
  const { data: job, error: claimError } = await claimSeedJob(WORKER_ID);
  
  if (claimError) {
    console.error(`[${WORKER_ID}] Error claiming job:`, claimError);
    return;
  }
  
  if (!job) {
    console.log(`[${WORKER_ID}] No jobs found.`);
    return;
  }

  stats.claimed++;
  if (job.attempts > 1) stats.retried++;
  
  console.log(`[${WORKER_ID}] Processing job ${job.id} for font: ${job.font_name} (Attempt ${job.attempts})`);
  
  try {
    // 1. Resolve Font Data
    const { data: existingFont } = await supabase
      .from('fonts')
      .select('*')
      .eq('name', job.font_name)
      .single();
    
    let fontData = existingFont;
    
    if (!fontData) {
      console.log(`[${WORKER_ID}] Font ${job.font_name} not found in DB, enriching...`);
      const payload = job.source_payload || {};
      const aiData = await enrichFontWithAI(
        job.font_name, 
        payload.category || 'sans-serif', 
        job.source
      );
      
      fontData = {
        name: job.font_name,
        category: payload.category || 'sans-serif',
        description: payload.description || aiData.description,
        tags: payload.tags || aiData.tags,
        source: job.source,
        files: payload.files || {}
      };
    }

    // 2. Validate URLs if present
    if (fontData.files && Object.values(fontData.files).length > 0) {
      const firstUrl = Object.values(fontData.files)[0] as string;
      if (typeof firstUrl === 'string' && firstUrl.startsWith('http')) {
        const isValid = await validateUrl(firstUrl);
        if (!isValid) {
          throw new Error(`Invalid file URL: ${firstUrl}`);
        }
      }
    }

    // 3. Generate B2 Embedding
    const contextString = `Name: ${fontData.name}. Category: ${fontData.category}. Tags: ${fontData.tags?.join(", ")}. Description: ${fontData.description}`;
    console.log(`[${WORKER_ID}] Generating B2 embedding for ${job.font_name}...`);
    
    const embedding = await generateB2Embedding({ text: contextString });

    // 4. Upsert/Update Font Record
    const { error: upsertError } = await supabase
      .from('fonts')
      .upsert({
        name: fontData.name,
        category: fontData.category,
        description: fontData.description,
        tags: fontData.tags,
        source: fontData.source,
        files: fontData.files,
        embedding: embedding,
        updated_at: new Date().toISOString()
      }, { onConflict: 'name' });

    if (upsertError) throw upsertError;

    // 5. Complete Job
    const { error: completeError } = await completeSeedJob(job.id);
    if (completeError) throw completeError;

    stats.completed++;
    console.log(`[${WORKER_ID}] Successfully processed ${job.font_name}`);
  } catch (err: any) {
    stats.failed++;
    console.error(`[${WORKER_ID}] Job ${job.id} failed:`, err);
    const { error: failError } = await failSeedJob(job.id, err.message || 'Unknown error');
    if (failError) console.error(`[${WORKER_ID}] Error marking job as failed:`, failError);
  }
}

async function run() {
  if (!WORKER_ENABLED) {
    console.log(`[${WORKER_ID}] Worker is disabled via WORKER_ENABLED env var.`);
    return;
  }
  console.log(`[${WORKER_ID}] Worker started. Poll interval: ${POLL_INTERVAL}ms`);
  
  while (true) {
    await processJob();
    await new Promise(resolve => setTimeout(resolve, POLL_INTERVAL));
  }
}

run().catch(err => {
  console.error("Worker crashed:", err);
  process.exit(1);
});
