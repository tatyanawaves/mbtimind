# System Design: Test Engine Module

**Модуль:** Test Engine (Ядро тестирования)  
**Платформа:** MBTI Psychometric Testing SaaS  
**Дата:** 2026-05-20  
**Автор:** Claude (System Architect)

---

## 1. Requirements

### 1.1 Functional Requirements

- **FR-1:** Пользователь начинает тестирование и получает вопросы последовательно или постранично
- **FR-2:** Система поддерживает forced-choice формат (выбор между двумя утверждениями)
- **FR-3:** Сессия сохраняется — пользователь может прервать и продолжить позже
- **FR-4:** По завершении теста автоматически рассчитывается MBTI-тип (4 шкалы, 16 типов)
- **FR-5:** Генерируется детальный профиль: сильные/слабые стороны, паттерны, стресс-триггеры
- **FR-6:** Поддержка нескольких типов тестов: MBTI Standard (взрослые), MBTI Teen (14+), Holland (будущее)
- **FR-7:** Администратор может настраивать параметры теста: time limit, randomization, количество вопросов
- **FR-8:** Контрольные шкалы для обнаружения случайных ответов и социальной желательности

### 1.2 Non-Functional Requirements

| Requirement | Target (MVP) | Target (Scale) |
|-------------|-------------|----------------|
| Concurrent sessions | 50 | 10 000 |
| Response latency (next question) | < 200ms | < 100ms |
| Session persistence | 7 дней | 30 дней |
| Test completion rate | Мониторинг | > 85% |
| Data durability | 99.9% | 99.99% |
| Availability | 99% | 99.9% |

### 1.3 Constraints

- Stack: FastAPI (Python 3.12+), PostgreSQL 16, Redis 7
- Модульный монолит (ADR-001)
- Data residency: Казахстан
- Команда: 2-5 разработчиков
- Timeline: 3 недели на MVP Test Engine

---

## 2. High-Level Design

### 2.1 Component Diagram

```
                    ┌─────────────────┐
                    │   Client Apps   │
                    │ (Web / Mobile)  │
                    └───────┬─────────┘
                            │ HTTPS
                    ┌───────▼─────────┐
                    │   API Gateway   │
                    │  (Auth, RBAC,   │
                    │   Rate Limit)   │
                    └───────┬─────────┘
                            │
              ┌─────────────▼──────────────┐
              │       TEST ENGINE MODULE    │
              │                            │
              │  ┌──────────────────────┐  │
              │  │   Session Manager    │  │
              │  │  (create, resume,    │  │
              │  │   pause, complete)   │  │
              │  └──────────┬───────────┘  │
              │             │              │
              │  ┌──────────▼───────────┐  │
              │  │  Question Sequencer  │  │
              │  │  (ordering, paging,  │  │
              │  │   adaptive/fixed)    │  │
              │  └──────────┬───────────┘  │
              │             │              │
              │  ┌──────────▼───────────┐  │
              │  │   Answer Collector   │  │
              │  │  (validation, timing │  │
              │  │   metadata capture)  │  │
              │  └──────────┬───────────┘  │
              │             │              │
              │  ┌──────────▼───────────┐  │
              │  │   Scoring Engine     │  │
              │  │  (scale calculation, │  │
              │  │   type assignment,   │  │
              │  │   confidence score)  │  │
              │  └──────────┬───────────┘  │
              │             │              │
              │  ┌──────────▼───────────┐  │
              │  │  Integrity Checker   │  │
              │  │  (L-scale, timing,   │  │
              │  │   pattern detection) │  │
              │  └─────────────────────┘  │
              └────────────────────────────┘
                     │           │
           ┌─────────▼──┐  ┌────▼─────┐
           │ PostgreSQL  │  │  Redis   │
           │ (sessions,  │  │ (active  │
           │  results,   │  │  session │
           │  questions) │  │  cache)  │
           └─────────────┘  └──────────┘
```

### 2.2 Data Flow

```
1. Client → POST /api/v1/tests/sessions          → Session Manager creates session
2. Client → GET  /api/v1/tests/sessions/{id}/next → Question Sequencer returns question(s)
3. Client → POST /api/v1/tests/sessions/{id}/answers → Answer Collector stores answer
4. [Repeat 2-3 until all questions answered]
5. Client → POST /api/v1/tests/sessions/{id}/complete → Scoring Engine computes result
6. Scoring Engine → Integrity Checker validates → Result stored
7. Event emitted: test.completed → (Recommendation Module subscribes)
```

---

## 3. API Design

### 3.1 Endpoints

```
# Test Management (Admin)
GET    /api/v1/tests                          → List available tests
GET    /api/v1/tests/{test_id}                → Get test metadata
PUT    /api/v1/tests/{test_id}/config         → Update test configuration

# Session Lifecycle
POST   /api/v1/tests/sessions                 → Start new test session
GET    /api/v1/tests/sessions/{session_id}    → Get session status & progress
DELETE /api/v1/tests/sessions/{session_id}    → Abandon session

# Question Flow
GET    /api/v1/tests/sessions/{sid}/questions?page=1&size=10  → Get questions (paged)
GET    /api/v1/tests/sessions/{sid}/next      → Get next unanswered question(s)

# Answer Submission
POST   /api/v1/tests/sessions/{sid}/answers   → Submit answer(s) (batch)
PUT    /api/v1/tests/sessions/{sid}/answers/{qid} → Change answer (if allowed)

# Completion & Results
POST   /api/v1/tests/sessions/{sid}/complete  → Finalize and score
GET    /api/v1/tests/results/{result_id}      → Get detailed result
GET    /api/v1/tests/results/me               → Current user's results history
```

### 3.2 Key Request/Response Schemas

**Start Session:**
```json
// POST /api/v1/tests/sessions
// Request:
{
  "test_type": "MBTI_STANDARD",   // MBTI_STANDARD | MBTI_TEEN | HOLLAND
  "language": "ru",                // ru | kz | en
  "mode": "FULL"                   // FULL (93 questions) | QUICK (48 questions)
}

// Response: 201 Created
{
  "session_id": "uuid",
  "test_type": "MBTI_STANDARD",
  "total_questions": 93,
  "estimated_minutes": 15,
  "expires_at": "2026-05-27T12:00:00Z",
  "status": "IN_PROGRESS"
}
```

**Get Next Questions:**
```json
// GET /api/v1/tests/sessions/{sid}/next?count=5
// Response:
{
  "questions": [
    {
      "id": "q_042",
      "order": 42,
      "scale": null,              // hidden from client
      "format": "FORCED_CHOICE",
      "options": [
        {"key": "A", "text": "Вам легче работать в команде"},
        {"key": "B", "text": "Вам легче работать самостоятельно"}
      ]
    }
  ],
  "progress": {
    "answered": 41,
    "total": 93,
    "percent": 44.1
  }
}
```

**Submit Answers (Batch):**
```json
// POST /api/v1/tests/sessions/{sid}/answers
// Request:
{
  "answers": [
    {
      "question_id": "q_042",
      "selected": "A",
      "response_time_ms": 3420    // client-measured
    }
  ]
}

// Response: 200 OK
{
  "accepted": 1,
  "progress": { "answered": 42, "total": 93, "percent": 45.2 }
}
```

**Complete & Get Result:**
```json
// POST /api/v1/tests/sessions/{sid}/complete
// Response: 200 OK
{
  "result_id": "uuid",
  "mbti_type": "INTJ",
  "scales": {
    "E_I": { "E": 32, "I": 68, "dominant": "I", "clarity": "CLEAR" },
    "S_N": { "S": 25, "N": 75, "dominant": "N", "clarity": "VERY_CLEAR" },
    "T_F": { "T": 71, "F": 29, "dominant": "T", "clarity": "CLEAR" },
    "J_P": { "J": 63, "P": 37, "dominant": "J", "clarity": "MODERATE" }
  },
  "confidence_score": 0.87,
  "integrity": {
    "status": "VALID",
    "flags": []
  },
  "profile": {
    "summary": "...",
    "strengths": ["..."],
    "weaknesses": ["..."],
    "stress_triggers": ["..."],
    "communication_style": "...",
    "work_preferences": "..."
  },
  "completed_at": "2026-05-20T14:32:00Z"
}
```

---

## 4. Data Model

### 4.1 Core Tables

```sql
-- Шаблоны тестов (admin-managed)
CREATE TABLE test_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(30) NOT NULL,          -- MBTI_STANDARD, MBTI_TEEN, HOLLAND
    version VARCHAR(20) NOT NULL,
    name_ru TEXT NOT NULL,
    name_kz TEXT,
    name_en TEXT,
    config JSONB NOT NULL DEFAULT '{}',  -- time_limit, randomize, allow_back, etc.
    scoring_algorithm VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Банк вопросов
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID REFERENCES test_templates(id),
    order_index INT NOT NULL,
    scale VARCHAR(10) NOT NULL,         -- E_I, S_N, T_F, J_P, L (control)
    pole VARCHAR(5) NOT NULL,           -- E, I, S, N, T, F, J, P
    format VARCHAR(20) DEFAULT 'FORCED_CHOICE',
    text_ru JSONB NOT NULL,             -- {"A": "...", "B": "..."}
    text_kz JSONB,
    text_en JSONB,
    weight FLOAT DEFAULT 1.0,           -- для адаптивного тестирования
    difficulty FLOAT,                   -- IRT parameter (future)
    is_control BOOLEAN DEFAULT false,   -- control scale question
    UNIQUE(template_id, order_index)
);

-- Сессии прохождения
CREATE TABLE test_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,              -- FK to users
    org_id UUID NOT NULL,               -- FK to organizations (tenant)
    template_id UUID REFERENCES test_templates(id),
    status VARCHAR(20) DEFAULT 'IN_PROGRESS',  -- IN_PROGRESS, COMPLETED, ABANDONED, EXPIRED
    language VARCHAR(5) DEFAULT 'ru',
    mode VARCHAR(20) DEFAULT 'FULL',
    question_order JSONB,               -- shuffled order of question IDs
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    environment JSONB,                  -- device, browser, IP hash
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Ответы (append-only)
CREATE TABLE session_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES test_sessions(id),
    question_id UUID REFERENCES questions(id),
    selected VARCHAR(5) NOT NULL,       -- A or B
    response_time_ms INT,               -- time to answer
    changed_count INT DEFAULT 0,        -- how many times changed
    answered_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(session_id, question_id)
);

-- Результаты
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID UNIQUE REFERENCES test_sessions(id),
    user_id UUID NOT NULL,
    org_id UUID NOT NULL,
    mbti_type CHAR(4) NOT NULL,         -- INTJ, ENFP, etc.
    scale_scores JSONB NOT NULL,        -- {E_I: {E:32, I:68}, ...}
    confidence_score FLOAT NOT NULL,
    integrity_status VARCHAR(20),       -- VALID, SUSPECT, INVALID
    integrity_flags JSONB DEFAULT '[]',
    profile JSONB NOT NULL,             -- full personality profile
    scoring_version VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Row Level Security for multitenancy
ALTER TABLE test_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_sessions ON test_sessions
    USING (org_id = current_setting('app.current_org_id')::UUID);

CREATE POLICY tenant_isolation_results ON test_results
    USING (org_id = current_setting('app.current_org_id')::UUID);

-- Indexes
CREATE INDEX idx_sessions_user ON test_sessions(user_id, status);
CREATE INDEX idx_sessions_org ON test_sessions(org_id, created_at DESC);
CREATE INDEX idx_results_user ON test_results(user_id, created_at DESC);
CREATE INDEX idx_results_org_type ON test_results(org_id, mbti_type);
CREATE INDEX idx_answers_session ON session_answers(session_id);
```

---

## 5. Scoring Engine — Deep Dive

### 5.1 Алгоритм подсчёта MBTI

```python
# Pseudocode: MBTI Scoring Algorithm

def score_mbti(session: TestSession, answers: list[Answer]) -> MBTIResult:
    # 1. Group answers by scale
    scale_answers = group_by_scale(answers)  # {E_I: [...], S_N: [...], ...}
    
    # 2. Calculate raw scores per pole
    scales = {}
    for scale_name, scale_data in scale_answers.items():
        pole_a, pole_b = get_poles(scale_name)  # E/I, S/N, T/F, J/P
        
        score_a = sum(
            q.weight for q in scale_data
            if q.selected_pole == pole_a
        )
        score_b = sum(
            q.weight for q in scale_data
            if q.selected_pole == pole_b
        )
        
        total = score_a + score_b
        pct_a = round(score_a / total * 100) if total > 0 else 50
        pct_b = 100 - pct_a
        
        # 3. Determine clarity
        diff = abs(pct_a - pct_b)
        clarity = (
            "VERY_CLEAR" if diff > 40 else
            "CLEAR" if diff > 20 else
            "MODERATE" if diff > 10 else
            "SLIGHT"
        )
        
        dominant = pole_a if pct_a > pct_b else pole_b
        scales[scale_name] = ScaleResult(
            pole_a_score=pct_a, pole_b_score=pct_b,
            dominant=dominant, clarity=clarity
        )
    
    # 4. Compose MBTI type
    mbti_type = "".join(s.dominant for s in scales.values())
    
    # 5. Calculate confidence score
    confidence = calculate_confidence(scales, answers)
    
    # 6. Generate profile from type database
    profile = generate_profile(mbti_type, scales)
    
    return MBTIResult(
        mbti_type=mbti_type,
        scales=scales,
        confidence_score=confidence,
        profile=profile
    )
```

### 5.2 Confidence Score (Индекс достоверности)

Confidence score (0-1) комбинирует три фактора:

```
confidence = 0.4 * scale_clarity + 0.3 * timing_consistency + 0.3 * integrity_score

scale_clarity:     средняя clarity по 4 шкалам (VERY_CLEAR=1, CLEAR=0.8, MODERATE=0.6, SLIGHT=0.4)
timing_consistency: 1 - (std_dev(response_times) / mean(response_times)), clamped [0, 1]
integrity_score:   результат Integrity Checker (L-шкала + pattern detection)
```

---

## 6. Integrity Checker (Anti-Cheating)

### 6.1 Механизмы защиты

| Механизм | Реализация | Когда срабатывает |
|----------|------------|-------------------|
| **L-шкала (ложь)** | 10 контрольных вопросов с заведомо "правильным" ответом | > 7 из 10 "правильных" → flag SOCIAL_DESIRABILITY |
| **Speed detection** | Минимальное время ответа: 1.5 секунды | > 30% ответов < 1.5s → flag RANDOM_CLICKING |
| **Flat pattern** | Один и тот же ответ (A или B) подряд | > 10 одинаковых подряд → flag FLAT_PATTERN |
| **Alternating pattern** | Чередование A-B-A-B | > 15 чередований подряд → flag ALTERNATING |
| **Total time** | Общее время < 5 минут для 93 вопросов | → flag IMPOSSIBLY_FAST |
| **Midpoint bias** | Для шкал с gradual scale: все ответы в середине | > 80% нейтральных → flag MIDPOINT_BIAS |

### 6.2 Integrity Status

```
VALID:   0 flags                          → результат достоверен
SUSPECT: 1-2 minor flags                  → результат показывается с предупреждением
INVALID: 3+ flags или 1 critical flag     → рекомендуется повторное тестирование
```

Critical flags: RANDOM_CLICKING, IMPOSSIBLY_FAST  
Minor flags: SOCIAL_DESIRABILITY, FLAT_PATTERN, ALTERNATING, MIDPOINT_BIAS

---

## 7. Caching Strategy

### 7.1 Redis Usage

```
# Active session state (hot data)
test:session:{session_id}          → JSON {status, progress, current_question}
                                     TTL: 2 hours (refreshed on activity)

# Question bank cache (read-heavy)
test:template:{template_id}:questions → JSON array of questions
                                       TTL: 24 hours (invalidate on admin update)

# Rate limiting per user
test:ratelimit:{user_id}           → counter
                                     TTL: 60 seconds, max 30 requests

# Session lock (prevent concurrent modifications)
test:lock:{session_id}             → user_id
                                     TTL: 30 seconds (released on response)
```

### 7.2 Cache Invalidation

- Question bank: invalidate on `PUT /tests/{id}/config` (admin action, rare)
- Session cache: write-through (every answer updates Redis + async write to PostgreSQL)
- Results: not cached in Redis (read from PostgreSQL, cached at API Gateway level)

---

## 8. Error Handling

| Scenario | HTTP Code | Behavior |
|----------|-----------|----------|
| Session expired | 410 Gone | Return partial progress, suggest restart |
| Duplicate answer | 409 Conflict | Return current state, idempotent |
| Session already completed | 422 | Return result_id |
| Invalid question_id | 400 | Validation error with details |
| Concurrent session modification | 429 | Redis lock prevents, retry after |
| DB write failure | 500 | Answer saved in Redis, async retry to PostgreSQL |
| Scoring failure | 500 | Session marked PENDING_SCORING, background retry |

**Retry strategy:** exponential backoff for DB writes (1s, 2s, 4s, max 3 retries)

---

## 9. Events (Internal Event Bus)

```python
# Events emitted by Test Engine

class TestSessionStarted:
    session_id: UUID
    user_id: UUID
    org_id: UUID
    test_type: str

class TestSessionCompleted:
    session_id: UUID
    result_id: UUID
    user_id: UUID
    org_id: UUID
    mbti_type: str
    confidence_score: float

class TestSessionAbandoned:
    session_id: UUID
    user_id: UUID
    progress_percent: float
    
class TestIntegrityAlert:
    session_id: UUID
    user_id: UUID
    flags: list[str]
    severity: str  # MINOR, CRITICAL
```

**Subscribers:**
- `TestSessionCompleted` → Recommendation Module (generates career matches)
- `TestSessionCompleted` → Notification Module (sends results email/telegram)
- `TestSessionCompleted` → Analytics Module (updates ClickHouse aggregates)
- `TestIntegrityAlert` → Notification Module (alerts psychologist/admin)
- `TestSessionAbandoned` → Notification Module (reminder to continue)

---

## 10. Scale & Performance

### 10.1 Load Estimation (12 месяцев)

```
50,000 tests/month ÷ 22 working days = ~2,300 tests/day
Peak: 3x average = ~7,000 tests/day
Peak hour: 40% of daily = ~2,800 tests/hour = ~47 tests/minute

Per test: ~93 answers = ~93 API calls over 15 minutes
Peak API calls: 47 × 93 / 15 = ~290 requests/minute ≈ 5 RPS

Conclusion: Single FastAPI instance handles this easily (FastAPI: 5,000+ RPS)
```

### 10.2 Scaling Strategy

| Load tier | Architecture | Infrastructure |
|-----------|-------------|----------------|
| MVP (500 tests/mo) | Single instance | 1 VPS, Docker Compose |
| Growth (50K tests/mo) | 2 replicas behind Nginx | 2 VPS, load balancer |
| Scale (500K tests/mo) | Test Engine → separate service | Kubernetes, horizontal pod autoscaler |
| Enterprise (5M+ tests/mo) | Full microservices | K8s multi-node, read replicas, sharding |

### 10.3 Database Growth

```
Per test: ~5KB (session) + ~10KB (93 answers) + ~8KB (result) = ~23KB
50K tests/month = ~1.15GB/month
1 year = ~14GB → PostgreSQL handles this trivially
```

---

## 11. Security Considerations

- **Question leakage:** Questions never include scale/pole info in API response
- **Answer tampering:** Answers are append-only, changes tracked via `changed_count`
- **Session hijacking:** Session bound to user_id + JWT, validated on every request
- **Timing attacks:** `response_time_ms` is client-reported but cross-checked with server timestamps
- **Data export:** Psychometric results require explicit consent and org admin approval
- **Minor protection:** Sessions for users with `is_minor=true` require guardian consent pre-check

---

## 12. What to Revisit

- **Adaptive testing (IRT):** При накоплении данных (>10K тестов) — переход от фиксированного набора к адаптивному подбору вопросов через Item Response Theory
- **Question rotation:** Создание параллельных форм теста для снижения запоминания вопросов
- **Real-time proctoring:** При высоких ставках (сертификация) — интеграция с камерой/screen monitoring
- **A/B testing:** Тестирование разных формулировок вопросов и их влияния на reliability (alpha Кронбаха)
- **Offline mode (Flutter):** Полное прохождение теста без интернета с последующей синхронизацией
