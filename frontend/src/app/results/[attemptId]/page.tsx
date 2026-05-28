"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { api, TestResult } from "@/lib/api";

export default function ResultsPage() {
  const params = useParams();
  const attemptId = params.attemptId as string;

  const [result, setResult] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchResult() {
      try {
        const data = await api.getResult(attemptId);
        setResult(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchResult();
  }, [attemptId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[65vh] text-center px-4">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center relative shadow-sm border border-primary/20 mb-4 animate-pulse">
          <div className="w-10 h-10 bg-primary rounded-full animate-ping opacity-75 absolute"></div>
          <div className="w-8 h-8 bg-primary rounded-full"></div>
        </div>
        <p className="text-text-secondary font-medium">Готовим подробный разбор вашего типа личности...</p>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="text-center py-20 animate-pop-in">
        <div className="text-4xl mb-4">🤔</div>
        <p className="text-accent-red text-lg font-semibold mb-6">{error || "Результат не найден"}</p>
        <button 
          onClick={() => window.location.href = "/"}
          className="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-full btn-pop font-heading font-bold"
        >
          На главную
        </button>
      </div>
    );
  }

  const confidencePercent = Math.round(result.confidence_score * 100);
  const confidenceColor =
    confidencePercent >= 70 ? "text-accent-teal" :
    confidencePercent >= 40 ? "text-accent-yellow" : "text-accent-red";
  const confidenceBg =
    confidencePercent >= 70 ? "bg-accent-teal/10 border-accent-teal/20" :
    confidencePercent >= 40 ? "bg-accent-yellow/10 border-accent-yellow/20" : "bg-red-50 border-red-100";

  return (
    <div className="max-w-3xl mx-auto px-4 relative z-10 animate-pop-in">
      {/* Floating background decorations */}
      <div className="absolute -top-10 -left-10 w-32 h-32 bg-primary-light/30 rounded-full blur-2xl pointer-events-none" />
      <div className="absolute top-40 -right-20 w-44 h-44 bg-accent-yellow/10 rounded-full blur-3xl pointer-events-none" />

      {/* Type Hero */}
      <div className="bg-white rounded-3xl border-2 border-surface-border p-8 md:p-10 text-center mb-8 shadow-bouncy relative overflow-hidden">
        {/* Playful abstract circle frame behind text */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-primary-light/20 rounded-full blur-3xl pointer-events-none" />
        
        {/* Soft mascot smile badge */}
        <div className="w-16 h-16 bg-primary-light rounded-full flex items-center justify-center mx-auto mb-4 border border-primary/20">
          <svg viewBox="0 0 100 100" className="w-10 h-10 fill-primary animate-float">
            <circle cx="50" cy="50" r="42" />
            <path d="M 32,44 C 32,44 37,49 42,44" stroke="#ffffff" strokeWidth="6" strokeLinecap="round" fill="none" />
            <path d="M 58,44 C 58,44 63,49 68,44" stroke="#ffffff" strokeWidth="6" strokeLinecap="round" fill="none" />
            <path d="M 38,60 A 12,12 0 0,0 62,60" stroke="#ffffff" strokeWidth="6" strokeLinecap="round" fill="none" />
          </svg>
        </div>

        <p className="text-text-secondary text-xs font-bold uppercase tracking-wider mb-2">Ваш тип личности</p>
        <h1 className="text-6xl md:text-7xl font-heading font-extrabold text-primary mb-3 tracking-widest drop-shadow-sm select-none">
          {result.mbti_type}
        </h1>
        <p className="text-2xl text-text-dark font-heading font-extrabold mb-6">
          {result.type_name_ru || "—"}
        </p>
        
        <div className="max-w-xl mx-auto bg-surface-bg/50 border border-surface-border rounded-2xl p-5 md:p-6 text-left mb-6 shadow-sm">
          <p className="text-text-dark leading-relaxed text-base md:text-lg">
            {result.type_description_ru}
          </p>
        </div>

        {/* Confidence badge */}
        <div className={`inline-flex items-center gap-2 rounded-2xl px-5 py-2.5 border ${confidenceBg} shadow-sm font-bold text-sm`}>
          <span className="text-text-secondary">Уверенность результата:</span>
          <span className={`${confidenceColor} text-base font-extrabold`}>{confidencePercent}%</span>
        </div>

        {!result.is_valid && (
          <div className="mt-4 block bg-red-50 border border-red-100 text-accent-red text-xs md:text-sm px-4 py-2.5 rounded-2xl font-bold">
            ⚠️ Внимание: в ответах замечены признаки неконсистентности. Возможно, вы колебались или спешили.
          </div>
        )}
      </div>

      {/* Scale Bars */}
      <div className="bg-white rounded-3xl border-2 border-surface-border p-8 md:p-10 mb-8 shadow-sm">
        <h2 className="text-xl md:text-2xl font-heading font-extrabold text-text-dark mb-8 flex items-center gap-2">
          <span>Ваш внутренний баланс шкал</span>
          <span className="text-xs bg-primary/10 text-primary rounded-full px-2.5 py-0.5 font-bold uppercase">4 Шкалы</span>
        </h2>
        <div className="space-y-8">
          {result.scales.map((scale, index) => (
            <ScaleBar key={scale.scale} scale={scale} index={index} />
          ))}
        </div>
      </div>

      {/* Career Recommendations */}
      {result.career_recommendations && result.career_recommendations.length > 0 && (
        <div className="bg-white rounded-3xl border-2 border-surface-border p-8 md:p-10 mb-8 shadow-sm">
          <h2 className="text-xl md:text-2xl font-heading font-extrabold text-text-dark mb-6 flex items-center gap-2">
            <span>Рекомендуемые сферы и профессии</span>
            <span className="text-lg">🎯</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {result.career_recommendations.map((career, i) => {
              // Cycle colors for recommendation numbers
              const pillColors = [
                "bg-primary-light text-primary border-primary/20",
                "bg-accent-teal/10 text-accent-teal border-accent-teal/20",
                "bg-accent-yellow/10 text-accent-yellow border-accent-yellow/20",
                "bg-accent-pink/10 text-accent-pink border-accent-pink/20"
              ];
              const pColor = pillColors[i % pillColors.length];
              
              return (
                <div
                  key={i}
                  className="flex items-center gap-4 p-4 bg-surface-bg/50 hover:bg-white hover:shadow-md border-2 border-surface-border rounded-2xl transition-all duration-200"
                >
                  <span className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-heading font-extrabold shrink-0 ${pColor}`}>
                    {i + 1}
                  </span>
                  <span className="text-base font-bold text-text-dark leading-snug">{career}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
        <button
          onClick={() => window.print()}
          className="w-full sm:w-auto px-8 py-3.5 bg-white border-2 border-surface-border rounded-full text-text-dark hover:bg-surface-bg transition-all text-base font-bold btn-pop-white"
        >
          🖨️ Скачать PDF отчет
        </button>
        <button
          onClick={() => (window.location.href = "/")}
          className="w-full sm:w-auto px-8 py-3.5 bg-primary hover:bg-primary-hover text-white rounded-full transition-all text-base font-bold btn-pop"
        >
          🏡 На главную
        </button>
      </div>
    </div>
  );
}

function ScaleBar({ scale, index }: { scale: TestResult["scales"][0]; index: number }) {
  const total = scale.positive_count + scale.negative_count;
  const leftPercent = total > 0 ? (scale.positive_count / total) * 100 : 50;
  const rightPercent = 100 - leftPercent;
  const isLeftDominant = scale.positive_count >= scale.negative_count;

  // Scale colors: Purple, Teal, Yellow, Pink
  const activeColors = ["bg-[#7B52FF]", "bg-[#35B0A2]", "bg-[#F5C747]", "bg-[#F299B2]"];
  const selectColor = activeColors[index % activeColors.length];

  const scaleLetters: Record<string, [string, string]> = {
    "E/I": ["E", "I"],
    "S/N": ["S", "N"],
    "T/F": ["T", "F"],
    "J/P": ["J", "P"],
  };
  const [leftLetter, rightLetter] = scaleLetters[scale.scale] || ["?", "?"];

  return (
    <div className="group">
      {/* Labels */}
      <div className="flex justify-between text-base font-bold mb-3 px-1">
        <span className={`flex items-center gap-1.5 transition-colors ${isLeftDominant ? "text-primary font-extrabold text-lg" : "text-text-secondary"}`}>
          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${isLeftDominant ? "bg-primary text-white" : "bg-surface-bg border border-surface-border text-text-secondary"}`}>
            {leftLetter}
          </span>
          <span>{scale.positive_label}</span>
        </span>
        <span className={`flex items-center gap-1.5 transition-colors ${!isLeftDominant ? "text-primary font-extrabold text-lg" : "text-text-secondary"}`}>
          <span>{scale.negative_label}</span>
          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${!isLeftDominant ? "bg-primary text-white" : "bg-surface-bg border border-surface-border text-text-secondary"}`}>
            {rightLetter}
          </span>
        </span>
      </div>

      {/* Tactile Bubbly Bar */}
      <div className="flex h-10 bg-surface-bg border-2 border-surface-border rounded-full overflow-hidden p-0.5 transition-transform duration-200 group-hover:scale-[1.01]">
        {/* Left Side */}
        <div
          className={`flex items-center justify-end pr-3 transition-all duration-500 rounded-l-full ${
            isLeftDominant ? selectColor : "bg-primary/20"
          }`}
          style={{ width: `${leftPercent}%` }}
        >
          {leftPercent > 10 && (
            <span className={`text-sm font-heading font-extrabold ${isLeftDominant ? "text-white" : "text-primary"}`}>
              {Math.round(leftPercent)}%
            </span>
          )}
        </div>
        {/* Right Side */}
        <div
          className={`flex items-center justify-start pl-3 transition-all duration-500 rounded-r-full ${
            !isLeftDominant ? selectColor : "bg-primary/20"
          }`}
          style={{ width: `${rightPercent}%` }}
        >
          {rightPercent > 10 && (
            <span className={`text-sm font-heading font-extrabold ${!isLeftDominant ? "text-white" : "text-primary"}`}>
              {Math.round(rightPercent)}%
            </span>
          )}
        </div>
      </div>

      {/* Counts */}
      <div className="flex justify-between text-xs text-text-light font-bold mt-1.5 px-2">
        <span>{scale.positive_count} ответов</span>
        <span>{scale.negative_count} ответов</span>
      </div>
    </div>
  );
}
