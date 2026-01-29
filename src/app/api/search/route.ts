import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";
import { ChatMessage } from "@/lib/types";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");
const model = genAI.getGenerativeModel({
  model: "gemini-2.0-flash-exp", // Using latest available or specified
});

const SYSTEM_PROMPT = `You are a typography expert and font discovery assistant. 
Strictly return JSON in the following format:
{
  "reply": "string (a concise, helpful reply, max 15 words)",
  "fonts": [
    {
      "name": "Exact Google Font Name",
      "desc": "Short description of why this font fits the request (max 10 words)",
      "category": "serif | sans-serif | display | handwriting | monospace"
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

    const chatSession = model.startChat({
      history: history.map((msg: ChatMessage) => ({
        role: msg.role === "user" ? "user" : "model",
        parts: [{ text: msg.text }],
      })),
      generationConfig: {
        responseMimeType: "application/json",
      },
    });

    // We can also use system instruction if supported by the model version
    // but for flash-preview we often include it in the prompt or use the new systemInstruction field
    const prompt = `${SYSTEM_PROMPT}\n\nUser Request: ${message}`;
    
    const result = await chatSession.sendMessage(prompt);
    const responseText = result.response.text();

    try {
      const data = JSON.parse(responseText);
      return NextResponse.json(data);
    } catch (parseError) {
      console.error("Failed to parse AI response:", responseText);
      return NextResponse.json(
        { error: "Invalid AI response format" },
        { status: 500 }
      );
    }
  } catch (error: any) {
    console.error("Search API Error:", error);
    return NextResponse.json(
      { error: error.message || "Internal Server Error" },
      { status: 500 }
    );
  }
}
