import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MBTI Mind — Познай себя",
  description: "Профессиональное MBTI тестирование и исследование личности в стиле Headspace",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body className="min-h-screen bg-surface-bg text-text-dark antialiased">
        <header className="sticky top-0 z-50 bg-[#FAF7F2]/80 backdrop-blur-md border-b border-surface-border py-4 px-6">
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            {/* Friendly Brand Logo */}
            <a href="/" className="flex items-center gap-3 group transition-transform active:scale-95">
              <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center relative shadow-sm hover:rotate-12 transition-transform duration-300">
                {/* Cute Headspace Smiley Sun (in purple) */}
                <svg viewBox="0 0 100 100" className="w-7 h-7 fill-white">
                  {/* Face */}
                  <circle cx="50" cy="50" r="40" />
                  {/* Closed happy eyes */}
                  <path d="M 32,45 C 32,45 37,50 42,45" stroke="#7B52FF" strokeWidth="6" strokeLinecap="round" fill="none" />
                  <path d="M 58,45 C 58,45 63,50 68,45" stroke="#7B52FF" strokeWidth="6" strokeLinecap="round" fill="none" />
                  {/* Cute smiley mouth */}
                  <path d="M 40,60 A 10,10 0 0,0 60,60" stroke="#7B52FF" strokeWidth="6" strokeLinecap="round" fill="none" />
                </svg>
              </div>
              <span className="font-heading font-extrabold text-xl text-text-dark tracking-tight">
                mbti<span className="text-primary">mind</span>
              </span>
            </a>

            {/* Quick Navigation and Badge */}
            <div className="flex items-center gap-6">
              <a
                href="/admin"
                className="text-sm font-semibold text-text-secondary hover:text-primary transition-colors flex items-center gap-1.5"
              >
                <span>Панель управления</span>
                <span className="w-1.5 h-1.5 rounded-full bg-accent-teal"></span>
              </a>
              <span className="text-xs font-bold bg-primary/10 text-primary px-3 py-1.5 rounded-full border border-primary/20">
                Mindfulness v0.1
              </span>
            </div>
          </div>
        </header>

        <main className="max-w-5xl mx-auto px-6 py-10 min-h-[calc(100vh-140px)]">
          {children}
        </main>
      </body>
    </html>
  );
}
