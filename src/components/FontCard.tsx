"use client";

import { ExternalLink } from "lucide-react";
import { Font } from "@/lib/types";

interface FontCardProps {
  font: Font;
  previewText: string;
  fontSize: number;
  fontWeight: number;
}

export function FontCard({ font, previewText, fontSize, fontWeight }: FontCardProps) {
  const googleFontsUrl = `https://fonts.google.com/specimen/${font.name.replace(/\s+/g, "+")}`;

  return (
    <div className="font-card bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4 transition-all duration-300 group hover:shadow-md">
      <div className="flex justify-between items-center mb-3">
        <div className="relative cursor-help flex flex-col group/tooltip">
          <span className="font-bold text-sm text-gray-900 dark:text-gray-100 border-b border-dotted border-gray-300 dark:border-gray-700 pb-0.5">
            {font.name}
          </span>
          <span className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">
            {font.category}
          </span>
          
          <div className="opacity-0 group-hover/tooltip:opacity-100 pointer-events-none absolute left-0 bottom-full mb-2 w-48 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-[11px] p-2 rounded-lg shadow-xl backdrop-blur-sm z-50 transition-all transform translate-y-2 group-hover/tooltip:translate-y-0">
            <p className="font-medium">{font.desc}</p>
            <div className="absolute top-full left-4 border-8 border-transparent border-t-gray-900 dark:border-t-gray-100"></div>
          </div>
        </div>
        <a
          href={googleFontsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-300 hover:text-blue-500 transition-colors"
          title="View on Google Fonts"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
      <div
        className="preview-text w-full overflow-hidden whitespace-nowrap text-ellipsis transition-all duration-200"
        style={{
          fontFamily: `'${font.name}', sans-serif`,
          fontSize: `${fontSize}px`,
          fontWeight: fontWeight,
        }}
      >
        {previewText}
      </div>
    </div>
  );
}
