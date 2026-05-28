"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import { api, Question } from "@/lib/api";

export default function TestPage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const attemptId = params.attemptId as string;
  const sessionTitle = searchParams.get("title") || "MBTI Тестирование";
  const totalQuestions = parseInt(searchParams.get("total") || "60");

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answeredCount, setAnsweredCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [error, setError] = useState("");

  // Timer for response time tracking
  const questionStartTime = useRef<number>(Date.now());

  // Load first batch of questions
  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const data = await api.getQuestions(attemptId, 10);
      setQuestions(data.questions);
      setCurrentIndex(0);
      questionStartTime.current = Date.now();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = useCallback(async (option: "a" | "b") => {
    if (submitting) return;

    const question = questions[currentIndex];
    if (!question) return;

    const responseTime = Date.now() - questionStartTime.current;
    setSubmitting(true);
    setError("");

    try {
      const result = await api.submitAnswer(attemptId, question.id, option, responseTime);
      setAnsweredCount(result.progress);

      // Move to next question
      if (currentIndex < questions.length - 1) {
        setCurrentIndex((prev) => prev + 1);
        questionStartTime.current = Date.now();
      } else if (result.progress >= totalQuestions) {
        // All questions answered — complete test
        setFinishing(true);
        const testResult = await api.completeTest(attemptId);
        router.push(`/results/${attemptId}`);
        return;
      } else {
        // Load next batch
        const data = await api.getQuestions(attemptId, 10);
        if (data.questions.length > 0) {
          setQuestions(data.questions);
          setCurrentIndex(0);
          questionStartTime.current = Date.now();
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }, [attemptId, currentIndex, questions, submitting, totalQuestions, router]);

  // Keyboard shortcuts: 1 or A for option A, 2 or B for option B
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "1" || e.key.toLowerCase() === "a") handleAnswer("a");
      if (e.key === "2" || e.key.toLowerCase() === "b") handleAnswer("b");
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleAnswer]);

  const progress = (answeredCount / totalQuestions) * 100;
  const currentQuestion = questions[currentIndex];

  if (finishing) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[65vh] text-center px-4 animate-pop-in">
        <div className="relative w-24 h-24 mb-8">
          <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping"></div>
          <div className="w-full h-full bg-primary rounded-full flex items-center justify-center relative shadow-lg">
            <svg viewBox="0 0 100 100" className="w-14 h-14 fill-white animate-bounce">
              <circle cx="50" cy="50" r="40" />
              <path d="M 32,45 C 32,45 37,50 42,45" stroke="#7B52FF" strokeWidth="6" strokeLinecap="round" fill="none" />
              <path d="M 58,45 C 58,45 63,50 68,45" stroke="#7B52FF" strokeWidth="6" strokeLinecap="round" fill="none" />
              <path d="M 38,62 A 12,12 0 0,0 62,62" stroke="#7B52FF" strokeWidth="6" strokeLinecap="round" fill="none" />
            </svg>
          </div>
        </div>
        <h2 className="text-3xl font-heading font-extrabold text-text-dark mb-3">Собираем мысли воедино...</h2>
        <p className="text-text-secondary text-lg max-w-sm mx-auto leading-relaxed">
          Анализируем ваши ответы по 4 основным шкалам MBTI для составления глубокого портрета личности.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[65vh] text-center px-4 animate-pop-in">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center relative shadow-sm border border-primary/20 mb-4 animate-pulse">
          <div className="w-10 h-10 bg-primary rounded-full animate-ping opacity-75 absolute"></div>
          <div className="w-8 h-8 bg-primary rounded-full"></div>
        </div>
        <p className="text-text-secondary font-medium">Настраиваем дыхание и готовим вопросы...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 relative z-10 animate-pop-in">
      {/* Header Info */}
      <div className="bg-white rounded-3xl border-2 border-surface-border p-6 mb-8 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h1 className="font-heading font-extrabold text-lg text-text-dark tracking-tight">{sessionTitle}</h1>
          <div className="text-sm font-bold text-primary bg-primary-light px-3 py-1 rounded-full">
            {answeredCount} из {totalQuestions} ответов
          </div>
        </div>
        
        {/* Playful Progress Bar */}
        <div className="w-full h-4 bg-surface-bg border-2 border-surface-border rounded-full overflow-hidden p-0.5 relative">
          <div
            className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-text-secondary font-bold mt-2.5 px-1">
          <span>Старт путешествия</span>
          <span>{Math.round(progress)}% завершено</span>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-2 border-red-100 text-accent-red text-sm px-4 py-3 rounded-2xl mb-6 font-medium animate-pop-in">
          🤔 {error}
        </div>
      )}

      {/* Question Card */}
      {currentQuestion && (
        <div className="bg-white rounded-3xl border-2 border-surface-border p-8 md:p-10 mb-8 shadow-bouncy transition-transform relative overflow-hidden">
          {/* Subtle colored blob in card background */}
          <div className="absolute -top-12 -right-12 w-28 h-28 bg-primary-light/30 rounded-full blur-xl pointer-events-none" />

          <p className="text-xl md:text-2xl font-heading font-extrabold text-text-dark leading-relaxed mb-10 text-center">
            {currentQuestion.text_ru}
          </p>

          <div className="space-y-4">
            <button
              onClick={() => handleAnswer("a")}
              disabled={submitting}
              className="w-full text-left p-5 rounded-2xl border-2 border-surface-border hover:border-primary hover:bg-primary-light/40 transition-all duration-200 disabled:opacity-50 group flex items-center justify-between active:scale-[0.99]"
            >
              <div className="flex items-start gap-4">
                <span className="w-10 h-10 rounded-full bg-surface-bg border-2 border-surface-border flex items-center justify-center text-base font-heading font-extrabold text-text-secondary group-hover:bg-primary group-hover:text-white group-hover:border-primary transition-all shrink-0">
                  A
                </span>
                <span className="text-text-dark font-semibold leading-relaxed pt-1.5 text-base md:text-lg">
                  {currentQuestion.option_a_ru}
                </span>
              </div>
              <svg className="w-6 h-6 text-primary opacity-0 group-hover:opacity-100 transition-opacity duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>

            <button
              onClick={() => handleAnswer("b")}
              disabled={submitting}
              className="w-full text-left p-5 rounded-2xl border-2 border-surface-border hover:border-primary hover:bg-primary-light/40 transition-all duration-200 disabled:opacity-50 group flex items-center justify-between active:scale-[0.99]"
            >
              <div className="flex items-start gap-4">
                <span className="w-10 h-10 rounded-full bg-surface-bg border-2 border-surface-border flex items-center justify-center text-base font-heading font-extrabold text-text-secondary group-hover:bg-primary group-hover:text-white group-hover:border-primary transition-all shrink-0">
                  B
                </span>
                <span className="text-text-dark font-semibold leading-relaxed pt-1.5 text-base md:text-lg">
                  {currentQuestion.option_b_ru}
                </span>
              </div>
              <svg className="w-6 h-6 text-primary opacity-0 group-hover:opacity-100 transition-opacity duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Relaxing Keyboard Hint */}
      <p className="text-center text-text-light text-sm font-medium flex items-center justify-center gap-1.5 select-none animate-pulse">
        <span>✨ Подсказка: нажимайте</span>
        <kbd className="px-2 py-1 bg-white border-2 border-surface-border rounded-xl text-xs font-heading font-extrabold text-text-dark shadow-sm">A</kbd>
        <span>или</span>
        <kbd className="px-2 py-1 bg-white border-2 border-surface-border rounded-xl text-xs font-heading font-extrabold text-text-dark shadow-sm">B</kbd>
        <span>на клавиатуре для быстрого ответа</span>
      </p>
    </div>
  );
}
