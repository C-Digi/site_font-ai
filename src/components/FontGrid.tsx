"use client";

import { Font } from "@/lib/types";
import { FontCard } from "./FontCard";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface FontGridProps {
  fonts: Font[];
  isLoading: boolean;
  previewText: string;
  fontSize: number;
  fontWeight: number;
  currentPage: number;
  setCurrentPage: (page: number) => void;
  itemsPerPage: number;
}

export function FontGrid({
  fonts,
  isLoading,
  previewText,
  fontSize,
  fontWeight,
  currentPage,
  setCurrentPage,
  itemsPerPage,
}: FontGridProps) {
  if (isLoading && fonts.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl p-4">
            <div className="flex justify-between mb-4">
              <div className="h-4 w-24 rounded skeleton" />
              <div className="h-4 w-4 rounded skeleton" />
            </div>
            <div className="h-8 w-3/4 rounded skeleton" />
          </div>
        ))}
      </div>
    );
  }

  if (fonts.length === 0) {
    return (
      <div className="col-span-full text-center text-gray-400 py-10 italic">
        Start a chat to find fonts...
      </div>
    );
  }

  const totalPages = Math.ceil(fonts.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentFonts = fonts.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="flex flex-col flex-1">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {currentFonts.map((font, i) => (
          <FontCard
            key={`${font.name}-${i}`}
            font={font}
            previewText={previewText}
            fontSize={fontSize}
            fontWeight={fontWeight}
          />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 py-4 mt-auto">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
          >
            <ChevronLeft className="w-4 h-4" /> Previous
          </button>
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
