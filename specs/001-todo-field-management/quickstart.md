# Quickstart - TODO Advanced Field Management

## Prerequisites
- Python 3.11.x with `pip` and `venv`.
- SQLite 3 (bundled with Python) and Alembic configured via `alembic.ini`.
- Existing Feature 001 database (or run `alembic upgrade head` once to create it).

## Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply the new migration (after authoring `0002_add_advanced_fields.py`):
   ```bash
   alembic upgrade head
   ```
4. Run the FastAPI app for manual testing:
   ```bash
   uvicorn app.main:app --reload
   ```

## Test-Driven Workflow
1. Start by adding failing unit tests in:
   - `tests/unit/test_repositories_todos.py`
   - `tests/unit/test_services_todos.py`
2. Add failing integration tests in `tests/integration/test_todos_api.py` that cover:
   - Creating a TODO with due_date/priority/category/tags
   - Updating/removing those fields
   - Validation errors (bad date, >10 tags, duplicate tags, tag >20 chars)
3. Run the full test suite with coverage:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```
   Ensure coverage stays >=70%.
4. Implement repository/service/API/schema changes until the suite is green, then refactor if needed.

## Manual Verification Checklist
1. `POST /api/v1/todos` with:
   ```json
   {
     "title": "Ship docs",
     "priority": "high",
     "due_date": "2025-12-31",
     "category": "Work",
     "tags": ["release", "q4"]
   }
   ```
   Expect 201 response; follow up with `GET /api/v1/todos/{id}` to confirm stored values and lowercase tags.
2. `PUT /api/v1/todos/{id}` replacing the entire `tags` list (send full array). Existing tags must be replaced by the normalized payload.
3. Send a payload with 11 tags or a tag longer than 20 characters; expect HTTP 422 validation errors.
4. Create a TODO without optional fields; ensure `GET` returns `priority="medium"`, `due_date=null`, `category=null`, `tags=[]` (or omitted per schema) demonstrating backward compatibility.
5. Verify Swagger UI (`/docs`) shows the new optional fields and validation notes.

## Operations Notes
- Keep Swagger enabled in all environments and regenerate OpenAPI JSON if you export client SDKs.
- Remember to document the migration in release notes and communicate that past due dates are allowed but must be ISO formatted.
- When seeding data, always provide lowercase tags or rely on the new normalization helper to avoid surprises.
