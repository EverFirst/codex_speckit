# Quickstart: TODO 기본 관리
_Updated: 2025-11-11_

## 1. Prerequisites
- Python 3.11+
- pip (or uv/pipenv) and virtualenv support
- SQLite 3 (bundled with Python on most systems)

Optional:
- `make` for shortcuts
- `httpie` or `curl` for API calls

## 2. Setup
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Create `.env` (or copy `.env.example`) and set:
```
DATABASE_URL=sqlite:///./todo.db
```

## 3. Database Migration
```bash
alembic upgrade head
```

For tests / local dev you can rely on SQLite file auto-creation, but running migrations keeps schema consistent.

## 4. Run the API
```bash
uvicorn app.main:app --reload
```

Endpoints:
- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## 5. Sample Workflow
```bash
# Create
http POST :8000/todos title="Read spec" description="finish clarify"
# List
http GET :8000/todos
# Toggle complete
http PATCH :8000/todos/<id>/status completed:=true
# Update
http PUT :8000/todos/<id> title="Read plan" description="update doc"
# Delete
http DELETE :8000/todos/<id>
```

All responses are JSON and include `created_at`, `updated_at`, and `completed_at`.

## 6. Testing & Coverage
```bash
pytest --cov=app --cov-report=term-missing
```

- Unit tests live under `tests/unit`.
- Integration/API tests use FastAPI TestClient under `tests/integration`.
- Coverage threshold: 70% minimum (CI should fail otherwise).

## 7. Coding Standards
- Run `black .` and `isort .` before committing.
- Use TDD: write failing test, implement, refactor.
- Keep Swagger docs in sync; FastAPI auto-generates once routers/schemas updated.

## 8. Troubleshooting
- **SQLite locking**: ensure single uvicorn worker locally; for tests use in-memory DB fixtures.
- **Migrations missing**: run `alembic revision --autogenerate -m "create todos"` before `upgrade head`.
- **Slow responses (>200ms)**: check for `time.sleep` or heavy loops; list endpoint should be single SELECT with ORDER BY created_at DESC.
