# Research Notes: TODO 기본 관리
_Updated: 2025-11-11_

## Goals
- Validate stack choices (FastAPI + SQLite + SQLAlchemy Core) meet constitution mandates.
- Identify best practices for layered Clean Architecture in small FastAPI apps.
- Confirm how to reach ≥70% pytest coverage and <200 ms p95 latency.

## Findings

### FastAPI + SQLAlchemy Core
- FastAPI docs recommend dependency-injected DB sessions via `SessionLocal()`; for Core we can use `Session(engine)` and explicit transactions.
- SQLAlchemy 2.0 async APIs exist but sync version is simpler and meets latency target; we can upgrade later without contract break.
- Use `sqlalchemy.sql.func.now()` for timestamps; ensures consistent UTC when combined with `datetime.utcnow()` fallback.

### Layered Clean Architecture
- Keep FastAPI routers thin (serialize/deserialise + status codes).
- Service layer owns business rules (validation beyond Pydantic, timestamp/ID handling).
- Repository layer returns plain dicts/DTOs to avoid leaking SQL Alchemy Row objects; easier for unit tests.

### Validation & Error Handling
- Pydantic v2 `BaseModel` with `ConfigDict(str_strip_whitespace=True)` ensures trimmed titles/descriptions.
- Centralize error payloads via custom `HTTPException` helper to guarantee `{ "detail": "...", "error_code": "..." }`.
- 422 errors automatically shaped by FastAPI; add examples in OpenAPI schema for clarity.

### Performance Considerations
- SQLite handles small workloads if we keep single writer; for API tests use `check_same_thread=False`.
- Index on `created_at DESC` to keep list queries O(log n). Even without index small dataset fine but add proactively.
- Avoid `SELECT *` for list endpoint; specify columns to reduce row parsing overhead.

### Testing Strategy
- Use `pytest.fixture(scope="function")` to set up in-memory DB per test; ensures isolation.
- Integration tests: override `get_db` dependency to use same in-memory engine and create schema via `metadata.create_all`.
- Coverage: include `--cov=app --cov-report=term-missing` in default test command; track in CI.

### Observability
- Use FastAPI middleware logging request method/path + duration.
- Provide structured logging via `logging.config.dictConfig`; log error stack traces at ERROR, request IDs at INFO.

## Decisions
- Stick to synchronous FastAPI + SQLAlchemy Core; async adds unnecessary complexity now.
- Represent timestamps as timezone-aware UTC ISO strings; store as `DateTime(timezone=True)`.
- Use UUID v4 (generated via Python `uuid4()`) as primary key text column; easier to share between SQLite and future DBs.
- Alembic baseline migration will live under `app/db/migrations/versions/0001_create_todos.py`.

## Open Questions
- None currently; clarified updated_at behavior during status toggles in spec.
