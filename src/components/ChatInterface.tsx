"use client";

import { useState, useRef, useEffect } from "react";
import { Send, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { ChatMessage } from "@/lib/types";

interface ChatInterfaceProps {
  history: ChatMessage[];
  isLoading: boolean;
  onSend: (message: string) => void;
  status: string;
}

export function ChatInterface({ history, isLoading, onSend, status }: ChatInterfaceProps) {
  const [input, setInput] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <section className="mb-8 relative z-20">
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm transition-all duration-300 overflow-hidden">
        {isExpanded && history.length > 0 && (
          <div
            ref={scrollRef}
            className="flex flex-col gap-3 p-4 max-h-60 overflow-y-auto chat-scroll border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50"
          >
            {history.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "flex",
                  msg.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "max-w-[85%] text-sm px-3 py-2 rounded-xl",
                    msg.role === "user"
                      ? "bg-blue-100 text-blue-900 dark:bg-blue-900/30 dark:text-blue-100"
                      : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                  )}
                >
                  {msg.text}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="p-4">
          <div className="flex justify-between items-start mb-3">
            <div className={cn(
              "text-sm text-gray-600 dark:text-gray-300 font-medium flex items-center gap-2",
              isLoading && "animate-pulse"
            )}>
              {isLoading ? <div className="loader border-gray-400 border-b-blue-500" /> : <Sparkles className="w-4 h-4 text-blue-500" />}
              {status}
            </div>
            {history.length > 0 && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
              >
                <span>{isExpanded ? "Hide History" : "Show History"}</span>
                {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            )}
          </div>
          <div className="relative flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              placeholder="Describe the vibe..."
              className="flex-1 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white border-0 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-950 transition-all outline-none"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-xl px-4 py-2 transition-colors flex items-center justify-center min-w-[50px]"
            >
              {isLoading ? (
                <div className="loader border-white/30 border-b-white" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
