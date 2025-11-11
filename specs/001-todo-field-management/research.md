# Research Notes - TODO Advanced Field Management

## Decision 1: Persist tags as JSON text on the todos table
- **Decision**: Use a nullable `tags` TEXT column that stores the ordered list as JSON (list of lowercase strings).
- **Rationale**: SQLite lacks a native JSON array type with length constraints, but TEXT plus JSON serialization keeps ordering without a join table and can be validated in Python before persistence. It also matches the migration guidance (`tags TEXT NULL`).
- **Alternatives considered**:
  - Separate `todo_tags` table with one row per tag: adds referential integrity but complicates ordering and increases query joins for every GET.
  - SQLite JSON1 virtual columns: unavailable across all developer environments and harder to keep migrations portable.

## Decision 2: Centralize validation and normalization in Pydantic schemas
- **Decision**: Extend `TodoCreate`, `TodoUpdate`, and `TodoResponse` schemas to normalize tags to lowercase, enforce max lengths/counts, and ensure enums for `priority` while allowing nullable optional fields.
- **Rationale**: Pydantic already guards the API boundary; keeping validation there prevents duplicated checks in services/repositories and guarantees error payloads conform to FastAPI's standard 422 structure.
- **Alternatives considered**:
  - Service-layer validation: harder to reuse for both POST/PUT/PATCH and increases risk of bypass when tests interact via the API schemas.
  - Database constraints or triggers: SQLite cannot easily enforce list length or lowercase normalization without custom functions.

## Decision 3: Allow past due dates if they pass ISO validation
- **Decision**: Accept any valid `YYYY-MM-DD` date even if earlier than "today".
- **Rationale**: Backlog imports and historical tracking remain valid use cases; rejecting past dates would force clients to omit information or fake values. Feature spec explicitly calls out that past dates are acceptable.
- **Alternatives considered**:
  - Reject past dates: conflicts with requirement and would require server clock access inside validation, complicating deterministic testing.
  - Auto-clamp to today: silently mutates user intent and risks data integrity issues when auditing.

## Decision 4: Single Alembic migration 0002 with SQLAlchemy metadata alignment
- **Decision**: Author `app/db/migrations/versions/0002_add_advanced_fields.py` to add the four columns (`due_date`, `priority`, `category`, `tags`) with defaults/nullability matching SQLAlchemy models and repositories.
- **Rationale**: Aligning migration plus metadata ensures `alembic upgrade head` and application metadata stay consistent; defaulting priority to `'medium'` satisfies the spec and keeps existing rows valid.
- **Alternatives considered**:
  - Multiple migrations (one per column): unnecessary churn and prolongs rollout risk.
  - Manual `ALTER TABLE` outside Alembic: violates the constitution (schema changes must be tracked) and complicates CI automation.

## Decision 5: Test-first workflow touching unit and integration layers
- **Decision**: Create failing pytest cases in `tests/unit/test_services_todos.py`, `tests/unit/test_repositories_todos.py`, and `tests/integration/test_todos_api.py` before implementation to cover validation, persistence, and serialization paths.
- **Rationale**: Preserves the >=70% coverage mandate, proves backwards compatibility (legacy payloads still succeed), and guards the API contract across layers.
- **Alternatives considered**:
  - Adding only integration tests: slower feedback and weaker coverage of repository/service edge cases.
  - Adding only unit tests: risks missing FastAPI/Pydantic behavior regressions on the wire format.
