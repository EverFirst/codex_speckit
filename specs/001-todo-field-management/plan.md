# Implementation Plan: TODO Advanced Field Management

**Branch**: `001-todo-field-management` | **Date**: 2025-11-11 | **Spec**: `specs/001-todo-field-management/spec.md`
**Input**: Feature specification from `/specs/001-todo-field-management/spec.md`

**Note**: This plan aligns with the `.specify/templates/commands/plan.md` workflow and covers Phases 0-2 deliverables for the feature.

## Summary

Extend Feature 001's FastAPI-based TODO service so each item can optionally store an ISO `due_date`, an enum `priority`, a single `category`, and up to 10 lowercase, deduplicated tags. Work stays within the existing Python 3.11/FastAPI/SQLite stack: add Alembic migration `0002_add_advanced_fields.py`, expand repository/service layers plus Pydantic schemas for validation, and keep all new fields optional to preserve backward compatibility and sub-200 ms latency expectations.

## Technical Context

**Language/Version**: Python 3.11.x  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy Core, Alembic, Uvicorn, pytest + pytest-cov  
**Storage**: SQLite (file-backed) via SQLAlchemy Core metadata and Alembic migrations  
**Testing**: pytest with FastAPI TestClient and pytest-cov (TDD mandated, >=70% coverage)  
**Target Platform**: Linux container/local uvicorn runtime (same as Feature 001 deployment target)  
**Project Type**: Single backend REST API service  
**Performance Goals**: `/todos` POST/PUT/GET endpoints must remain <=200 ms p95 in staging under Feature 001 load profile  
**Constraints**: Backward-compatible optional fields, Alembic migration 0002, Swagger kept current, strict REST semantics, tag validation (<=10 tags, <=20 chars, lowercase unique), TDD workflow, Feature 001 tests stay green  
**Scale/Scope**: Single-tenant TODO API handling tens of thousands of tasks with no sharding or multi-service expansion

## Constitution Check

*GATE: Must pass before Phase 0 research. Status = PASS (re-evaluate after Phase 1 artifacts).*

- **Architecture Discipline** - PASS: No new endpoints; existing REST resources stay stateless and continue returning consistent JSON envelopes.  
- **Technical Stack Standards** - PASS: Remains on Python 3.11, FastAPI, SQLite, SQLAlchemy Core, Pydantic, and leaves Swagger enabled.  
- **Quality Guarantees** - PASS: Plan mandates Alembic migration, validation errors for bad input, and maintains >=70% pytest coverage plus <200 ms p95 latency.  
- **Development Workflow** - PASS: TDD enforced (new tests before code), REST verb semantics preserved, and formatting/type-hint rules unchanged.  
- **Security & Performance Safeguards** - PASS: All payloads validated via Pydantic before repositories run parameterized SQLAlchemy statements; no broad CORS changes.  
- **Documentation & Knowledge Stewardship** - PASS: Spec/plan/research/data-model/quickstart/contracts files live in `specs/001-todo-field-management/` and Swagger models get updated.  
- **Testing, Deployment & Evolution** - PASS: pytest + TestClient remain primary toolchain; Alembic migration included; backward compatibility strategy documented to avoid version bumps.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-field-management/
|- spec.md
|- plan.md              # This file (/speckit.plan output)
|- research.md          # Phase 0 output
|- data-model.md        # Phase 1 output
|- quickstart.md        # Phase 1 output
|- contracts/           # Phase 1 output (OpenAPI snippets)
`- tasks.md             # Phase 2 output (/speckit.tasks; not created yet)
```

### Source Code (repository root)

```text
app/
|- api/
|  |- __init__.py
|  |- schemas.py
|  `- v1/
|     |- __init__.py
|     |- dependencies.py
|     `- routes.py
|- repositories/
|  |- __init__.py
|  `- todos.py
|- services/
|  |- __init__.py
|  `- todos.py
|- db/
|  |- __init__.py
|  |- base.py
|  |- models.py
|  `- migrations/
|- config.py
`- main.py

tests/
|- conftest.py
|- integration/
|  `- test_todos_api.py
`- unit/
   |- test_repositories_todos.py
   `- test_services_todos.py
```

**Structure Decision**: Single FastAPI backend plus pytest suites cover the entire product. Work is scoped to the shared `app/` modules (api, services, repositories, db) and the existing unit/integration tests; no new projects or frontend layers are introduced.

## Complexity Tracking

No constitution violations anticipated; table intentionally left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations introduced by this feature. | Existing architecture already satisfies requirements. |
