import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  return (
    <header className="flex items-center justify-between mb-8">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
          Aa
        </div>
        <h1 className="text-xl font-bold tracking-tight">
          Font Explorer <span className="text-blue-500 text-sm font-normal ml-1">AI</span>
        </h1>
      </div>
      <ThemeToggle />
    </header>
  );
}
