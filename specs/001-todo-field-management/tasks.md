---

description: "Task list for TODO Advanced Field Management"
---

# Tasks: TODO Advanced Field Management

**Input**: Design documents from `/specs/001-todo-field-management/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD required per constitution; each user story lists the tests that must be authored before implementation.

**Organization**: Tasks are grouped by user story so each slice can be delivered and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Task can run in parallel (different files, no blocking dependency)
- **[Story]**: User story mapping (US1, US2, US3)
- Every task references the exact file(s) it touches

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Schema and metadata work that every user story depends on.

- [ ] T001 Create Alembic migration `app/db/migrations/versions/0002_add_advanced_fields.py` adding `due_date DATE NULL`, `priority TEXT DEFAULT 'medium'`, `category TEXT NULL`, and `tags TEXT NULL` (JSON payload).
- [ ] T002 Update `app/db/models.py` to keep the SQLAlchemy `todos` table definition in sync with the new columns and defaults from T001.
- [ ] T003 Adjust seed factories/fixtures in `tests/conftest.py` so test TODOs expose the new optional fields with sensible defaults (null/"medium").

**Checkpoint**: Database + fixtures ready ? user stories can start.

---

## Phase 2: User Story 1 - Set deadlines and priority when creating todos (Priority: P1) ? MVP

**Goal**: Allow clients to set/modify `due_date` (ISO, past allowed) and `priority` (enum, default medium) on create/update + surface via GET.

**Independent Test**: Using `tests/integration/test_todos_api.py`, POST/PUT TODOs with different due_date/priority combos and ensure GET responses echo exact values while defaulting `priority` to `"medium"` when omitted.

### Tests (write first)

- [ ] T004 [P] [US1] Extend `tests/unit/test_repositories_todos.py` to cover persisting/retrieving `due_date` and `priority` columns through `TodoRepository`.
- [ ] T005 [P] [US1] Extend `tests/unit/test_services_todos.py` to verify service-level validation (ISO date, enum enforcement, default `priority`).
- [ ] T006 [P] [US1] Add integration scenarios in `tests/integration/test_todos_api.py` for POST/PUT/GET around due dates (valid + invalid) and priority defaults.

### Implementation

- [ ] T007 [P] [US1] Update `app/api/schemas.py` (`TodoCreate`, `TodoUpdate`, `TodoResponse`) to include optional `due_date` and `priority` with proper Pydantic validators and OpenAPI metadata.
- [ ] T008 [US1] Update `app/services/todos.py` to normalize `priority`, allow past ISO dates, and propagate values to repositories.
- [ ] T009 [US1] Update `app/repositories/todos.py` to read/write the new columns and ensure defaults surface when DB values are null.
- [ ] T010 [US1] Ensure `app/api/v1/routes.py` response builders and dependency wiring pass the new fields end-to-end without altering other payload bits.

**Checkpoint**: Deadlines + priority independently testable (MVP slice complete).

---

## Phase 3: User Story 2 - Maintain a single category per TODO (Priority: P2)

**Goal**: Allow clients to add/change/remove a trimmed category label (<=50 chars) per TODO.

**Independent Test**: Using `tests/integration/test_todos_api.py`, PUT a TODO to set `category`, update to another value, then send `category=null` to clear it while verifying GET output.

### Tests (write first)

- [ ] T011 [P] [US2] Extend `tests/unit/test_services_todos.py` with cases covering trim, length validation, and clearing via `None`/empty string.
- [ ] T012 [P] [US2] Add integration coverage in `tests/integration/test_todos_api.py` for category create/update/remove flows.

### Implementation

- [ ] T013 [P] [US2] Update `app/api/schemas.py` to add the optional `category` field with max-length enforcement and whitespace trimming.
- [ ] T014 [US2] Update `app/services/todos.py` to convert whitespace-only payloads into `None` and enforce the 50-character rule.
- [ ] T015 [US2] Update `app/repositories/todos.py` and serializer helpers to persist nullable category values and surface them on GET responses.

**Checkpoint**: Category lifecycle independently testable without impacting deadlines/priority.

---

## Phase 4: User Story 3 - Manage a bounded tag list per TODO (Priority: P3)

**Goal**: Support up to 10 tags per TODO, normalize to lowercase, reject duplicates/oversized entries, and treat PUT payload as full replacement.

**Independent Test**: Via `tests/integration/test_todos_api.py`, create a TODO with tags, verify GET ordering, attempt duplicate/past-10 entries for 422s, and confirm PUT replacement semantics.

### Tests (write first)

- [ ] T016 [P] [US3] Add unit coverage in `tests/unit/test_services_todos.py` for tag normalization, length limits, uniqueness, and replacement semantics.
- [ ] T017 [P] [US3] Expand `tests/unit/test_repositories_todos.py` to ensure tags serialize to/from the TEXT JSON column without order loss.
- [ ] T018 [P] [US3] Add integration flows in `tests/integration/test_todos_api.py` for add/remove/over-limit tag scenarios.

### Implementation

- [ ] T019 [P] [US3] Update `app/api/schemas.py` tag validators (max 10 entries, 20 chars each, lowercase normalization, duplicate rejection) and document them for Swagger.
- [ ] T020 [US3] Update `app/services/todos.py` so PUT treats the incoming `tags` list as authoritative (replace existing, enforce rules, allow empty list to clear).
- [ ] T021 [US3] Update `app/repositories/todos.py` to serialize normalized tag arrays to JSON text and deserialize back into ordered lists.
- [ ] T022 [US3] Ensure `app/api/v1/routes.py` responses include `tags` consistently (default empty array) and align error payloads with validation failures.

**Checkpoint**: Tag management independently testable alongside previous stories.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T023 [P] Update `specs/001-todo-field-management/contracts/todos.yaml` so the documented request/response schemas exactly match the implemented fields/validators.
- [ ] T024 Refresh `specs/001-todo-field-management/quickstart.md` manual verification steps to reflect the final payload shapes and validation guidance.
- [ ] T025 Run full `pytest --cov=app --cov-report=term-missing` from repo root and keep coverage >=70% before merging.
- [ ] T026 [P] Exercise the manual checklist in `quickstart.md` (POST/PUT/GET flows) against the running FastAPI app to validate Swagger and runtime behavior.
- [ ] T027 Document the migration + feature summary in `README.md` (section referencing new optional fields) to keep consumers aligned.

---

## Dependencies & Execution Order

1. **Phase 1** ? All user stories ? Phase 5.
2. US1 (P1) must land before US2/US3 only if shared files create conflicts; otherwise US2/US3 can start right after foundational work because their tasks touch distinct validation paths.
3. Within each story: tests (T00x) ? models/services/repos/routes (T01x-T02x).
4. Polish tasks run after all targeted user stories are complete.

## Parallel Opportunities

- Marked [P] tasks operate on different files (e.g., unit tests across different modules) and can proceed simultaneously once prerequisites complete.
- After Phase 2, separate contributors can split across US1/US2/US3 because repositories/services changes largely target different logic branches (just coordinate around shared files via short-lived feature branches or feature flags).
- During US3, tag-related schema/service/repo tasks touch distinct blocks, so T019-T022 can run in parallel once validations are defined.

## Implementation Strategy

- **MVP**: Deliver Phase 2 (US1) after foundational work ? this unlocks due dates/priority which are the highest value signals.
- **Incremental Additions**: Layer in US2 (category) and US3 (tags) sequentially, validating each slice independently via its test set before merging.
- **Regression Safety**: Re-run the full suite plus manual quickstart after each story to guarantee backwards compatibility for clients still sending legacy payloads.
- **Deployment Note**: Apply Alembic migration 0002 before deploying any code that expects the new columns, and include rollback instructions in release notes.
