---
description: "Task list for feature 001 - TODO 기본 관리"
---

# Tasks: TODO 기본 관리

**Input**: plan.md, spec.md, data-model.md, research.md, contracts/, quickstart.md  
**Prerequisites**: Feature branch `001-todo-basics`

Tests are mandatory per constitution/TDD. Each user story lists tests before implementation.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 [P] [-] Generate `requirements.txt` / `pyproject.toml` with FastAPI 0.104+, SQLAlchemy Core 2.x, Pydantic v2, Alembic, pytest(+cov), Black, isort.
- [x] T002 [-] Scaffold project tree (`app/`, `tests/`, `specs/001-todo-basics/…`) and add `app/main.py` FastAPI app factory placeholder.
- [x] T003 [P] [-] Add `.env.example` containing `DATABASE_URL=sqlite:///./todo.db` and document loading logic in `app/config.py`.
- [x] T004 [-] Configure formatting/lint tooling: `pyproject.toml` sections for Black/isort, add `Makefile` or scripts for `fmt`, `test`.

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T005 [-] Initialize Alembic (`alembic.ini`, `app/db/migrations/env.py`) and create baseline revision `0001_create_todos.py` matching data-model.md (table + `idx_todos_created_at_desc`).
- [x] T006 [P] [-] Implement DB bootstrap: `app/db/base.py` (engine/session factory, SQLite pragmas) and `app/db/models.py` (SQLAlchemy Core metadata + `todos` table).
- [x] T007 [P] [-] Implement repository abstraction skeleton in `app/repositories/todos.py` (interfaces only) and wiring dependency helpers in `app/api/v1/dependencies.py`.
- [x] T008 [-] Create Pydantic v2 schemas in `app/api/schemas.py` (CreateTodo, UpdateTodo, PatchTodo, ToggleStatusRequest, TodoResponse, TodoListResponse, ErrorResponse) with validation limits.
- [x] T009 [P] [-] Add base test fixtures in `tests/conftest.py` (FastAPI app factory override, in-memory SQLite session, `todo_factory` helper).

## Phase 3: User Story 1 – TODO 작성 및 목록 조회 (P1) ✅ MVP

### Tests first
- [x] T010 [P] [US1] Add integration tests in `tests/integration/test_todos_api.py` covering POST /todos success, validation errors, and GET /todos ordering + `total_count`.
- [x] T011 [P] [US1] Add service/repository unit tests in `tests/unit/test_services_todos.py` & `tests/unit/test_repositories_todos.py` to assert create/list behaviors (defaults, ordering, timestamps).

### Implementation
- [x] T012 [P] [US1] Implement repository methods `create_todo` and `list_todos` in `app/repositories/todos.py` using SQLAlchemy Core parameter binding.
- [x] T013 [US1] Implement service functions in `app/services/todos.py` for create/list (enforce title length, description trimming, default `completed=false`, timestamps).
- [x] T014 [US1] Build FastAPI routes in `app/api/v1/routes.py` for POST /todos and GET /todos, including response models, error envelopes, and router registration in `app/main.py`.
- [x] T015 [US1] Update OpenAPI contract (`specs/001-todo-basics/contracts/todos.openapi.yaml`) and README endpoint summary to reflect implemented routes.

## Phase 4: User Story 2 – TODO 상세 조회 및 수정 (P2)

### Tests first
- [x] T016 [P] [US2] Extend integration tests (`tests/integration/test_todos_api.py`) for GET /todos/{id}, PUT /todos/{id}, PATCH /todos/{id} success + 404 cases.
- [x] T017 [P] [US2] Add unit tests ensuring service-level update logic enforces validation, `updated_at` refresh, and 404 propagation.

### Implementation
- [x] T018 [P] [US2] Implement repository functions `get_todo`, `update_todo_full`, `update_todo_partial` in `app/repositories/todos.py`.
- [x] T019 [US2] Expand service layer to map DTOs to responses, handle not-found errors, and centralize `error_code` mapping.
- [x] T020 [US2] Add FastAPI handlers for GET/PUT/PATCH `/todos/{id}` in `app/api/v1/routes.py`, wiring dependencies + raising `HTTPException` with proper status codes.

## Phase 5: User Story 3 – 완료 토글 및 삭제 (P3)

### Tests first
- [x] T021 [P] [US3] Add integration tests covering PATCH /todos/{id}/status transitions (completed true/false) and DELETE /todos/{id}` (204 + idempotent 404).
- [x] T022 [P] [US3] Add service/repository unit tests confirming `completed_at`/`updated_at` handling and hard delete semantics.

### Implementation
- [x] T023 [P] [US3] Implement repository `toggle_status` and `delete_todo` functions (single UPDATE + DELETE with affected row count checks).
- [x] T024 [US3] Extend service layer for toggle/delete workflows, ensuring clarification rule: status changes always refresh `updated_at` and set/clear `completed_at`.
- [x] T025 [US3] Expose PATCH /todos/{id}/status and DELETE /todos/{id} endpoints in `app/api/v1/routes.py` with JSON responses described in spec.

## Phase 6: Polish & Cross-Cutting

- [x] T026 [P] [-] Implement structured logging + request timing middleware in `app/main.py` (INFO) and error logging (ERROR) per constitution.
- [x] T027 [-] Ensure `GET /health` endpoint exists in `app/api/v1/routes.py` (DB ping) and include in docs.
- [x] T028 [P] [-] Update README + `specs/001-todo-basics/quickstart.md` with final commands, health endpoint, and sample curl/httpie calls.
- [x] T029 [-] Run `black . && isort .`, type checking (mypy/pyright if configured), and `pytest --cov=app --cov-report=term-missing`; raise issue if coverage <70%.
- [x] T030 [-] Final verification: ensure Swagger UI shows all endpoints, Alembic migrations applied, and commit feature artifacts (`specs/001-todo-basics/*`).
