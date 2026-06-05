"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/lib/theme-provider";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="group relative inline-flex h-8 w-14 items-center rounded-full bg-slate-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-800"
      aria-label="Toggle theme"
    >
      <span className="sr-only">Toggle theme</span>

      <span
        className={`
          ${isDark ? "translate-x-7" : "translate-x-1"}
          inline-flex h-6 w-6 transform items-center justify-center rounded-full 
          bg-white shadow-md transition-transform duration-300 ease-in-out
        `}
      >
        {!isDark && (
          <Sun className="size-4 text-orange-500 animate-in fade-in zoom-in duration-300" />
        )}

        {isDark && (
          <Moon className="size-4 text-blue-600 fill-blue-600 animate-in fade-in zoom-in duration-300" />
        )}
      </span>
    </button>
  );
}
