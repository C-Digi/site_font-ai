import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";
import { ChatMessage } from "@/lib/types";
import { supabase } from "@/lib/supabase";
import { generateEmbedding } from "@/lib/ai/embeddings";
import { enqueueSeedJob } from "@/lib/jobs";
import { getRetrievalStrategy } from "@/lib/config/retrieval";
import { applyIntervention } from "@/lib/retrieval/intervention";
import * as dotenv from "dotenv";

dotenv.config({ path: ".env.local", override: true });

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");
const model = genAI.getGenerativeModel({
  model: "gemini-2.0-flash-lite",
});


const SYSTEM_PROMPT = `You are a typography expert and font discovery assistant. 
You will be provided with a user request and some relevant font context from our database.
Your job is to recommend the best fonts from the context or your general knowledge that fit the user's request.

Strictly return JSON in the following format:
{
  "reply": "string (a concise, helpful reply, max 15 words)",
  "fonts": [
    {
      "name": "Exact Font Name",
      "desc": "Short description of why this font fits the request (max 10 words)",
      "category": "serif | sans-serif | display | handwriting | monospace",
      "tags": ["tag1", "tag2", "tag3"],
      "source": "Google Fonts | Fontsource | Fontshare"
    }
  ]
}
Provide at least 16-24 fonts to allow for pagination. 
Only suggest real fonts available on Google Fonts, Fontsource, or Fontshare.
Do not include any markdown formatting (like code blocks) in your response, just the raw JSON string.`;

export async function POST(req: Request) {
  try {
    const { message, history } = await req.json();

    if (!process.env.GEMINI_API_KEY) {
      return NextResponse.json(
        { error: "Gemini API Key not configured" },
        { status: 500 }
      );
    }

    // 1. Generate Embedding for the query
    console.log("Generating embedding for query...");
    const embedding = await generateEmbedding(message);

    // 2. Check Semantic Cache
    console.log("Checking semantic cache...");
    const { data: cacheData, error: cacheError } = await supabase.rpc("match_searches", {
      query_embedding: embedding,
      match_threshold: 0.95, // High threshold for cache hit
    });

    if (!cacheError && cacheData && cacheData.length > 0) {
      console.log("Semantic cache hit!");
      return NextResponse.json(cacheData[0].response_json);
    }

    // 3. RAG: Retrieve similar fonts
    console.log("Performing RAG retrieval...");
    const { data: fontsData, error: fontsError } = await supabase.rpc("match_fonts", {
      query_embedding: embedding,
      match_threshold: 0.5,
      match_count: 20,
    });

    // 3.5. Apply retrieval strategy intervention
    const strategy = getRetrievalStrategy();
    console.log(`[retrieval] strategy=${strategy}`);

    let processedFontsData = fontsData;
    if (strategy === 'p5_07a' && fontsData && fontsData.length > 0) {
      const interventionResults = applyIntervention(fontsData, message);
      // Map back to original shape with adjusted confidence for downstream use
      processedFontsData = interventionResults.map(r => ({
        ...r,
        confidence: r.adjustedConfidence,
      }));
    }

    let context = "";
    if (processedFontsData && processedFontsData.length > 0) {
      context = "Relevant fonts from our database:\n" + 
        processedFontsData.map((f: any) => `- ${f.name} (${f.category}) [Source: ${f.source}]: ${f.description} [Tags: ${f.tags?.join(", ")}]`).join("\n");
    }

    const chatSession = model.startChat({
      history: history.map((msg: ChatMessage) => ({
        role: msg.role === "user" ? "user" : "model",
        parts: [{ text: msg.text }],
      })),
      generationConfig: {
        responseMimeType: "application/json",
      },
    });

    const prompt = `${SYSTEM_PROMPT}\n\n${context}\n\nUser Request: ${message}`;

    const result = await chatSession.sendMessage(prompt);
    const responseText = result.response.text();
    
    try {
      const data = JSON.parse(responseText);

      // Enrich AI results with database metadata (files, tags, actual source)
      if (data.fonts && processedFontsData) {
        data.fonts = data.fonts.map((aiFont: any) => {
          const dbFont = processedFontsData.find((df: any) => df.name.toLowerCase() === aiFont.name.toLowerCase());
          if (dbFont) {
            return {
              ...aiFont,
              tags: dbFont.tags || aiFont.tags,
              source: dbFont.source || aiFont.source,
              files: dbFont.files || {}
            };
          }
          return aiFont;
        });
      }

      // 4. Progressive Seeding (JIT) - Enqueue for background processing
      if (data.fonts && data.fonts.length > 0) {
        // We don't await this to keep the response fast
        (async () => {
          try {
            // Get list of unique font names suggested by AI
            const uniqueFontNames = Array.from(new Set(data.fonts.map((f: any) => f.name)));
            
            // Bulk check existence to minimize DB roundtrips
            const { data: existingFonts } = await supabase
              .from("fonts")
              .select("name")
              .in("name", uniqueFontNames);
            
            const existingNames = new Set(existingFonts?.map(f => f.name.toLowerCase()) || []);
            
            for (const font of data.fonts) {
              if (!existingNames.has(font.name.toLowerCase())) {
                console.log(`Enqueuing JIT seed job for: ${font.name}`);
                await enqueueSeedJob({
                  font_name: font.name,
                  source: font.source || "Google Fonts",
                  source_payload: {
                    category: font.category,
                    tags: font.tags,
                    description: font.desc,
                  },
                  priority: 1, // Higher priority for JIT jobs
                });
              }
            }
          } catch (err) {
            console.error("Progressive Seeding Enqueue Error:", err);
          }
        })();
      }
      // 5. Cache the search result
      console.log("Caching search result...");
      try {
        const { error: cacheError } = await supabase.from("searches").insert({
          query_text: message,
          embedding: embedding,
          response_json: data,
        });
        if (cacheError) console.error("Cache Insert Error:", cacheError);
      } catch (err) {
        console.error("Cache Insert Error (exception):", err);
      }

      return NextResponse.json(data);
    } catch (parseError) {
      console.error("Failed to parse AI response. Raw text:", responseText);
      return NextResponse.json(
        { error: "Invalid AI response format", raw: responseText },
        { status: 500 }
      );
    }
  } catch (error: any) {
    console.error("Search API Error Details:", error);
    return NextResponse.json(
      { error: error.message || "Internal Server Error", stack: error.stack },
      { status: 500 }
    );
  }
}
