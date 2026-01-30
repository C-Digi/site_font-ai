"use client";

import { useState, useEffect } from "react";
import { ExternalLink, Download, Tag, AlertTriangle } from "lucide-react";
import { Font } from "@/lib/types";

interface FontCardProps {
  font: Font;
  previewText: string;
  fontSize: number;
  fontWeight: number;
}

export function FontCard({ font, previewText, fontSize, fontWeight }: FontCardProps) {
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    // Check if font is loaded/valid
    if (typeof document !== "undefined") {
      // Small delay to allow stylesheet to load
      const timeout = setTimeout(() => {
        const isLoaded = document.fonts.check(`${fontWeight} 16px "${font.name}"`);
        if (!isLoaded) {
          // Attempt to load it explicitly to be sure
          document.fonts.load(`${fontWeight} 16px "${font.name}"`).then(fonts => {
            if (fonts.length === 0) setHasError(true);
          }).catch(() => setHasError(true));
        }
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [font.name, fontWeight]);

  // Construct links based on source
  const googleFontsUrl = `https://fonts.google.com/specimen/${font.name.replace(/\s+/g, "+")}`;
  const fontshareUrl = `https://www.fontshare.com/fonts/${font.name.toLowerCase().replace(/\s+/g, "-")}`;
  const fontsourceUrl = `https://fontsource.org/fonts/${font.name.toLowerCase().replace(/\s+/g, "-")}`;
  
  const externalUrl = font.source === 'Fontshare' ? fontshareUrl : 
                      font.source === 'Fontsource' ? fontsourceUrl : 
                      googleFontsUrl;

  // For downloads, we try to find a 400 weight or the first available
  const downloadUrl = font.files?.["regular"] || font.files?.["400"] || Object.values(font.files || {})[0];

  return (
    <div className="font-card bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 transition-all duration-300 group hover:shadow-lg hover:border-blue-200 dark:hover:border-blue-900">
      <div className="flex justify-between items-start mb-4">
        <div className="flex flex-col">
          <div className="relative cursor-help inline-flex group/tooltip">
            <span className="font-bold text-base text-gray-900 dark:text-gray-100 border-b border-dotted border-gray-300 dark:border-gray-700 pb-0.5">
              {font.name}
            </span>
            
            <div className="opacity-0 group-hover/tooltip:opacity-100 pointer-events-none absolute left-0 bottom-full mb-2 w-64 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs p-3 rounded-xl shadow-2xl backdrop-blur-md z-50 transition-all transform translate-y-2 group-hover/tooltip:translate-y-0 border border-gray-800 dark:border-gray-200">
              <p className="font-medium leading-relaxed">{font.desc}</p>
              {font.tags && font.tags.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-800 dark:border-gray-200 flex flex-wrap gap-1">
                  {font.tags.slice(0, 4).map(tag => (
                    <span key={tag} className="text-[9px] px-1.5 py-0.5 bg-gray-800 dark:bg-gray-200 rounded uppercase tracking-wider font-bold">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              <div className="absolute top-full left-4 border-8 border-transparent border-t-gray-900 dark:border-t-gray-100"></div>
            </div>
          </div>
          
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[10px] uppercase tracking-wider text-gray-400 font-bold bg-gray-50 dark:bg-gray-800 px-1.5 py-0.5 rounded">
              {font.category}
            </span>
            <span className="text-[10px] text-gray-400 font-medium flex items-center gap-1">
              via {font.source || "Google Fonts"}
              {hasError && <AlertTriangle className="w-3 h-3 text-amber-500" title="Font failed to load" />}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {downloadUrl && (
            <a
              href={downloadUrl}
              download
              className="p-2 text-gray-400 hover:text-green-500 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-all"
              title="Download Font"
            >
              <Download className="w-4 h-4" />
            </a>
          )}
          <a
            href={externalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all"
            title={`View on ${font.source || "Google Fonts"}`}
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      <div
        className="preview-text w-full overflow-hidden whitespace-nowrap text-ellipsis py-2"
        style={{
          fontFamily: `'${font.name}', sans-serif`,
          fontSize: `${fontSize}px`,
          fontWeight: fontWeight,
          opacity: hasError ? 0.5 : 1
        }}
      >
        {previewText}
      </div>
      
      {font.tags && font.tags.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {font.tags.slice(0, 3).map(tag => (
            <div key={tag} className="flex items-center gap-1 text-[10px] text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-800/50 px-2 py-0.5 rounded-full border border-gray-100 dark:border-gray-800">
              <Tag className="w-2.5 h-2.5" />
              {tag}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
