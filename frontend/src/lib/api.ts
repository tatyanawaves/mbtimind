/**
 * API client for MBTI Platform backend.
 * Proxied through Next.js rewrites -> localhost:8000
 */

const API_BASE = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// --- Types ---

export interface TestSession {
  id: string;
  title: string;
  description?: string;
  status: string;
  invite_code: string;
  questions_count: number;
  time_limit_minutes?: number;
  created_at: string;
  participants_count: number;
  completed_count: number;
}

export interface StartTestResponse {
  attempt_id: string;
  session_title: string;
  total_questions: number;
  time_limit_minutes?: number;
}

export interface Question {
  id: string;
  text_ru: string;
  option_a_ru: string;
  option_b_ru: string;
  index: number;
}

export interface QuestionsResponse {
  questions: Question[];
  current_index: number;
  total_questions: number;
  is_last_batch: boolean;
}

export interface ScaleScore {
  scale: string;
  positive_label: string;
  negative_label: string;
  positive_count: number;
  negative_count: number;
  percentage: number;
  dominant: string;
}

export interface TestResult {
  attempt_id: string;
  mbti_type: string;
  confidence_score: number;
  scales: ScaleScore[];
  is_valid: boolean;
  completed_at?: string;
  type_name_ru?: string;
  type_description_ru?: string;
  career_recommendations?: string[];
}

// --- Admin types ---

export interface Participant {
  attempt_id: string;
  user_name: string;
  user_email?: string;
  status: string;
  started_at: string;
  completed_at?: string;
  mbti_type?: string;
  confidence_score?: number;
}

export interface SessionDetail extends TestSession {
  participants: Participant[];
}

// --- API calls ---

export const api = {
  /** Join a test session by invite code */
  joinSession(invite_code: string, full_name: string, email?: string) {
    return request<StartTestResponse>("/sessions/join", {
      method: "POST",
      body: JSON.stringify({ invite_code, full_name, email }),
    });
  },

  /** Get next batch of questions */
  getQuestions(attempt_id: string, count = 5) {
    return request<QuestionsResponse>(
      `/questions/next?attempt_id=${attempt_id}&count=${count}`
    );
  },

  /** Submit a single answer */
  submitAnswer(attempt_id: string, question_id: string, selected_option: "a" | "b", response_time_ms: number) {
    return request<{ status: string; progress: number }>(
      `/results/${attempt_id}/answers`,
      {
        method: "POST",
        body: JSON.stringify({ question_id, selected_option, response_time_ms }),
      }
    );
  },

  /** Complete test and get result */
  completeTest(attempt_id: string) {
    return request<TestResult>(`/results/${attempt_id}/complete`, {
      method: "POST",
    });
  },

  /** Get existing result */
  getResult(attempt_id: string) {
    return request<TestResult>(`/results/${attempt_id}`);
  },

  // --- Admin API ---

  /** Create a new test session */
  createSession(data: { title: string; description?: string; questions_count?: number; time_limit_minutes?: number }) {
    return request<TestSession>("/sessions/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /** List all sessions */
  listSessions() {
    return request<TestSession[]>("/sessions/");
  },

  /** Get session detail with participants */
  getSessionDetail(session_id: string) {
    return request<SessionDetail>(`/sessions/${session_id}/detail`);
  },

  /** Update session status (close/reactivate) */
  updateSessionStatus(session_id: string, new_status: "active" | "closed") {
    return request<{ status: string }>(`/sessions/${session_id}/status?new_status=${new_status}`, {
      method: "PATCH",
    });
  },
};
