"use client";

import { RotateCcw, AlertCircle, DownloadCloud } from "lucide-react";

interface ControlsProps {
  previewText: string;
  setPreviewText: (text: string) => void;
  fontSize: number;
  setFontSize: (size: number) => void;
  fontWeight: number;
  setFontWeight: (weight: number) => void;
  showUnrenderable: boolean;
  setShowUnrenderable: (show: boolean) => void;
  showDownloadless: boolean;
  setShowDownloadless: (show: boolean) => void;
}

export function Controls({
  previewText,
  setPreviewText,
  fontSize,
  setFontSize,
  fontWeight,
  setFontWeight,
  showUnrenderable,
  setShowUnrenderable,
  showDownloadless,
  setShowDownloadless,
}: ControlsProps) {
  const pangrams = [
    "The quick brown fox jumps over the lazy dog.",
    "Pack my box with five dozen liquor jugs.",
    "Sphinx of black quartz, judge my vow.",
    "How vexingly quick balthazar zephyr pulls his fjord-themed gown.",
    "The quick brown fox jumps over the lazy dog.",
    "Pack my box with five dozen liquor jugs.",
  ];

  const setRandomPangram = () => {
    const random = pangrams[Math.floor(Math.random() * pangrams.length)] ?? pangrams[0];
    setPreviewText(random!);
  };

  return (
    <div className="bg-white dark:bg-gray-900 p-4 rounded-xl border border-gray-200 dark:border-gray-800 flex flex-col gap-6 shadow-sm mb-8">
      <div className="flex flex-col md:flex-row gap-6">
        <div className="flex-1 flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
            Preview Text
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={previewText}
              onChange={(e) => setPreviewText(e.target.value)}
              className="flex-1 bg-transparent border-b border-gray-200 dark:border-gray-700 py-1 text-base focus:border-blue-500 outline-none transition-colors dark:text-white"
            />
            <button
              onClick={setRandomPangram}
              className="text-gray-400 hover:text-blue-500 transition-colors"
              title="Random Pangram"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
          </div>
        </div>
        <div className="w-full md:w-32 flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 flex justify-between">
            Size <span>{fontSize}px</span>
          </label>
          <input
            type="range"
            min="12"
            max="72"
            value={fontSize}
            onChange={(e) => setFontSize(parseInt(e.target.value))}
            className="w-full h-1 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
        </div>
        <div className="w-full md:w-32 flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400 flex justify-between">
            Weight <span>{fontWeight}</span>
          </label>
          <input
            type="range"
            min="100"
            max="900"
            step="100"
            value={fontWeight}
            onChange={(e) => setFontWeight(parseInt(e.target.value))}
            className="w-full h-1 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-4 pt-4 border-t border-gray-50 dark:border-gray-800/50">
        <label className="flex items-center gap-2 cursor-pointer group">
          <input
            type="checkbox"
            checked={showUnrenderable}
            onChange={(e) => setShowUnrenderable(e.target.checked)}
            className="w-3 h-3 rounded text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-700"
          />
          <span className="text-[11px] font-medium text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" /> Include rendering issues
          </span>
        </label>
        
        <label className="flex items-center gap-2 cursor-pointer group">
          <input
            type="checkbox"
            checked={showDownloadless}
            onChange={(e) => setShowDownloadless(e.target.checked)}
            className="w-3 h-3 rounded text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-700"
          />
          <span className="text-[11px] font-medium text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200 flex items-center gap-1">
            <DownloadCloud className="w-3 h-3" /> Include missing downloads
          </span>
        </label>
      </div>
    </div>
  );
}
