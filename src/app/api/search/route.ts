import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";
import { ChatMessage } from "@/lib/types";
import { supabase } from "@/lib/supabase";
import { generateEmbedding } from "@/lib/ai/embeddings";
import * as dotenv from "dotenv";

dotenv.config({ path: ".env.local", override: true });

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");
const model = genAI.getGenerativeModel({
  model: "gemini-3-pro-preview",
});


const SYSTEM_PROMPT = `You are a typography expert and font discovery assistant. 
You will be provided with a user request and some relevant font context from our database.
Your job is to recommend the best fonts from the context or your general knowledge that fit the user's request.

Strictly return JSON in the following format:
{
  "reply": "string (a concise, helpful reply, max 15 words)",
  "fonts": [
    {
      "name": "Exact Google Font Name",
      "desc": "Short description of why this font fits the request (max 10 words)",
      "category": "serif | sans-serif | display | handwriting | monospace",
      "tags": ["tag1", "tag2", "tag3"]
    }
  ]
}
Provide at least 16-24 fonts to allow for pagination. 
Only suggest real fonts available on Google Fonts.
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

    let context = "";
    if (fontsData && fontsData.length > 0) {
      context = "Relevant fonts from our database:\n" + 
        fontsData.map((f: any) => `- ${f.name} (${f.category}): ${f.description} [Tags: ${f.tags?.join(", ")}]`).join("\n");
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

      // 4. Progressive Seeding (JIT)
      // Check if suggested fonts exist in our DB, if not, seed them in the background
      if (data.fonts && data.fonts.length > 0) {
        // We don't await this to keep the response fast
        (async () => {
          try {
            await Promise.all(data.fonts.map(async (font: any) => {
              try {
                const { data: existing } = await supabase
                  .from("fonts")
                  .select("name")
                  .eq("name", font.name)
                  .maybeSingle();

                if (!existing) {
                  console.log(`Lazy seeding missing font: ${font.name}`);
                  const tags = font.tags || [font.category];
                  const fontEmbedding = await generateEmbedding(`${font.name} ${font.category} ${tags.join(" ")} ${font.desc}`);
                  const { error: insertError } = await supabase.from("fonts").insert({
                    name: font.name,
                    category: font.category,
                    description: font.desc,
                    tags: tags,
                    embedding: fontEmbedding
                  });
                  if (insertError) throw insertError;
                }
              } catch (err) {
                console.error(`Failed to lazy seed ${font.name}:`, err);
              }
            }));
          } catch (err) {
            console.error("Progressive Seeding Error:", err);
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
