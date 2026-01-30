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
  const [fontStatuses, setFontStatuses] = useState<Record<string, { renderable: boolean; downloadable: boolean }>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("Ready to explore typography.");
  const [previewText, setPreviewText] = useState("The quick brown fox jumps over the lazy dog.");
  const [fontSize, setFontSize] = useState(32);
  const [fontWeight, setFontWeight] = useState(400);
  const [showUnrenderable, setShowUnrenderable] = useState(false);
  const [showDownloadless, setShowDownloadless] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // Initial prompt
  useEffect(() => {
    handleSend("Show me diverse, modern trending fonts for UI design.");
  }, []);

  // Update dynamic font link & check renderability
  useEffect(() => {
    if (fonts.length > 0) {
      const uniqueNames = Array.from(new Set(fonts.map(f => f.name)));
      
      // 1. Update Stylesheet
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

      // 2. Check Renderability and Downloadability
      uniqueNames.forEach((name) => {
        const font = fonts.find(f => f.name === name);
        if (!font) return;

        const hasFiles = font.files && Object.keys(font.files).length > 0;
        
        // Check renderable (after a short delay for stylesheet to parse)
        setTimeout(async () => {
          let isRenderable = false;
          try {
            // Test at multiple weights to be sure
            const loaded = await document.fonts.load(`${fontWeight} 16px "${name}"`);
            isRenderable = loaded.length > 0;
          } catch (e) {
            console.error(`Render check failed for ${name}:`, e);
          }

          if (!isRenderable && !hasFiles) {
             console.log(`%c🚫 Font Hidden: ${name} (No download + No render)`, "color: #ff4444; font-weight: bold;");
          }

          setFontStatuses(prev => ({
            ...prev,
            [name]: { renderable: isRenderable, downloadable: !!hasFiles }
          }));
        }, 1500);
      });
    }
  }, [fonts, fontWeight]);

  // Filtered fonts logic
  const filteredFonts = fonts.filter(font => {
    const s = fontStatuses[font.name];
    if (!s) return true; // Show while checking

    // If both fail, NEVER show
    if (!s.renderable && !s.downloadable) return false;

    // Apply user toggles
    if (!showUnrenderable && !s.renderable) return false;
    if (!showDownloadless && !s.downloadable) return false;

    return true;
  });

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

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Search failed with status ${response.status}`);
      }

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
          showUnrenderable={showUnrenderable}
          setShowUnrenderable={setShowUnrenderable}
          showDownloadless={showDownloadless}
          setShowDownloadless={setShowDownloadless}
        />
        <FontGrid
          fonts={filteredFonts}
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
