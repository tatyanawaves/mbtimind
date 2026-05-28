"use client";

import { useState, useEffect } from "react";
import { api, TestSession } from "@/lib/api";

export default function AdminDashboard() {
  const [sessions, setSessions] = useState<TestSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  // Create form state
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newQuestionsCount, setNewQuestionsCount] = useState(60);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await api.listSessions();
      setSessions(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setCreating(true);
    setError("");
    try {
      await api.createSession({
        title: newTitle.trim(),
        description: newDescription.trim() || undefined,
        questions_count: newQuestionsCount,
      });
      setNewTitle("");
      setNewDescription("");
      setNewQuestionsCount(60);
      setShowCreate(false);
      await loadSessions();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  // Stats
  const totalSessions = sessions.length;
  const activeSessions = sessions.filter((s) => s.status === "active").length;
  const totalParticipants = sessions.reduce((sum, s) => sum + s.participants_count, 0);
  const totalCompleted = sessions.reduce((sum, s) => sum + s.completed_count, 0);

  return (
    <div className="max-w-5xl mx-auto px-4 relative z-10 animate-pop-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-heading font-extrabold text-text-dark tracking-tight">Панель управления</h1>
          <p className="text-text-secondary font-medium text-sm mt-1">
            Управляйте сессиями тестирования, делитесь приглашениями и просматривайте глубокие результаты.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-6 py-3 bg-primary hover:bg-primary-hover text-white font-heading font-bold rounded-full btn-pop transition-transform shrink-0"
        >
          {showCreate ? "✕ Закрыть форму" : "✨ Создать сессию"}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Всего сессий" value={totalSessions} icon="📋" color="border-primary/20 bg-primary-light/40 text-primary" />
        <StatCard label="Активные" value={activeSessions} icon="🟢" color="border-accent-teal/20 bg-accent-teal/10 text-accent-teal" />
        <StatCard label="Участники" value={totalParticipants} icon="👥" color="border-accent-yellow/20 bg-accent-yellow/10 text-accent-yellow" />
        <StatCard label="Завершили тест" value={totalCompleted} icon="✅" color="border-accent-pink/20 bg-accent-pink/10 text-accent-pink" />
      </div>

      {error && (
        <div className="bg-red-50 border-2 border-red-100 text-accent-red text-sm px-4 py-3 rounded-2xl mb-6 font-medium animate-pop-in">
          🤔 {error}
        </div>
      )}

      {/* Create Session Form */}
      {showCreate && (
        <div className="bg-white rounded-3xl border-2 border-surface-border p-6 md:p-8 mb-8 shadow-bouncy animate-pop-in">
          <h2 className="text-xl font-heading font-extrabold text-text-dark mb-6 flex items-center gap-2">
            <span>Новая сессия тестирования</span>
            <span className="text-lg">✏️</span>
          </h2>
          
          <div className="space-y-5">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-text-secondary mb-2">
                Название сессии *
              </label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="Например: Отбор дизайнеров Q3 2026"
                className="w-full px-4 py-3 border-2 border-surface-border rounded-2xl text-text-dark focus:outline-none focus:border-primary transition-colors bg-surface-bg/30 focus:bg-white text-base"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-text-secondary mb-2">
                Описание сессии
              </label>
              <textarea
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="Укажите дополнительную информацию для участников..."
                rows={3}
                className="w-full px-4 py-3 border-2 border-surface-border rounded-2xl text-text-dark focus:outline-none focus:border-primary transition-colors bg-surface-bg/30 focus:bg-white text-base resize-none"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-text-secondary mb-2">
                Количество вопросов
              </label>
              <select
                value={newQuestionsCount}
                onChange={(e) => setNewQuestionsCount(parseInt(e.target.value))}
                className="px-4 py-3 border-2 border-surface-border rounded-2xl text-text-dark focus:outline-none focus:border-primary transition-colors bg-surface-bg/30 focus:bg-white text-base font-bold"
              >
                <option value={30}>30 вопросов (быстрое экспресс-тестирование, ~8 мин)</option>
                <option value={60}>60 вопросов (профессиональный полный тест, ~15 мин)</option>
              </select>
            </div>
            
            <div className="flex gap-3 pt-2">
              <button
                onClick={handleCreate}
                disabled={creating || !newTitle.trim()}
                className="px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-full btn-pop transition-all text-sm font-bold disabled:opacity-50"
              >
                {creating ? "Создаем..." : "Создать сессию"}
              </button>
              <button
                onClick={() => setShowCreate(false)}
                className="px-6 py-3 bg-white border-2 border-surface-border text-text-dark hover:bg-surface-bg rounded-full btn-pop-white transition-all text-sm font-bold"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sessions List */}
      <div className="bg-white rounded-3xl border-2 border-surface-border shadow-sm overflow-hidden mb-8">
        <div className="px-6 py-5 border-b border-surface-border bg-surface-bg/30">
          <h2 className="text-xl font-heading font-extrabold text-text-dark">Все активные и закрытые сессии</h2>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-text-secondary text-sm font-medium">Получаем список сессий...</p>
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-16 px-4">
            <div className="text-4xl mb-4">🔮</div>
            <p className="text-text-secondary text-lg font-bold mb-1">Пока нет созданных сессий</p>
            <p className="text-text-light text-sm max-w-sm mx-auto mb-6">
              Создайте вашу первую сессию тестирования с помощью кнопки в верхнем углу, чтобы пригласить участников!
            </p>
            <button
              onClick={() => setShowCreate(true)}
              className="px-6 py-3 bg-primary hover:bg-primary-hover text-white font-heading font-bold rounded-full btn-pop transition-transform"
            >
              Создать первую сессию
            </button>
          </div>
        ) : (
          <div className="divide-y divide-surface-border">
            {sessions.map((session) => (
              <SessionRow key={session.id} session={session} onRefresh={loadSessions} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: number;
  icon: string;
  color: string;
}

function StatCard({ label, value, icon, color }: StatCardProps) {
  return (
    <div className="bg-white rounded-3xl border-2 border-surface-border p-5 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-bold uppercase tracking-wider text-text-secondary">{label}</span>
        <span className={`w-8 h-8 rounded-xl border flex items-center justify-center text-lg ${color}`}>
          {icon}
        </span>
      </div>
      <p className="text-3xl font-heading font-extrabold text-text-dark">{value}</p>
    </div>
  );
}

function SessionRow({ session, onRefresh }: { session: TestSession; onRefresh: () => void }) {
  const [copying, setCopying] = useState(false);
  const isActive = session.status === "active";
  const completionRate =
    session.participants_count > 0
      ? Math.round((session.completed_count / session.participants_count) * 100)
      : 0;

  const copyInviteCode = async () => {
    setCopying(true);
    await navigator.clipboard.writeText(session.invite_code);
    setTimeout(() => setCopying(false), 1500);
  };

  const handleToggleStatus = async () => {
    try {
      await api.updateSessionStatus(session.id, isActive ? "closed" : "active");
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  const createdDate = new Date(session.created_at).toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <div className="px-6 py-5 hover:bg-surface-bg/30 transition-colors duration-150 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-3 mb-1.5">
          <a
            href={`/admin/session/${session.id}`}
            className="font-heading font-extrabold text-text-dark hover:text-primary transition-colors text-lg truncate"
          >
            {session.title}
          </a>
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
        <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-sm font-medium text-text-secondary">
          <span className="flex items-center gap-1">📅 {createdDate}</span>
          <span className="flex items-center gap-1">✍️ {session.questions_count} вопросов</span>
          <span className="flex items-center gap-1">
            👥 {session.completed_count}/{session.participants_count} завершили
            {session.participants_count > 0 && ` (${completionRate}%)`}
          </span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 shrink-0">
        {/* Invite code */}
        <button
          onClick={copyInviteCode}
          className="flex items-center gap-2 px-4 py-2 bg-surface-bg border-2 border-surface-border rounded-xl text-base font-mono font-bold hover:bg-white hover:border-primary transition-colors group relative"
          title="Скопировать код приглашения"
        >
          <span className="text-primary tracking-wider">{session.invite_code}</span>
          <span className="text-text-light text-sm transition-transform duration-200 group-hover:scale-110">
            {copying ? "✓ Скопирован!" : "📋"}
          </span>
        </button>

        {/* Toggle status */}
        <button
          onClick={handleToggleStatus}
          className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide border transition-all ${
            isActive
              ? "bg-red-50 text-accent-red border-red-200 hover:bg-red-100"
              : "bg-green-50 text-accent-green border-green-200 hover:bg-green-100"
          }`}
        >
          {isActive ? "Закрыть" : "Открыть"}
        </button>

        {/* View details */}
        <a
          href={`/admin/session/${session.id}`}
          className="px-4 py-2 bg-primary/10 text-primary border border-primary/20 rounded-full text-xs font-bold uppercase tracking-wide hover:bg-primary hover:text-white transition-all"
        >
          Результаты →
        </a>
      </div>
    </div>
  );
}
