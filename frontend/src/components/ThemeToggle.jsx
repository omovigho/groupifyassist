import { useEffect, useState, useCallback } from 'react';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle({ size = 18, className = '' }) {
  const [isDark, setIsDark] = useState(() => {
    if (typeof document === 'undefined') return false;
    return document.documentElement.classList.contains('dark');
  });

  const applyTheme = useCallback((dark) => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
    setIsDark(dark);
  }, []);

  useEffect(() => {
    const onStorage = (e) => {
      if (e.key === 'theme') {
        applyTheme(e.newValue === 'dark');
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [applyTheme]);

  return (
    <button
      type="button"
      onClick={() => applyTheme(!isDark)}
      aria-label="Toggle theme"
      className={`inline-flex items-center gap-2 rounded-md border border-border px-2.5 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground transition ${className}`}
    >
      {isDark ? <Sun size={size} /> : <Moon size={size} />}
      <span className="hidden sm:inline">{isDark ? 'Light' : 'Dark'}</span>
    </button>
  );
}
