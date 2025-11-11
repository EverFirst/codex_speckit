# Implementation Plan: TODO 기본 관리

**Branch**: `001-todo-basics` | **Date**: 2025-11-11 | **Spec**: `specs/001-todo-basics/spec.md`
**Input**: Feature specification from `specs/001-todo-basics/spec.md`

**Note**: Generated per `/speckit.plan` guidance. Aligns with constitution requirements (REST-only, FastAPI + SQLite stack, ≥70% coverage, TDD).

## Summary

Deliver a single-user TODO REST API supporting CRUD plus completion toggles. Endpoints: `POST /todos`, `GET /todos`, `GET /todos/{id}`, `PUT/PATCH /todos/{id}`, `PATCH /todos/{id}/status`, `DELETE /todos/{id}`. All use FastAPI + Pydantic v2, persist to SQLite via SQLAlchemy Core repositories, and expose Swagger UI. Enforce validation (title 1-200 chars, description optional ≤2000), stateless behavior, 200ms p95 latency, and 70%+ pytest coverage. Completion toggles must update `completed`, `completed_at`, and `updated_at`.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI 0.104+, SQLAlchemy Core 2.x, Pydantic v2, Uvicorn, Alembic (for migrations)  
**Storage**: SQLite 3 (file for dev, in-memory for tests)  
**Testing**: pytest, pytest-cov, FastAPI TestClient  
**Target Platform**: Linux/Windows server running uvicorn/gunicorn (stateless)  
**Project Type**: Backend API (single service)  
**Performance Goals**: p95 < 200 ms per request with <50 records, constant-time O(1) toggles/deletes  
**Constraints**: No auth; TDD required; Swagger UI must stay enabled; repository pattern enforced; type hints + Black/isort compliance  
**Scale/Scope**: Single tenant, expected tens of todos per user, easily extendable to multi-user later

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **REST Discipline**: All functionality delivered via REST endpoints listed above. → PASS.  
2. **Stack Lock**: Python 3.11 + FastAPI + SQLite + SQLAlchemy Core without ORM; commit to Pydantic v2. → PASS (explicit).  
3. **Data Validation**: Pydantic models defined for requests/responses; enforce title/description limits. → PASS once schemas coded.  
4. **Quality Targets**: pytest + pytest-cov; enforce ≥70% coverage on business logic; instrumentation in CI. → PASS (planned).  
5. **Performance**: Keep queries simple (single table) and index on `created_at`; ensure toggles only update single row. → PASS (architecture).  
6. **Documentation**: Swagger UI stays enabled; README updates scheduled in polish tasks. → PASS.  
7. **Migrations**: Alembic baseline migration created with todo table (id, title, etc.). → PASS once migration committed.  
8. **TDD Workflow**: Each endpoint implemented after failing test; integrate into task order. → PASS (process).  

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-basics/
├── plan.md              # This implementation plan
├── spec.md              # Approved feature spec
├── research.md          # Phase 0 research output (TBD)
├── data-model.md        # Phase 1 output (TBD)
├── quickstart.md        # Phase 1 output (TBD)
├── contracts/           # OpenAPI or HTTP contract artifacts (TBD)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── api/
│   ├── v1/
│   │   ├── routes.py          # FastAPI routers for /todos
│   │   └── dependencies.py    # Shared DI helpers (DB session, repos)
│   ├── schemas.py             # Pydantic request/response models
│   └── __init__.py
├── services/
│   └── todos.py               # Business rules (validation, toggles)
├── repositories/
│   └── todos.py               # SQLAlchemy Core queries for CRUD
├── db/
│   ├── base.py                # Engine/session creation
│   ├── migrations/            # Alembic scripts
│   └── models.py              # Table metadata (SQLAlchemy Core)
├── config.py                  # Settings (DATABASE_URL, CORS)
└── main.py                    # FastAPI app factory + routers

tests/
├── unit/
│   ├── test_services_todos.py
│   └── test_repositories_todos.py
├── integration/
│   └── test_todos_api.py      # FastAPI TestClient end-to-end
└── conftest.py                # Fixtures (app, DB session, factories)
```

**Structure Decision**: Single backend service; no frontend/client components. Layered Clean Architecture (API → Service → Repository → DB) satisfies repository pattern requirement and keeps business logic testable.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| None | — | — |

## Phase Breakdown & Key Activities

### Phase 0: Research & Design
- Finalize entity/table fields (id/title/description/completed/completed_at/created_at/updated_at).
- Confirm error envelope format (`{"detail": "...", "error_code": "..."}`) and log correlation IDs.
- Document OpenAPI contracts & sample payloads under `specs/001-todo-basics/contracts/`.

### Phase 1: Infrastructure & Foundations
- Set up FastAPI project scaffolding, app factory, router registration.
- Configure SQLAlchemy Core engine with SQLite URL; implement session dependency.
- Initialize Alembic with baseline migration creating `todos` table + indexes.
- Add Pydantic schemas (CreateTodo, UpdateTodo, TodoResponse, ToggleStatusRequest/Response).

### Phase 2: Service & Repository Layer
- Implement repository CRUD using SQLAlchemy Core insert/select/update/delete with parameter binding.
- Implement service functions enforcing validation, default states, and updated_at/completed_at rules.
- Write unit tests (pytest) for repositories (using transaction rollbacks) and services (using in-memory fakes).

### Phase 3: API Endpoints
- Wire FastAPI routers to service layer; map HTTP status codes and error handling.
- Ensure dependency injection for DB session + repository.
- Add pagination placeholders (return `total_count` even without paging).
- Instrument logging (INFO request IDs, ERROR stack traces).

### Phase 4: Testing & Quality Gates
- Implement integration tests with FastAPI TestClient covering all user stories.
- Track coverage with pytest-cov; fail build if <70%.
- Measure local latency (e.g., `pytest --durations=0`) to assert <200ms operations.
- Verify Swagger UI renders all models; capture screenshots or docs.

### Phase 5: Polish & Docs
- Update README with setup/run/test instructions and endpoint summary.
- Document assumptions + future work in `specs/001-todo-basics/quickstart.md`.
- Review logging and error messages for clarity.
- Run Black/isort and type checks (mypy or pyright if available).

### Phase 6: Deployment Readiness
- Provide `.env.example` with `DATABASE_URL`.
- Ensure Alembic migrations executed during startup.
- Confirm `GET /health` exists (basic DB connectivity check).
- Tag release notes summarizing feature.

## Risks & Mitigations

1. **SQLite locking under concurrent tests**: Use in-memory DB with single connection per test; serialize writes in integration fixtures.  
2. **Performance regressions**: Keep queries simple, add index on `created_at`, monitor p95 via pytest benchmarks.  
3. **Validation drift**: Centralize schemas in `app/api/schemas.py` and reuse in services to avoid duplication.  
4. **Updated_at consistency**: Enforce via service layer tests referencing clarification (toggle updates timestamp).  

## Dependencies

- Python 3.11 runtime
- pip/uv pipenv/poetry (choose tool; default pip + requirements.txt)
- Alembic CLI for migrations
- Optional: docker-compose (if later moving off SQLite)

## Testing Strategy Alignment

- Unit: service + repository functions (mock DB or use transaction rollbacks).  
- Integration: FastAPI TestClient hitting real SQLite (in-memory) via dependency override.  
- Coverage: `pytest --cov=app --cov-report=term-missing`.  
- CI: run lint (Black/isort), type check, tests before merge.

## Deployment Notes

- Run `alembic upgrade head` before starting app.
- Use `uvicorn app.main:app --reload` for dev, `gunicorn -k uvicorn.workers.UvicornWorker` for prod.
- Configure logging via `logging.config.dictConfig` with INFO/ERROR separation.

## Open Questions / Follow-Ups

- N/A (clarifications addressed); revisit if auth or pagination enters roadmap.
