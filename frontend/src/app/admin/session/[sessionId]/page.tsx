"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { api, SessionDetail, Participant } from "@/lib/api";

export default function SessionDetailPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadSession = async () => {
    try {
      setLoading(true);
      const data = await api.getSessionDetail(sessionId);
      setSession(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSession();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[65vh] text-center px-4 animate-pop-in">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center relative shadow-sm border border-primary/20 mb-4 animate-pulse">
          <div className="w-10 h-10 bg-primary rounded-full animate-ping opacity-75 absolute"></div>
          <div className="w-8 h-8 bg-primary rounded-full"></div>
        </div>
        <p className="text-text-secondary font-medium">Получаем детальную статистику сессии...</p>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="text-center py-20 animate-pop-in">
        <div className="text-4xl mb-4">🤔</div>
        <p className="text-accent-red text-lg font-semibold mb-6">{error || "Сессия не найдена"}</p>
        <a 
          href="/admin" 
          className="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-full btn-pop font-heading font-bold"
        >
          Назад к панели
        </a>
      </div>
    );
  }

  const isActive = session.status === "active";
  const completionRate =
    session.participants_count > 0
      ? Math.round((session.completed_count / session.participants_count) * 100)
      : 0;

  // MBTI type distribution
  const typeDistribution: Record<string, number> = {};
  session.participants.forEach((p) => {
    if (p.mbti_type) {
      typeDistribution[p.mbti_type] = (typeDistribution[p.mbti_type] || 0) + 1;
    }
  });
  const sortedTypes = Object.entries(typeDistribution).sort((a, b) => b[1] - a[1]);

  return (
    <div className="max-w-5xl mx-auto px-4 relative z-10 animate-pop-in">
      {/* Breadcrumb */}
      <a
        href="/admin"
        className="group text-text-secondary hover:text-primary mb-6 inline-flex items-center gap-2 text-sm font-bold transition-colors"
      >
        <span className="text-lg transition-transform group-hover:-translate-x-1">←</span> Назад к списку сессий
      </a>

      {/* Session Header Card */}
      <div className="bg-white rounded-3xl border-2 border-surface-border p-6 md:p-8 mb-8 shadow-sm relative overflow-hidden">
        {/* Subtle colored blob */}
        <div className="absolute -top-16 -left-16 w-36 h-36 bg-primary-light/35 rounded-full blur-2xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center flex-wrap gap-3 mb-3">
              <h1 className="text-2xl md:text-3xl font-heading font-extrabold text-text-dark tracking-tight">
                {session.title}
              </h1>
              <span
                className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wide border ${
                  isActive
                    ? "bg-accent-teal/10 text-accent-teal border-accent-teal/20"
                    : "bg-gray-100 text-text-secondary border-gray-200"
                }`}
              >
                {isActive ? "Активна" : "Закрыта"}
              </span>
            </div>
            {session.description && (
              <p className="text-text-secondary text-base font-medium mb-4 leading-relaxed max-w-2xl">{session.description}</p>
            )}
            <div className="flex items-center flex-wrap gap-y-1 gap-x-4 text-xs font-bold uppercase tracking-wider text-text-light">
              <span className="flex items-center gap-1">📅 Создана: {new Date(session.created_at).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" })}</span>
              <span className="flex items-center gap-1">✍️ {session.questions_count} вопросов в тесте</span>
            </div>
          </div>

          {/* Invite code block */}
          <div className="text-center bg-surface-bg border-2 border-surface-border rounded-2xl px-6 py-4 shrink-0 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wider text-text-secondary mb-2">Код приглашения</p>
            <p className="text-3xl font-heading font-extrabold text-primary tracking-widest font-mono mb-2 select-all">
              {session.invite_code}
            </p>
            <button
              onClick={() => navigator.clipboard.writeText(session.invite_code)}
              className="text-xs font-bold text-primary hover:underline hover:text-primary-hover transition-colors"
            >
              Скопировать код
            </button>
          </div>
        </div>

        {/* Session Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8 pt-8 border-t-2 border-surface-border">
          <MiniStat label="Участники" value={session.participants_count} icon="👥" color="text-primary bg-primary-light" />
          <MiniStat label="Завершили" value={session.completed_count} icon="✅" color="text-accent-teal bg-accent-teal/10" />
          <MiniStat label="Процент прохождения" value={`${completionRate}%`} icon="📊" color="text-accent-yellow bg-accent-yellow/10" />
          <MiniStat
            label="В процессе"
            value={session.participants_count - session.completed_count}
            icon="⌛"
            color="text-accent-pink bg-accent-pink/10"
          />
        </div>
      </div>

      {/* MBTI Distribution */}
      {sortedTypes.length > 0 && (
        <div className="bg-white rounded-3xl border-2 border-surface-border p-6 md:p-8 mb-8 shadow-sm">
          <h2 className="text-lg md:text-xl font-heading font-extrabold text-text-dark mb-6 flex items-center gap-2">
            <span>Распределение типов MBTI в группе</span>
            <span className="text-lg">🌈</span>
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-3">
            {sortedTypes.map(([type, count]) => {
              // Alternate nice backgrounds
              return (
                <div
                  key={type}
                  className="text-center p-4 bg-primary-light/30 border-2 border-primary/10 rounded-2xl hover:border-primary/40 transition-colors"
                >
                  <p className="text-2xl font-heading font-extrabold text-primary">{type}</p>
                  <p className="text-xs font-bold text-text-secondary mt-1.5">
                    {count} чел.
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Participants Table Container */}
      <div className="bg-white rounded-3xl border-2 border-surface-border shadow-sm overflow-hidden mb-12">
        <div className="px-6 py-5 border-b border-surface-border bg-surface-bg/30 flex items-center justify-between flex-wrap gap-4">
          <h2 className="text-xl font-heading font-extrabold text-text-dark">
            Результаты участников ({session.participants.length})
          </h2>
          <button
            onClick={loadSession}
            className="px-4 py-2 bg-white border-2 border-surface-border text-text-dark hover:bg-surface-bg font-bold rounded-full btn-pop-white text-xs uppercase tracking-wider"
          >
            🔄 Обновить данные
          </button>
        </div>

        {session.participants.length === 0 ? (
          <div className="text-center py-16 px-4">
            <div className="text-4xl mb-4">💫</div>
            <p className="text-text-secondary text-lg font-bold">Участников пока нет</p>
            <p className="text-text-light text-sm max-w-sm mx-auto mt-2">
              Скопируйте пригласительный код{" "}
              <span className="font-mono font-bold text-primary select-all">
                {session.invite_code}
              </span>{" "}
              и отправьте вашей группе, чтобы они смогли присоединиться к тестированию.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto no-scrollbar">
            <table className="w-full text-left text-sm font-medium border-collapse min-w-[700px]">
              <thead>
                <tr className="border-b border-surface-border bg-surface-bg/30 text-text-secondary font-bold text-xs uppercase tracking-wider">
                  <th className="px-6 py-4">Участник</th>
                  <th className="px-4 py-4">Статус</th>
                  <th className="px-4 py-4">Тип MBTI</th>
                  <th className="px-4 py-4">Уверенность</th>
                  <th className="px-4 py-4">Начало пути</th>
                  <th className="px-6 py-4 text-right">Действия</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border text-text-dark">
                {session.participants.map((p) => (
                  <ParticipantRow key={p.attempt_id} participant={p} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

interface MiniStatProps {
  label: string;
  value: number | string;
  icon: string;
  color: string;
}

function MiniStat({ label, value, icon, color }: MiniStatProps) {
  return (
    <div className="text-center p-4 bg-surface-bg/40 rounded-2xl border border-surface-border flex items-center gap-4 hover:bg-white hover:shadow-sm transition-all duration-200">
      <div className={`w-10 h-10 rounded-xl border flex items-center justify-center text-lg ${color} shrink-0`}>
        {icon}
      </div>
      <div className="text-left">
        <p className="text-2xl font-heading font-extrabold text-text-dark leading-tight">{value}</p>
        <p className="text-xs font-bold text-text-secondary mt-0.5 leading-tight">{label}</p>
      </div>
    </div>
  );
}

function ParticipantRow({ participant: p }: { participant: Participant }) {
  const isCompleted = p.status === "completed";
  const confidencePercent = p.confidence_score
    ? Math.round(p.confidence_score * 100)
    : null;
  const confidenceColor =
    confidencePercent !== null
      ? confidencePercent >= 70
        ? "text-accent-teal"
        : confidencePercent >= 40
        ? "text-accent-yellow"
        : "text-accent-red"
      : "";

  const startTime = new Date(p.started_at).toLocaleString("ru-RU", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <tr className="hover:bg-surface-bg/25 transition-colors duration-150">
      <td className="px-6 py-4">
        <div>
          <p className="font-bold text-text-dark text-base">{p.user_name}</p>
          {p.user_email && (
            <p className="text-xs text-text-light font-medium mt-0.5">{p.user_email}</p>
          )}
        </div>
      </td>
      <td className="px-4 py-4">
        <span
          className={`text-xs px-3 py-1 rounded-full font-bold uppercase border ${
            isCompleted
              ? "bg-accent-teal/10 text-accent-teal border-accent-teal/20"
              : "bg-accent-yellow/10 text-accent-yellow border-accent-yellow/20"
          }`}
        >
          {isCompleted ? "Завершен" : "В процессе"}
        </span>
      </td>
      <td className="px-4 py-4">
        {p.mbti_type ? (
          <span className="font-heading font-extrabold text-primary text-lg">{p.mbti_type}</span>
        ) : (
          <span className="text-text-light font-bold">—</span>
        )}
      </td>
      <td className="px-4 py-4">
        {confidencePercent !== null ? (
          <span className={`font-extrabold text-base ${confidenceColor}`}>
            {confidencePercent}%
          </span>
        ) : (
          <span className="text-text-light font-bold">—</span>
        )}
      </td>
      <td className="px-4 py-4 text-text-secondary font-medium">{startTime}</td>
      <td className="px-6 py-4 text-right">
        {isCompleted ? (
          <a
            href={`/results/${p.attempt_id}`}
            className="inline-flex items-center gap-1 px-4 py-2 bg-primary/10 hover:bg-primary text-primary hover:text-white border border-primary/20 rounded-full text-xs font-bold uppercase tracking-wide transition-all"
          >
            Результат →
          </a>
        ) : (
          <span className="text-text-light text-xs font-bold uppercase tracking-wider select-none">В процессе</span>
        )}
      </td>
    </tr>
  );
}
