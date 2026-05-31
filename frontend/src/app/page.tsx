"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function WelcomePage() {
  const router = useRouter();
  const [step, setStep] = useState<"welcome" | "join">("welcome");
  const [inviteCode, setInviteCode] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!inviteCode.trim() || !fullName.trim()) {
      setError("Введите код приглашения и ваше имя");
      return;
    }

    setLoading(true);
    try {
      const result = await api.joinSession(inviteCode.trim(), fullName.trim(), email || undefined);
      router.push(`/test/${result.attempt_id}?title=${encodeURIComponent(result.session_title)}&total=${result.total_questions}`);
    } catch (err: any) {
      setError(err.message || "Не удалось присоединиться к сессии");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-[75vh] flex flex-col items-center justify-center py-6 overflow-hidden">
      {/* Decorative Floating Blobs (Headspace Aesthetic) */}
      <div className="absolute top-10 left-10 w-24 h-24 bg-accent-yellow/20 rounded-full blur-xl animate-float" />
      <div className="absolute bottom-10 right-10 w-36 h-36 bg-primary-light/40 rounded-full blur-xl animate-float-delayed" />
      <div className="absolute top-20 right-20 w-16 h-16 bg-accent-pink/20 rounded-full blur-lg animate-float" />
      <div className="absolute bottom-20 left-20 w-28 h-28 bg-accent-teal/15 rounded-full blur-xl animate-float-delayed" />

      {step === "welcome" ? (
        <div className="text-center max-w-xl px-4 animate-pop-in relative z-10">
          {/* Relaxing Character Mascot (Smiling Headspace Purple Sun) */}
          <div className="relative w-28 h-28 mx-auto mb-8 animate-float">
            <div className="absolute inset-0 bg-primary/10 rounded-full scale-110 blur-md"></div>
            <div className="w-full h-full bg-primary rounded-full flex items-center justify-center shadow-lg relative">
              <svg viewBox="0 0 100 100" className="w-20 h-20 fill-white">
                <circle cx="50" cy="50" r="40" />
                <path d="M 30,42 C 30,42 36,48 42,42" stroke="#7B52FF" strokeWidth="5" strokeLinecap="round" fill="none" />
                <path d="M 58,42 C 58,42 64,48 70,42" stroke="#7B52FF" strokeWidth="5" strokeLinecap="round" fill="none" />
                <path d="M 38,58 A 12,12 0 0,0 62,58" stroke="#7B52FF" strokeWidth="5" strokeLinecap="round" fill="none" />
                <circle cx="28" cy="54" r="5" fill="#F299B2" opacity="0.8" />
                <circle cx="72" cy="54" r="5" fill="#F299B2" opacity="0.8" />
              </svg>
            </div>
          </div>

          <h1 className="text-4xl md:text-5xl font-heading font-extrabold text-text-dark tracking-tight mb-4 leading-tight">
            Осознайте свой тип <br />
            личности с <span className="text-primary underline decoration-accent-yellow decoration-4 underline-offset-4">mbtimind</span>
          </h1>
          
          <p className="text-text-secondary text-lg md:text-xl mb-10 max-w-md mx-auto leading-relaxed">
            Пройдите мягкий, терапевтический тест Майерс-Бриггс. Узнайте свои сильные стороны и получите персональные советы по развитию.
          </p>

          {/* Features Grid */}
          <div className="grid grid-cols-3 gap-4 md:gap-5 mb-10">
            <FeatureCard 
              color="bg-accent-yellow/10 border-accent-yellow/20"
              icon={
                <svg className="w-7 h-7 text-accent-yellow mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              } 
              title="15 минут" 
              subtitle="в тишине" 
            />
            <FeatureCard 
              color="bg-accent-teal/10 border-accent-teal/20"
              icon={
                <svg className="w-7 h-7 text-accent-teal mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              } 
              title="60 вопросов" 
              subtitle="честных ответов" 
            />
            <FeatureCard 
              color="bg-accent-pink/10 border-accent-pink/20"
              icon={
                <svg className="w-7 h-7 text-accent-pink mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              } 
              title="Детальный отчет" 
              subtitle="о вашей душе" 
            />
          </div>

          <button
            onClick={() => setStep("join")}
            className="w-full sm:w-auto px-10 py-4 bg-primary hover:bg-primary-hover text-white font-heading font-bold text-lg rounded-full btn-pop transition-transform"
          >
            Начать исследование
          </button>
        </div>
      ) : (
        <div className="w-full max-w-md px-4 animate-pop-in relative z-10">
          <button
            onClick={() => setStep("welcome")}
            className="group text-text-secondary hover:text-primary mb-6 flex items-center gap-2 text-sm font-bold transition-colors"
          >
            <span className="text-lg transition-transform group-hover:-translate-x-1">←</span> Назад на главную
          </button>

          <div className="bg-white rounded-3xl border-2 border-surface-border p-8 md:p-10 shadow-bouncy">
            <h2 className="text-2xl font-heading font-extrabold text-text-dark mb-2">
              Присоединиться к сессии
            </h2>
            <p className="text-text-secondary text-sm mb-8 leading-relaxed">
              Введите пригласительный код, выданный вашим проводником или организатором тестирования
            </p>

            <form onSubmit={handleJoin} className="space-y-6">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-text-secondary mb-2">
                  Код приглашения *
                </label>
                <input
                  type="text"
                  value={inviteCode}
                  onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                  placeholder="CODE123"
                  maxLength={8}
                  className="w-full px-4 py-4 border-2 border-surface-border rounded-2xl text-center text-2xl font-mono font-bold tracking-widest text-primary focus:outline-none focus:border-primary transition-colors bg-surface-bg/30 focus:bg-white"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-text-secondary mb-2">
                  Ваше имя *
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Алексей"
                  className="w-full px-5 py-3.5 border-2 border-surface-border rounded-2xl text-text-dark focus:outline-none focus:border-primary transition-colors bg-surface-bg/30 focus:bg-white text-base"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-text-secondary mb-2">
                  Email <span className="text-text-light font-normal">(необязательно)</span>
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex@mind.ru"
                  className="w-full px-5 py-3.5 border-2 border-surface-border rounded-2xl text-text-dark focus:outline-none focus:border-primary transition-colors bg-surface-bg/30 focus:bg-white text-base"
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-100 text-accent-red text-sm px-4 py-3 rounded-2xl font-medium animate-pop-in">
                  🤔 {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary hover:bg-primary-hover disabled:opacity-50 text-white font-heading font-bold py-4 rounded-full btn-pop transition-all text-base mt-2"
              >
                {loading ? "Ищем сессию..." : "Начать путешествие"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  color: string;
}

function FeatureCard({ icon, title, subtitle, color }: FeatureCardProps) {
  return (
    <div className={`p-4 rounded-3xl border-2 text-center bg-white transition-transform hover:-translate-y-1 hover:shadow-md duration-200`}>
      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3 ${color.split(' ')[0]} border ${color.split(' ')[1]}`}>
        {icon}
      </div>
      <div className="font-heading font-extrabold text-text-dark text-sm md:text-base leading-tight mb-1">{title}</div>
      <div className="text-text-secondary text-xxs md:text-xs leading-tight">{subtitle}</div>
    </div>
  );
}
