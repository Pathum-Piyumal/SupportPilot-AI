# SupportPilot AI — Complete Engineering Master Plan

> **Version:** 1.0 | **Date:** 2026-11-16 | **Status:** Planned  
> **Owner:** Solo third-year Software Engineering undergraduate  
> **Duration / capacity:** 12 weeks, ~12–15 focused hours/week (144–180 hours)  
> **Domain:** Fictional banking customer-support operations  
> **Primary outcome:** A reproducible, interview-ready Hybrid ML + GenAI full-stack product.  
> **Companion:** [PROJECT_PROPOSAL.md](./PROJECT_PROPOSAL.md)

## 0. How to use this plan

- Treat each **CHUNK** as a releasable implementation unit, not just a learning topic.
- Complete tasks in order while respecting dependencies. Use task IDs in GitHub Issues and branch/PR descriptions.
- Every task is initially unchecked (`[ ]`). Check it only after its acceptance criteria are met.
- Prioritize tasks marked **P0** (blocking MVP). **P1** improves quality; **P2** is stretch work.
- Do not start microservices, an autonomous multi-agent framework, real bank integration or model fine-tuning unless all P0 tasks are done.
- At the end of each week, record **done / blocker / evidence / next** in `docs/progress/week-NN.md`.
- Each chunk below defines a deliverable and a release gate that can be tested, rather than merely claiming completion.

### End-to-end product journey

1. Agent signs in using a demo account.
2. Agent creates/opens a ticket containing synthetic customer text.
3. Backend invokes a versioned sklearn model and returns predicted intent + confidence + review flag.
4. Agent requests a drafted answer; retriever fetches passages from versioned **fictional bank policy** documents.
5. LLM creates an answer using only supplied evidence, or explicitly indicates insufficient support.
6. UI displays answer, passages/citations, model metadata and warning when applicable.
7. Agent edits, approves or rejects; backend stores the reviewed draft and audit events.
8. Dashboard reports ticket and review metrics; separate model report shows offline ML/RAG quality.

**Safety/product boundary:** No real banking customer data, no automatic bank operations, no outbound automated communication, no credential access, no real financial advice. Demo policies are fictional and clearly marked. BANKING77 is for intent labels, not SLA prediction, priority labels or measured labor savings.

---

# 1. Vision, requirements and success measures

## 1.1 Personas and permissions

| Persona | Main operations | Access boundaries |
|---|---|---|
| Agent | Create/view assigned demo tickets, see predictions, request/edit/approve/reject drafts | Tickets assigned to self or within explicit demo team scope |
| Admin | Manage demo users and policy versions, view all tickets and dashboard | Administrative routes only |
| ML Maintainer (developer CLI) | Train/evaluate/promote versioned models | Not exposed as a user-facing public API in MVP |

**RBAC enforcement must occur on the backend**. A hidden frontend button is not authorization. Every resource lookup must validate role and ticket ownership/team scope.

## 1.2 Functional requirements (FR)

| ID | P | Requirement | Evidence of completion |
|---|---|---|---|
| FR-01 | P0 | Agent/admin authentication and role checks | Unauthorized role gets 403; unauthenticated gets 401 |
| FR-02 | P0 | Create/list/get/update demo tickets | API tests and working inbox UI |
| FR-03 | P0 | Classify request with trained intent model | Stable prediction schema + test |
| FR-04 | P0 | Persist prediction with model version | Database record visible in ticket detail |
| FR-05 | P0 | Ingest/version policy documents | Admin upload/job and searchable chunk records |
| FR-06 | P0 | Retrieve source passages | Known retrieval fixture returns correct source IDs |
| FR-07 | P0 | Generate draft with verifiable citations or abstain | Evaluated positive/negative examples |
| FR-08 | P0 | Human review/edit/approve/reject | Audit events, permission and status tests |
| FR-09 | P0 | Dashboard with ticket/review metrics | Correct aggregate SQL and UI |
| FR-10 | P0 | Local reproducibility and CI | Fresh clone setup + green CI |
| FR-11 | P1 | Agent correction of intent | `corrected_intent` stored for future approved training |
| FR-12 | P1 | Model drift / performance monitoring | Basic drift report on demo batch |
| FR-13 | P2 | Advanced classifier | Measured gain against baseline on validation |

## 1.3 Non-functional requirements (NFR)

- **Security:** Password hashing (Argon2 or bcrypt), short-lived access tokens or secure sessions, server-side RBAC, input validation, parameterized SQL/ORM, secrets in env, rate limits on costly endpoints, content/file limits, audit records.
- **Reliability:** Error responses with trace IDs, timeouts and bounded retries for external LLM, idempotent ingestion, health checks, no request-time model training.
- **Performance:** Define and measure p50/p95 on a fixed local machine. Suggested **targets to measure, not promised outcomes**: classification API p95 < 500 ms after warmup and ordinary ticket endpoints p95 < 1 s on local demo load; LLM draft latency recorded separately.
- **Observability:** JSON application logs (excluding raw sensitive text), request IDs, inference times, LLM token/cost estimates, ingestion results, error classes.
- **Maintainability:** Typed schema contracts, modular monolith boundaries, tests, migrations and ADRs.
- **Reproducibility:** Lock dependency versions, fixed random seeds, dataset documentation, artifact version, Docker Compose commands and deterministic mock LLM for tests.
- **Accessibility:** Keyboard-operable controls, visible loading/error/empty states, readable contrast, labels, responsive layout.
- **Privacy:** Synthetic demo tickets only; minimize data; never log secrets or full request bodies by default.

## 1.4 Explicit non-goals

- No production banking claims, customer account access, transfer/refund execution, automatic customer messages, real bank APIs, or regulated customer data.
- No SLA/urgency predictions learned from BANKING77 (no such labels supplied).
- No unvalidated “AI risk score,” legal/financial compliance assertion, or unsupported accuracy guarantee.
- No Kubernetes, Kafka, separate microservices, complex multi-agent autonomy, or fine-tuning LLMs in MVP.

## 1.5 Definition of Done (every task)

- [ ] Behavior meets written acceptance criteria and negative/error paths were considered.
- [ ] Tests included/updated; lint, typing and CI checks pass.
- [ ] Authentication, authorization, data handling and prompt-injection implications reviewed.
- [ ] Contracts, docs, diagrams and fixtures updated when changed.
- [ ] Relevant manual demo path verified; no hard-coded secrets or private data.
- [ ] PR/commit references task ID; screenshot/log/test result attached to issue.

---

# 2. Technical architecture and boundaries

## 2.1 Architecture choice: modular monolith

```mermaid
flowchart LR
  A[Agent / Admin - React + TypeScript] -->|HTTPS / JSON| B[FastAPI - modular monolith]
  B --> C[Auth + RBAC]
  B --> D[Ticket + Review Services]
  B --> E[Intent Inference Service]
  B --> F[RAG Drafting Service]
  C --> G[(PostgreSQL)]
  D --> G
  E --> H[Versioned sklearn Pipeline]
  E --> G
  F --> I[(pgvector + knowledge chunks)]
  F --> J[LLM provider adapter]
  F --> G
  K[Offline BANKING77 Training + MLflow] --> H
  L[Policy Ingest CLI / background job] --> I
```

**Rules:** API routers only validate/translate HTTP; services hold business rules; repositories handle persistence; inference loads a prebuilt model at application startup; RAG retrieval runs only on approved documents; the LLM is not allowed to update tickets/DB or execute SQL; agent review is mandatory. Training and ingestion are separate repeatable processes.

## 2.2 Exact recommended stack

| Layer | Selected technology | Rationale |
|---|---|---|
| Runtime | Python 3.12, Node.js current LTS (pin in repo) | Modern supported runtimes; document actual lock versions |
| Data/ML | pandas, NumPy, scikit-learn, joblib, MLflow | Reproducible NLP classification and experiments |
| Backend | FastAPI, Pydantic v2, pydantic-settings, Uvicorn | Typed REST endpoints and config |
| Persistence | PostgreSQL, SQLAlchemy 2.x, Alembic | Relational data and migrations |
| Vector search | pgvector; sentence-transformers embedding model pinned by exact ID/version | Single-database semantic retrieval |
| LLM | Configurable provider via a small `LLMClient` interface + deterministic fake | Avoid vendor lock-in and isolate cost/errors |
| Frontend | React, TypeScript, Vite, React Router, TanStack Query | Typed asynchronous UI |
| UI | Tailwind CSS or simple component library; choose once | Fast consistent interface |
| Backend QA | pytest, HTTPX, Ruff, mypy or Pyright | API/units/lint/types |
| Frontend QA | Vitest, React Testing Library, Playwright smoke test | UI correctness and end-to-end path |
| Delivery | Docker Compose, GitHub Actions | Local stack and CI |
| Diagrams/docs | Markdown, Mermaid, OpenAPI, ADRs | Reviewable architecture and decisions |

**Design simplifications:** Choose one LLM provider and one embeddings model for MVP. Use exact library releases in lockfiles after verifying compatibility. No LangGraph unless a genuine stateful orchestration requirement emerges.

## 2.3 Suggested repository layout

```text
supportpilot-ai/
├── apps/
│   ├── web/
│   │   ├── src/
│   │   │   ├── app/                 # router/providers
│   │   │   ├── features/
│   │   │   │   ├── auth/
│   │   │   │   ├── tickets/
│   │   │   │   ├── predictions/
│   │   │   │   ├── knowledge/
│   │   │   │   ├── drafts/
│   │   │   │   └── analytics/
│   │   │   ├── components/ui/
│   │   │   ├── lib/api-client.ts
│   │   │   └── styles/
│   │   ├── public/
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── api/v1/{auth,tickets,predictions,knowledge,drafts,analytics,health}.py
│       │   ├── core/{config,security,logging,exceptions}.py
│       │   ├── db/{base,session}.py
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── repositories/
│       │   ├── services/{tickets,prediction,retrieval,drafting,reviews}.py
│       │   └── integrations/{llm,embeddings}.py
│       ├── alembic/
│       ├── tests/{unit,integration,security}/
│       └── pyproject.toml
├── ml/
│   ├── src/supportpilot_ml/{data,features,train,evaluate,infer}.py
│   ├── tests/
│   └── configs/
├── knowledge/
│   ├── demo_policies/             # fictional; clearly watermarked
│   ├── fixtures/
│   └── evaluations/
├── data/
│   ├── README.md                   # source, access, usage, licensing
│   └── .gitkeep                   # large/raw data gitignored
├── artifacts/                     # gitignored model binaries
├── scripts/{seed_demo,ingest_policies,verify_release}.py
├── docs/
│   ├── adr/
│   ├── architecture.md
│   ├── api-contracts.md
│   ├── data-dictionary.md
│   ├── model-card.md
│   ├── ml-evaluation.md
│   ├── rag-evaluation.md
│   ├── security-threat-model.md
│   ├── deployment.md
│   └── progress/
├── .github/{workflows,ISSUE_TEMPLATE}/
├── docker-compose.yml
├── .env.example
├── README.md
├── PROJECT_PROPOSAL.md
└── MASTERPLAN.md
```

---

# 3. Data, evaluation and AI correctness policies

## 3.1 Dataset strategy

**Supervised classification:** BANKING77 (`PolyAI/banking77`), a published intent classification dataset with 77 banking intents. Pin the dataset revision and record train/test counts, checksum/snapshot, license and source. Use an internal development validation slice from the published train split; do **not** tune on the final published test split.

**Ticket workflow:** Generate **synthetic** ticket IDs, created times, users, assignment and statuses. If BANKING77 text is used as demo customer text, clearly mark it as dataset-derived; do not claim to possess real banking interactions. Use synthetic content for free-form tickets where appropriate.

**Knowledge base:** Author fictional, internally consistent sample bank help-center policies (transfers, card payments, refunds, disputes, security). Name the organization `DemoBank` and mark every document `SIMULATED POLICY — NOT REAL BANK ADVICE`. Version policy content. Never imply real bank authority.

**Data license/release checklist:** Verify original dataset terms before republishing any samples; document attribution, redistribution restrictions and generated content provenance. Do not commit large raw datasets or secret-bearing model logs.

## 3.2 ML methodology requirements

- Baseline A: majority-class/DummyClassifier.
- Baseline B: `TfidfVectorizer` + `LogisticRegression` in one sklearn `Pipeline` (prevents fitting leakage).
- Optional comparator: sentence embeddings + linear classifier (P1) if baseline is stable.
- Split: fixed train/validation only from published training data; published test remains untouched until model selection and calibration/threshold decisions are finalized.
- Record experiment config, seed, versions, confusion matrix, class support and inference latency.
- Metrics: accuracy, macro-F1, weighted-F1, per-class F1, top-k accuracy (if useful), confidence calibration (ECE/Brier if applicable), coverage vs. accuracy at abstention thresholds.
- Confidence is not proof of correctness. Log the margin/threshold and route uncertain predictions to manual review.
- Never claim an unmeasured performance score. Document test-set errors and dataset/domain limitations.
- Model loading: only load artifacts built/trusted by this repository; joblib/pickle formats are unsafe when obtained from untrusted sources. Pin artifact version/hash.

## 3.3 RAG and LLM policy

1. Ingest only explicitly approved fictional policy files; limit type and size; extract and normalize text; record document version and status.
2. Chunk passages with stable IDs, metadata and page/section references when available.
3. Embed with a pinned sentence-transformers model and record embedding model/version/dimension.
4. Retrieve top-k passages scoped to `approved=true` policy versions; optionally use keyword fallback if vector search is weak.
5. Build an instruction that treats retrieved passages and customer text as **untrusted data**, not commands.
6. Output structured JSON `{draft_text, citations, confidence_note, needs_human_review, unsupported}`. Validate with Pydantic, verify citation IDs are among retrieved chunks, and decline unsupported answers.
7. LLM cannot call arbitrary network, SQL, admin, transaction or notification tools.
8. Enforce token/input limits, request timeout, bounded retries, rate limit, and provider cost budget. Disable raw prompt/body logging by default.
9. Agents must edit/approve or reject drafts; never auto-send or auto-approve.
10. Evaluate retrieval and answer quality on a small gold set, including adversarial prompt injection and policy-conflict examples. Human review is mandatory for any generated financial-service wording.

## 3.4 Evaluation sets

- `ml/` holds **train/validation/test discipline** and results; final test metrics appear only after freeze.
- `knowledge/evaluations/rag_cases.jsonl`: at least 30 reviewed cases with question, expected source IDs, whether answerable, prohibited claims if applicable, and rationale.
- Track Recall@3/5, citation precision/validity, unsupported-answer behavior, and qualitative groundedness. A small human-scored sheet is acceptable; avoid claiming automatic judge scores as ground truth.
- Set *candidate acceptance thresholds* on validation cases before final assessment; document actual measured outcomes and changes.

---

# 4. Database plan (PostgreSQL + pgvector)

## 4.1 ERD relationships

```mermaid
erDiagram
  USERS ||--o{ TICKETS : assigned_to
  USERS ||--o{ AUDIT_EVENTS : actor
  TICKETS ||--o{ PREDICTIONS : has
  TICKETS ||--o{ DRAFTS : has
  DRAFTS ||--o{ DRAFT_CITATIONS : supports
  KNOWLEDGE_CHUNKS ||--o{ DRAFT_CITATIONS : referenced_by
  KNOWLEDGE_DOCUMENTS ||--o{ KNOWLEDGE_CHUNKS : contains
  TICKETS ||--o{ AUDIT_EVENTS : generates
  MODEL_VERSIONS ||--o{ PREDICTIONS : used_for
  USERS {
    uuid id PK
    text email UK
    text password_hash
    text role
    boolean is_active
  }
  TICKETS {
    uuid id PK
    text subject
    text customer_message
    text status
    uuid assigned_agent_id FK
    uuid created_by FK
    timestamp created_at
  }
  PREDICTIONS {
    uuid id PK
    uuid ticket_id FK
    uuid model_version_id FK
    text predicted_intent
    float confidence
    text corrected_intent
  }
  MODEL_VERSIONS {
    uuid id PK
    text version UK
    text artifact_hash
    json metrics_summary
  }
  KNOWLEDGE_DOCUMENTS {
    uuid id PK
    text title
    text version
    text approval_status
    text content_hash
  }
  KNOWLEDGE_CHUNKS {
    uuid id PK
    uuid document_id FK
    text chunk_text
    vector embedding
    text section_label
  }
  DRAFTS {
    uuid id PK
    uuid ticket_id FK
    text text
    text status
    uuid reviewed_by FK
  }
  DRAFT_CITATIONS {
    uuid id PK
    uuid draft_id FK
    uuid chunk_id FK
  }
  AUDIT_EVENTS {
    uuid id PK
    uuid ticket_id FK
    uuid actor_id FK
    text action
    timestamp occurred_at
  }
```

## 4.2 Schema conventions and indexes

- UUID primary keys; `created_at`/`updated_at` as `TIMESTAMPTZ` in UTC; database constraints and proper foreign keys.
- Enumerate roles (`agent`, `admin`), statuses (`open`, `in_review`, `approved`, `closed`), draft statuses (`draft`, `approved`, `rejected`), document states (`draft`, `approved`, `archived`).
- Index `tickets(status, created_at DESC)`, `tickets(assigned_agent_id, status)`, `predictions(ticket_id, created_at DESC)`, `drafts(ticket_id, created_at DESC)`.
- Unique document version within title/key. For vector similarity use pgvector index appropriate to embedding dimension/distance (HNSW or IVFFlat based on dataset size); check query plans before adding complexity.
- Persist prediction `top_k` (JSON), `threshold`, `model_version_id` and timestamp where useful. Store draft `prompt_version`, `llm_model`, `retrieved_chunk_ids`, and failure/abstention status for auditability.
- Separate secrets from database and never store provider API keys in ticket rows.
- Use Alembic for **every** schema change. Seed only fake demo accounts and tickets.

---

# 5. API contract (versioned REST)

Base prefix: `/api/v1`. All list endpoints paginate and enforce auth.

| Method | Route | Auth | Purpose |
|---|---|---|---|
| `GET` | `/health/live` | public | Process liveness |
| `GET` | `/health/ready` | internal/demo | Dependency readiness |
| `POST` | `/auth/login` | public, rate-limited | Authenticate demo user |
| `GET` | `/auth/me` | agent/admin | Current identity/role |
| `GET` | `/tickets` | agent/admin | Scoped/paginated inbox |
| `POST` | `/tickets` | agent/admin | Create demo ticket |
| `GET` | `/tickets/{ticket_id}` | authorized | Detail + predictions/drafts |
| `PATCH` | `/tickets/{ticket_id}` | authorized | Update assignment/status per rules |
| `POST` | `/tickets/{ticket_id}/predict` | authorized | Run + persist intent inference |
| `POST` | `/ml/predict-intent` | authorized | Stateless prediction for supplied text |
| `POST` | `/knowledge/documents` | admin | Upload/ingest fictional policy |
| `GET` | `/knowledge/documents` | agent/admin | List approved knowledge |
| `POST` | `/tickets/{ticket_id}/drafts` | authorized | Retrieve + generate stored draft |
| `PATCH` | `/tickets/{ticket_id}/drafts/{draft_id}` | authorized | Edit generated draft |
| `POST` | `/tickets/{ticket_id}/drafts/{draft_id}/approve` | authorized | Human approval |
| `POST` | `/tickets/{ticket_id}/drafts/{draft_id}/reject` | authorized | Human rejection |
| `GET` | `/analytics/overview` | authorized | Ticket workflow counts |

**Example classifier response (illustrative, not measured):**

```json
{
  "intent": "transfer_not_received_by_recipient",
  "confidence": 0.91,
  "top_k": [{"intent": "transfer_not_received_by_recipient", "probability": 0.91}],
  "requires_manual_review": false,
  "model_version": "baseline-v1"
}
```

**Example draft result schema:**

```json
{
  "draft_id": "uuid",
  "status": "draft",
  "draft_text": "Draft to be verified by an agent.",
  "citations": [{"chunk_id": "uuid", "document_title": "DemoBank Transfer Policy", "section": "3.2"}],
  "unsupported": false,
  "needs_human_review": true,
  "llm_model": "configured-provider-model"
}
```

Use Pydantic request/response DTOs, stable error envelope `{"error":{"code":"...","message":"...","request_id":"..."}}`, appropriate 400/401/403/404/409/422/429/503 codes, and OpenAPI examples. Never trust `assigned_agent_id` solely because it was submitted by a browser.

---

# 6. Frontend UX design

## 6.1 Pages and states

1. `/login`: login, validation and expired-session flow.
2. `/app`: dashboard cards (total tickets, status distribution, reviewed drafts) and trend; no fabricated prediction-accuracy KPI.
3. `/app/tickets`: paginated inbox with search/status/intent filters, loading/error/empty states.
4. `/app/tickets/:id`: full message, ML predicted intent/top-k/confidence, override indicator, evidence and draft composer, approval history.
5. `/app/knowledge`: approved policy list; admin-only upload/approval actions.
6. `/app/quality`: offline model metrics and limitations, sourced from a published static/versioned evaluation artifact (P1 if schedule tight).

## 6.2 Component inventory

`AppShell`, `Sidebar`, `Topbar`, `ProtectedRoute`, `TicketTable`, `TicketFilters`, `TicketStatusBadge`, `IntentPredictionCard`, `ConfidenceMeter`, `EvidenceList`, `DraftEditor`, `ReviewActions`, `ActivityTimeline`, `MetricCard`, `ErrorBoundary`, `Toast`, `Skeleton`, `EmptyState`, `ConfirmDialog`.

## 6.3 UI behavior

- All AI text clearly labelled **Suggestion — requires review**.
- Confidence always identified as classifier score, not truth; low-confidence state prominent.
- Draft citations link to actual retrieved document text/version and highlight source segments.
- Actions require backend confirmation, not optimistic success messages for final approval.
- Error/timeout supports retry with bounded conditions; prevent double-submit.
- Accessible forms, responsive table layout and keyboard interactions.
- API client centralizes auth, request IDs, type-safe DTOs, and error parsing; server remains source of truth.

---

# 7. Delivery chunks and exhaustive task backlog

**Task ID convention:** `C<chunk>-T<number>`; each item includes priority and assignee (single developer unless team expands). The number of checkboxes is intentionally detailed so this file can drive GitHub Issues.

## CHUNK 00 — Scope, product discovery, architecture (Week 1)

**Dependencies:** None. **Output:** signed-off scope, diagrams and backlog. **Gate:** every P0 feature can be demonstrated with a user story and acceptance criteria.

- [ ] **C00-T01 P0** Define measurable problem statement, scope, personas and demo-only banking disclaimer.
- [ ] **C00-T02 P0** Write user journeys for ticket creation → predict → retrieve → draft → human approval.
- [ ] **C00-T03 P0** Write `docs/requirements.md` with FR/NFR tables, roles, acceptance scenarios, out-of-scope list.
- [ ] **C00-T04 P0** Make a risk register (misclassification, hallucination, leakage, security, time/cost).
- [ ] **C00-T05 P0** Draw system context, component diagrams and data-flow diagram with trust boundaries.
- [ ] **C00-T06 P0** Write ADR-001 modular monolith, ADR-002 RAG vs direct prompting, ADR-003 DB/vector choice.
- [ ] **C00-T07 P0** Decide LLM provider budget, mock strategy and development environments.
- [ ] **C00-T08 P0** Define issue labels, PR template, commit conventions and weekly review format.
- [ ] **C00-T09 P1** Sketch wireframes for inbox, ticket detail, knowledge and dashboard.
- [ ] **C00-T10 P0** Obtain/verify dataset usage terms and fictional knowledge-document policy.

**Acceptance:** `requirements.md`, diagrams, ADRs and risk register exist; scope is realistically 12 weeks; no feature assumes real banking access.

## CHUNK 01 — Repository, environments, quality gates (Weeks 1–2)

**Depends on:** C00. **Output:** runnable skeleton and green CI. **Gate:** one-command local startup and baseline CI.

- [ ] **C01-T01 P0** Initialize monorepo structure and Git, `.gitignore`, LICENSE decision and README skeleton.
- [ ] **C01-T02 P0** Create Python project/virtual environment, backend/ML dependency declarations and lock policy.
- [ ] **C01-T03 P0** Create React + TypeScript + Vite app with routing and typed API client skeleton.
- [ ] **C01-T04 P0** Configure Ruff, formatters, typing checks, Prettier/ESLint and test commands.
- [ ] **C01-T05 P0** Add `config.py` using pydantic-settings, `.env.example`, startup config validation.
- [ ] **C01-T06 P0** Add FastAPI `/health/live`, OpenAPI tags, CORS allowlist, unified error handling and request IDs.
- [ ] **C01-T07 P0** Create Docker Compose services `api`, `web`, `postgres`; pin image versions in implementation.
- [ ] **C01-T08 P0** Configure GitHub Actions for lint and unit tests; no secrets required for PR checks.
- [ ] **C01-T09 P0** Add backend integration test and frontend render test to CI.
- [ ] **C01-T10 P1** Add `.editorconfig`, pre-commit checks and dependency/security scanning.
- [ ] **C01-T11 P0** Write exact Windows PowerShell and Linux/macOS setup commands in README.

**Acceptance:** Fresh clone can start an empty shell app and API; lint/test CI passes; no credentials committed.

## CHUNK 02 — Dataset audit and reproducible preparation (Week 2)

**Depends on:** C01. **Output:** data card and fixed train/validation protocol. **Gate:** no test-set tuning.

- [ ] **C02-T01 P0** Download BANKING77 using documented source and pinned revision; record license/attribution.
- [ ] **C02-T02 P0** Validate schema, duplicates/nulls, label distribution, text lengths and train/test counts.
- [ ] **C02-T03 P0** Generate `docs/data-dictionary.md` and dataset limitations/data provenance.
- [ ] **C02-T04 P0** Split only the published train portion into stratified train/validation (seed recorded).
- [ ] **C02-T05 P0** Implement repeatable data load/prep commands with checks and fixed versions.
- [ ] **C02-T06 P0** Prevent raw/large dataset commits; record data setup in `data/README.md`.
- [ ] **C02-T07 P1** Visualize intent distribution and ambiguous examples for exploratory report.
- [ ] **C02-T08 P0** Write tests for label mapping, data integrity and preprocessing invariants.

**Acceptance:** Same prepared splits can be recreated; test data not inspected for model selection; dataset licensing is documented.

## CHUNK 03 — Supervised ML training + research (Weeks 3–4)

**Depends on:** C02. **Output:** versioned model + objective evaluation. **Gate:** classifier beats a documented dummy baseline on validation and is reproducible.

- [ ] **C03-T01 P0** Train dummy/majority-class baseline; record macro F1 and accuracy.
- [ ] **C03-T02 P0** Implement sklearn `Pipeline(TfidfVectorizer, LogisticRegression)` fitted on training data only.
- [ ] **C03-T03 P0** Tune a limited hyperparameter grid using validation/CV within training data.
- [ ] **C03-T04 P0** Record environment, data split, seed, params and metrics with MLflow or local experiment manifest.
- [ ] **C03-T05 P0** Evaluate per-class precision/recall/F1, confusion matrix and common failure examples.
- [ ] **C03-T06 P0** Evaluate confidence calibration; select manual-review threshold **on validation only**.
- [ ] **C03-T07 P0** Save trusted model pipeline with label map, version, hash and feature contract.
- [ ] **C03-T08 P0** Build testable `predict_intent(text)` returning top-k, confidence, version and review flag.
- [ ] **C03-T09 P0** Freeze model choice/threshold before **one** final published test evaluation; publish results, not guesses.
- [ ] **C03-T10 P0** Write model card: domain mismatch, data quality, limits, known mistakes, fairness considerations.
- [ ] **C03-T11 P0** Test input encoding, empty/oversized messages, out-of-domain messages and model load errors.
- [ ] **C03-T12 P1** Evaluate sentence-embedding + linear classifier as comparator if time allows.

**Acceptance:** Reproduction script loads exact artifact; metrics and confusion matrix stored; unknown/OOD handling is documented; code never trains during an API request.

## CHUNK 04 — Relational database, migrations, persistence (Week 5)

**Depends on:** C01 + approved ERD. **Output:** migration-backed schema + repository tests. **Gate:** schema can build from zero and enforce constraints.

- [ ] **C04-T01 P0** Define SQLAlchemy models: `users`, `tickets`, `predictions`, `model_versions`, `drafts`, `draft_citations`, `knowledge_documents`, `knowledge_chunks`, `audit_events`.
- [ ] **C04-T02 P0** Create initial Alembic migration; enable pgvector extension through documented DB setup/migration.
- [ ] **C04-T03 P0** Implement async or sync SQLAlchemy session consistently; transactions per request/task.
- [ ] **C04-T04 P0** Add indexes, unique constraints, foreign keys, status checks and UTC timestamps.
- [ ] **C04-T05 P0** Implement repositories with explicit scoping, pagination and safe sorting/filter mapping.
- [ ] **C04-T06 P0** Seed fake admin/agent accounts, demo tickets and reference model version idempotently.
- [ ] **C04-T07 P0** Add migration-up/fresh-schema and query integration tests in Postgres.
- [ ] **C04-T08 P1** Add practical backup/restore for demo DB and data reset command.

**Acceptance:** `alembic upgrade head` works from an empty DB; invalid relationships rejected; seed reruns do not duplicate records.

## CHUNK 05 — Authentication, ticket workflow, inference REST (Weeks 5–6)

**Depends on:** C03 + C04. **Output:** secure working ML ticket backend. **Gate:** API passes role/scope tests, predicts and stores model metadata.

- [ ] **C05-T01 P0** Implement password hashing, login, auth dependency and demo token/session expiry.
- [ ] **C05-T02 P0** Implement agent/admin role guards and per-ticket scope checks in services/repositories.
- [ ] **C05-T03 P0** Create Pydantic DTOs for ticket create/update/read, prediction request/response and pagination.
- [ ] **C05-T04 P0** Implement ticket create/list/detail/status routes and allowed state transitions.
- [ ] **C05-T05 P0** Load trusted ML artifact on app startup and fail readiness if required artifact unavailable.
- [ ] **C05-T06 P0** Implement stateless `/ml/predict-intent` and persisted `/tickets/{id}/predict` endpoints.
- [ ] **C05-T07 P0** Store model version, top-k, confidence, review threshold and timestamp.
- [ ] **C05-T08 P0** Add structured error envelope, safe logs, rate limits for costly routes, CORS config.
- [ ] **C05-T09 P0** Implement tests: 401, 403, unauthorized ticket access, empty text, oversized input, invalid states, inference failure.
- [ ] **C05-T10 P0** Document OpenAPI requests/responses and test with HTTP client/curl examples.
- [ ] **C05-T11 P1** Add agent override/correction of model intent, with audit history.

**Acceptance:** A scripted HTTP scenario logs in, creates a ticket, predicts, reads persisted result; other agent cannot read out-of-scope ticket.

## CHUNK 06 — Frontend foundation, login and ticket UI (Weeks 7–8)

**Depends on:** C05. **Output:** human-usable ML app. **Gate:** Week 8 portfolio-ready release without RAG.

- [ ] **C06-T01 P0** Implement design tokens, responsive shell, navigation and login UI.
- [ ] **C06-T02 P0** Create auth state handling, route guard, token expiry and role-based navigation (server remains authoritative).
- [ ] **C06-T03 P0** Build typed API client, query caching, mutation invalidation and error/toast flows.
- [ ] **C06-T04 P0** Build paginated ticket list, filter controls, ticket creation form and status badge.
- [ ] **C06-T05 P0** Build ticket details with original message, status and assignment.
- [ ] **C06-T06 P0** Add `Predict intent` action, score/top-k visualization and manual-review indicator.
- [ ] **C06-T07 P0** Handle loading, empty, validation, permission and server-error states.
- [ ] **C06-T08 P0** Add keyboard labels, accessible tables/forms and basic mobile layout.
- [ ] **C06-T09 P0** Create Vitest component tests and one Playwright login → create → predict smoke test.
- [ ] **C06-T10 P0** Record a Week 8 milestone demo and save screenshots for portfolio.
- [ ] **C06-T11 P1** Add editable intent correction UI, preserving audit trail.

**Acceptance:** An agent can complete login → create ticket → predict → inspect result in the browser; tested with seeded synthetic tickets.

## CHUNK 07 — Fictional policy knowledge and pgvector retrieval (Week 9)

**Depends on:** C04 + C05. **Output:** traceable, approved retrieval. **Gate:** correct policy chunks returned for test questions.

- [ ] **C07-T01 P0** Author 5–8 internally consistent `DemoBank` fictional policy docs, each prominently labelled simulated.
- [ ] **C07-T02 P0** Define version/approval rules; only approved, active versions indexed for retrieval.
- [ ] **C07-T03 P0** Implement safe ingestion with file size/type controls and text extraction (start with Markdown/TXT; PDF P1).
- [ ] **C07-T04 P0** Implement deterministic chunking, IDs, text normalization and metadata with source sections.
- [ ] **C07-T05 P0** Pin embedding model; build embeddings and store using pgvector with dimension consistency.
- [ ] **C07-T06 P0** Implement similarity retrieval with scope/filter and return chunk IDs, scores and source section labels.
- [ ] **C07-T07 P0** Make ingestion idempotent using content hash + version; support archiving/re-indexing.
- [ ] **C07-T08 P0** Create at least 30 manually reviewed RAG questions with expected references, including unanswerable cases.
- [ ] **C07-T09 P0** Measure retrieval Recall@3/5 and inspect retrieval failures.
- [ ] **C07-T10 P0** Add admin policy list/upload API and unauthorized-upload tests.
- [ ] **C07-T11 P1** Implement hybrid keyword retrieval or reranking only if baseline fails specific cases.

**Acceptance:** A known question retrieves expected source chunks; unknown question can return no support; outdated/unapproved docs excluded.

## CHUNK 08 — LLM drafts, citation verification, human-in-loop (Week 10)

**Depends on:** C07 + C06. **Output:** safe assistant end-to-end. **Gate:** no draft can be approved without a real authorized user action.

- [ ] **C08-T01 P0** Define `LLMClient` interface, production adapter, deterministic test/mock adapter and token/cost caps.
- [ ] **C08-T02 P0** Design immutable system/developer instructions that mark customer text/retrieved passages untrusted.
- [ ] **C08-T03 P0** Implement retrieval → context assembly → structured draft call → Pydantic output validation.
- [ ] **C08-T04 P0** Verify every cited chunk ID was actually retrieved and corresponds to correct doc version.
- [ ] **C08-T05 P0** Handle insufficient evidence, injection attempts, malformed JSON, provider timeout, empty response and token-budget exhaustion.
- [ ] **C08-T06 P0** Create `drafts` persistence with document/citation links, provider/prompt/model metadata and generation status.
- [ ] **C08-T07 P0** Implement draft editing, approval/rejection rules and transactional audit events; disallow auto-send.
- [ ] **C08-T08 P0** Add backend routes for generating, editing, approving, rejecting; enforce ownership and role.
- [ ] **C08-T09 P0** Build citation viewer, draft editor, regenerate button, review actions and confirmation states.
- [ ] **C08-T10 P0** Evaluate RAG cases for evidence support, valid citations, and unsupported-answer abstention; publish failures.
- [ ] **C08-T11 P0** Run security tests for malicious document instructions, fake citations and unauthorized approvals.
- [ ] **C08-T12 P1** Add grounded answer templates for selected high-risk intents if freeform LLM is unreliable.

**Acceptance:** Demo message → intent → verified policy citation → editable draft → approval log; policy injection cannot turn the LLM into a DB/action executor.

## CHUNK 09 — Analytics, observability and release hardening (Week 11)

**Depends on:** C06 + C08. **Output:** monitored, tested release candidate. **Gate:** key workflows measured and failure behavior understood.

- [ ] **C09-T01 P0** Implement aggregated ticket status, intent frequency and draft approval/rejection counts via SQL.
- [ ] **C09-T02 P0** Create dashboard cards/charts and clear data-source labels (`synthetic demo` vs `offline ML evaluation`).
- [ ] **C09-T03 P0** Add structured JSON logs, request/correlation IDs and inference/RAG duration metrics.
- [ ] **C09-T04 P0** Add provider failure/timeout and retry tests, user-facing graceful failure.
- [ ] **C09-T05 P0** Run basic app threat model: auth, broken object authorization, injection, PII leaks, malicious file uploads, prompt injection, denial-of-wallet.
- [ ] **C09-T06 P0** Add secrets/dependency scans and ensure example env files contain placeholders only.
- [ ] **C09-T07 P0** Create realistic but synthetic API load-test scenario; report measured local p50/p95, errors and machine config.
- [ ] **C09-T08 P0** Review DB indexes/query plans for slow pages and fix top bottlenecks.
- [ ] **C09-T09 P0** Verify run from empty volumes, seeds, migrations, known model artifact and policy indexing.
- [ ] **C09-T10 P1** Add simple batch drift report for classifier input distribution; distinguish drift from accuracy (no live labels).

**Acceptance:** core E2E tests pass; common failures have recoverable UX; no critical open security issues; measurement report is honest and reproducible.

## CHUNK 10 — CI/CD, deployment, documentation and portfolio (Week 12)

**Depends on:** All P0 chunks. **Output:** release `v1.0.0`. **Gate:** independent reviewer can run and understand system.

- [ ] **C10-T01 P0** Create multi-stage/production-conscious API and web Dockerfiles; non-root runtime where practical.
- [ ] **C10-T02 P0** Finalize Compose dependencies, health checks, volumes, model mount and startup migration command.
- [ ] **C10-T03 P0** GitHub Actions runs backend unit/integration, frontend tests, build, lint, type checks and security checks.
- [ ] **C10-T04 P0** Build staging/demo deployment with HTTPS and restricted demo users if budget/provider permits; otherwise provide one-command reproducible local demo.
- [ ] **C10-T05 P0** Confirm secrets excluded from repository and logs; document backups, reset and teardown.
- [ ] **C10-T06 P0** Write thorough README: problem, features, architecture, prerequisites, setup, demo credentials policy, screenshots, known limits.
- [ ] **C10-T07 P0** Finish model card, ML evaluation report, RAG evaluation report, threat model, ADRs and API docs.
- [ ] **C10-T08 P0** Capture demo: login → ticket → classify → retrieve → draft → edit/approve → dashboard.
- [ ] **C10-T09 P0** Create 3–5 minute presentation and 1-page portfolio case study with **measured** metrics, not invented KPIs.
- [ ] **C10-T10 P0** Tag `v1.0.0`, add release notes, known bugs and upgrade instructions.
- [ ] **C10-T11 P1** Add GitHub project board and screen-captured architecture walkthrough for interview practice.
- [ ] **C10-T12 P1** Verify deployment with a fresh reviewer machine/account.

**Acceptance:** Fresh-clone documentation works; interviewer can observe the entire human-reviewed AI workflow and inspect empirical evaluation, test suite and architecture.

## OPTIONAL CHUNK 11 — Post-MVP differentiators (after Week 12 only)

- [ ] **C11-T01 P2** Active-learning queue: store agent-corrected labels for review and future offline retraining, no automatic learning from unreviewed data.
- [ ] **C11-T02 P2** Sentence-embedding ML comparator or compact transformer fine-tuning if justified by measured benefit.
- [ ] **C11-T03 P2** RAG reranking/hybrid search with documented retrieval gain.
- [ ] **C11-T04 P2** Trend/drift report against versioned historical batches and threshold alerts.
- [ ] **C11-T05 P2** Multi-team organization scoping and isolated policy bases; prove tenant isolation.
- [ ] **C11-T06 P2** Ticket import/export (synthetic only), export filtering and secure downloadable summaries.
- [ ] **C11-T07 P2** Cost/performance dashboard for LLM usage, cache hits and model response latency.

---

# 8. Dependency map, weekly workload and milestones

```mermaid
flowchart LR
  C00[00 Discovery] --> C01[01 Repo/CI]
  C01 --> C02[02 Dataset]
  C02 --> C03[03 ML]
  C01 --> C04[04 Database]
  C03 --> C05[05 Backend]
  C04 --> C05
  C05 --> C06[06 Frontend]
  C04 --> C07[07 Knowledge/Retrieval]
  C06 --> C08[08 Draft UI + Workflow]
  C07 --> C08
  C08 --> C09[09 Hardening]
  C09 --> C10[10 Release]
```

| Week | Primary chunks | Evidence/checkpoint | Indicative hours |
|---|---|---|---:|
| 1 | 00 + 01 | Scope/ADRs, repo skeleton | 12–15 |
| 2 | 01 + 02 | CI, dataset audit/splits | 12–15 |
| 3 | 03 | Baselines & evaluation | 12–15 |
| 4 | 03 | Frozen model artifact/model card | 12–15 |
| 5 | 04 + 05 | DB migrations, auth, tickets | 12–15 |
| 6 | 05 | ML prediction API, role tests | 12–15 |
| 7 | 06 | Inbox and ticket UI | 12–15 |
| 8 | 06 | **Gate A: demo of integrated ML app** | 12–15 |
| 9 | 07 | Policy retrieval and eval set | 12–15 |
| 10 | 08 | **Gate B: RAG + human review demo** | 12–15 |
| 11 | 09 | Hardening, dashboard, tests | 12–15 |
| 12 | 10 | **Gate C: release v1.0.0** | 12–15 |

**Scope control:** ~144–180 hours is tight for full-stack + RAG. If blocked, keep only P0 features; simplify frontend design and use Markdown policies; skip MLflow UI, advanced dashboards and paid public hosting. If RAG is incomplete at Week 10, release the tested classification/ticketing app and mark RAG explicitly as a roadmap item rather than faking a working system.

---

# 9. Test strategy and acceptance matrix

## 9.1 Test pyramid

| Level | Cases | Tool |
|---|---|---|
| Unit — ML | preprocessing, label map, empty text, artifact version, confidence boundary | pytest |
| Unit — business | ticket transitions, RBAC decisions, draft approval rules, citation validation | pytest |
| Integration — DB | migrations, constraints, repository scope, transaction rollback, pgvector retrieval | pytest + Postgres |
| API | login, ticket CRUD, predict, upload, draft, approve/reject, errors | pytest + HTTPX |
| RAG reliability | answerable/unanswerable, fake citations, malicious passages, provider outage | pytest + fixture client |
| Frontend | forms, result states, citation views, invalid transitions | Vitest + RTL |
| E2E | seeded user logs in → creates ticket → predicts → drafts → approves | Playwright |
| Performance | measured p50/p95, failure rates; document hardware | lightweight load script |
| Security | unauthorized resource access, file validation, prompt injection, secrets hygiene | automated + manual checklist |

## 9.2 Release blocking scenarios

- [ ] Unauthorized user cannot access or modify another agent's ticket.
- [ ] Draft citation IDs cannot reference an unrelated, missing or unapproved policy chunk.
- [ ] Uploaded policies cannot override system instructions or trigger actions.
- [ ] Classifier handles empty, long and out-of-domain input safely.
- [ ] A provider timeout does not create an approved draft or corrupt a ticket.
- [ ] Approval is attributable to a real authenticated human and is audit-logged.
- [ ] Dashboard accurately aggregates database records and never passes synthetic metrics off as real performance.
- [ ] A clean run can recreate DB tables, seed fixtures, load model and ingest approved docs.

---

# 10. Threat model and responsible AI checklist

## 10.1 Trust boundaries

**Untrusted:** Customer-provided text, uploaded demo files, retrieved content, LLM output, browser request bodies.  
**Controlled:** Server-side rules, typed DTOs, role checks, approved source list, trusted model artifacts, access to environment secrets.

## 10.2 Concrete controls

- [ ] No direct LLM-generated SQL or unrestricted tool calls.
- [ ] Validate input types, body length, upload MIME/size and extraction errors.
- [ ] Check resource scope before retrieval, prediction history, draft review and document management.
- [ ] Keep provider keys server-side only; redact tokens, document secrets and raw text in logs.
- [ ] Enforce bounded LLM output size, timeouts and rate limits; track cost.
- [ ] Separate model probability from answer quality; don't present “AI confidence” as verified truth.
- [ ] Provide low-confidence/unsupported disclaimers and human review.
- [ ] Add prompt-injection and cross-document citation tests.
- [ ] Generate no automatic customer communications or financial actions.
- [ ] Publish dataset license, fictional-data statement and limitations in README.

---

# 11. Project management: scrum-lite operating system

## 11.1 Issue template

```markdown
### [CXX-TYY] Title
**Priority:** P0/P1/P2
**Owner:** Developer
**Depends on:** CXX-TYY
**User story / engineering outcome:** ...
**Implementation steps:** ...
**Acceptance criteria:**
- [ ] Positive path test
- [ ] Negative path test
- [ ] Documentation and screenshots
**Evidence:** commit/PR, test output, demo screenshot
**Estimate:** 1–6 hours (split larger items)
```

## 11.2 Branching and PR process

- `main` protected; short-lived `feat/C05-T06-prediction-api`, `fix/...`, `docs/...` branches.
- Each PR includes what/why, API/schema changes, test evidence, UI screenshots if relevant, security notes and rollback considerations.
- Use conventional commits such as `feat(api): add versioned intent prediction [C05-T06]`.
- Conduct a weekly self-review as if you are a tech lead reviewing a teammate's PR: clarity, tests, correctness, simplicity, safety.

## 11.3 Weekly ritual (30–45 minutes)

1. Review completed tasks and actual hours vs. estimate.
2. Demo one working increment; attach evidence.
3. Update risks and blockers; revise scope based on remaining capacity.
4. Plan 3–6 highest priority tasks for next week.
5. Write `docs/progress/week-NN.md` (done, learning, defects, next).

## 11.4 Milestones and sign-off criteria

| Gate | Date relative to start | Sign-off |
|---|---|---|
| M0 | End Week 2 | Repo, CI, requirements, dataset strategy approved |
| M1 | End Week 4 | Model trained, baseline compared, evaluation published |
| M2 | End Week 6 | Secured ticket/prediction API and DB functional |
| M3 | End Week 8 | Login + ticket creation + classification in browser |
| M4 | End Week 10 | Cited RAG response and human review workflow |
| M5 | End Week 12 | Release tag, tests, docs, reproducible demo |

---

# 12. Deployment and operations runbook

## Environments

- `dev`: local Vite + FastAPI + PostgreSQL (Docker for DB).
- `test`: isolated Postgres service and fake deterministic LLM; never spend provider tokens in CI.
- `demo`: Docker Compose stack, seeded fake users/tickets, simulated policies, real trained model; optionally hosted securely.

## Configuration variables (names only; no values/secrets)

```dotenv
APP_ENV=development
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/supportpilot
JWT_SECRET_KEY=REPLACE_WITH_LONG_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173
MODEL_ARTIFACT_PATH=artifacts/intent_model.joblib
MODEL_VERSION=baseline-v1
EMBEDDING_MODEL_ID=PINNED_MODEL_ID
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_MODEL=CONFIGURED_MODEL
LLM_MAX_INPUT_TOKENS=3000
LLM_MAX_OUTPUT_TOKENS=700
LLM_TIMEOUT_SECONDS=30
LLM_MONTHLY_BUDGET_USD=5
MAX_UPLOAD_SIZE_MB=3
```

**Important:** These are illustrative config keys; they become authoritative only once implemented in `core/config.py`. Do not use a sample JWT secret in deployed environments. Decide whether to use psycopg sync or async SQLAlchemy and keep `DATABASE_URL` consistent.

## Reproducible startup sequence

1. Clone repository and copy `.env.example` → `.env` (populate demo secrets and LLM provider if needed).
2. Start DB/container services; run Alembic migrations.
3. Seed synthetic users/tickets, register trusted model artifact and ingest fictional approved policies.
4. Start API and frontend; verify readiness.
5. Use seeded demo credentials (document how to generate locally, do not publish a fixed admin password).
6. Run the end-to-end smoke test; inspect logs and verification commands.

## Operational tests

- Restart services; pending tickets remain in database.
- Simulate invalid DB settings; readiness reports failure without exposing credentials.
- Disable LLM provider; classification and ticketing continue and drafting fails gracefully.
- Re-ingest unchanged policy; no duplicate chunks.
- Remove/delete demo data with a clearly documented reset command.

---

# 13. Technical interview preparation mapped to this project

| Topic | Be able to explain | Evidence |
|---|---|---|
| NLP + scikit-learn | TF-IDF, logistic regression, pipeline fitting, macro F1 | model card + experiment plots |
| Model validation | leakage, train/validation/test, calibration, abstention | evaluation script and report |
| Backend design | DI, Pydantic, auth, service/repository layers, response contracts | source modules + API tests |
| Databases | relationships, indexes, migrations, transactions, pgvector | ERD + Alembic history |
| RAG | chunking, embeddings, similarity, retrieval failures, citations | retrieval tests + gold set |
| LLM reliability | structured outputs, validation, prompt injection, fallback | threat model + negative tests |
| Frontend | typed API client, state, auth, accessibility, error states | app + component tests |
| MLOps | reproducibility, experiment tracking, artifact versioning, drift limits | experiment report + release |
| DevOps | containers, CI, env and secret management | GitHub Actions + Docker |
| Product thinking | user journey, non-goals, trade-offs, measured value | proposal + roadmap |

Prepare a short answer for: **Why use a supervised classifier instead of asking the LLM for the intent?** Good answer: cheaper deterministic inference, measurable labelled benchmark, versioned evaluation, and lower dependency on provider availability; GenAI is reserved for the task that benefits from natural language grounded in documents.

---

# 14. First 10 actions to take today

1. [ ] Create Git repository `supportpilot-ai` with `README.md`, `PROJECT_PROPOSAL.md`, and this `MASTERPLAN.md`.
2. [ ] Add `docs/requirements.md` from FR/NFR and create project board columns.
3. [ ] Write ADR-001 modular monolith and choose a single LLM provider or mock-first mode.
4. [ ] Initialize backend Python 3.12 project and FastAPI health route.
5. [ ] Initialize React TypeScript Vite app with routing.
6. [ ] Create `.env.example`, `.gitignore`, GitHub Actions lint/test starter.
7. [ ] Download/inspect BANKING77 and record license/provenance.
8. [ ] Commit a data audit notebook or script and initial class distribution report.
9. [ ] Create test/validation discipline document before training any model.
10. [ ] Demo Week 1 skeleton and log blockers in `docs/progress/week-01.md`.

**Final principle:** The success criterion is not the largest number of AI frameworks. It is a *tested, reproducible, secure, clearly explained end-to-end system* that proves you understand ML evaluation and responsible GenAI integration.
