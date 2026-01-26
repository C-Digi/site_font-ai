"use client";

import { useState, useEffect } from "react";
import { Header } from "./Header";
import { ChatInterface } from "./ChatInterface";
import { Controls } from "./Controls";
import { FontGrid } from "./FontGrid";
import { Font, ChatMessage, SearchResponse } from "@/lib/types";

export default function FontExplorer() {
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [fonts, setFonts] = useState<Font[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("Ready to explore typography.");
  const [previewText, setPreviewText] = useState("The quick brown fox jumps over the lazy dog.");
  const [fontSize, setFontSize] = useState(32);
  const [fontWeight, setFontWeight] = useState(400);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // Initial prompt
  useEffect(() => {
    handleSend("Show me diverse, modern trending fonts for UI design.");
  }, []);

  // Update dynamic font link
  useEffect(() => {
    if (fonts.length > 0) {
      const uniqueNames = Array.from(new Set(fonts.map(f => f.name)));
      const families = uniqueNames
        .map(name => `family=${name.trim().replace(/\s+/g, "+")}:wght@100;200;300;400;500;600;700;800;900`)
        .join("&");
      
      const linkId = "dynamic-google-fonts";
      let link = document.getElementById(linkId) as HTMLLinkElement;
      if (!link) {
        link = document.createElement("link");
        link.id = linkId;
        link.rel = "stylesheet";
        document.head.appendChild(link);
      }
      link.href = `https://fonts.googleapis.com/css2?${families}&display=swap`;
    }
  }, [fonts]);

  const handleSend = async (message: string) => {
    setIsLoading(true);
    setStatus("Thinking...");
    
    // Optimistically add user message
    const newHistory = [...history, { role: "user" as const, text: message }];
    setHistory(newHistory);

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history }),
      });

      if (!response.ok) throw new Error("Search failed");

      const data: SearchResponse = await response.json();
      
      setHistory(prev => [...prev, { role: "model", text: data.reply }]);
      if (data.fonts && data.fonts.length > 0) {
        setFonts(data.fonts);
        setCurrentPage(1);
      }
      setStatus(`✨ ${data.reply}`);
    } catch (error) {
      console.error(error);
      setStatus("Error connecting to AI.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto w-full p-4 md:p-8 flex-1 flex flex-col">
      <Header />
      <ChatInterface
        history={history}
        isLoading={isLoading}
        onSend={handleSend}
        status={status}
      />
      <main className="flex-1 flex flex-col">
        <Controls
          previewText={previewText}
          setPreviewText={setPreviewText}
          fontSize={fontSize}
          setFontSize={setFontSize}
          fontWeight={fontWeight}
          setFontWeight={setFontWeight}
        />
        <FontGrid
          fonts={fonts}
          isLoading={isLoading}
          previewText={previewText}
          fontSize={fontSize}
          fontWeight={fontWeight}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          itemsPerPage={itemsPerPage}
        />
      </main>
    </div>
  );
}
