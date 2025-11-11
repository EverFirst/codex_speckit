from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.repositories.todos import TodoRepository


def _todo_dict(ts: datetime | None = None) -> dict:
    now = ts or datetime.now(timezone.utc)
    return {
        "id": str(uuid4()),
        "title": "Repo Test",
        "description": "testing repo create/list",
        "completed": False,
        "created_at": now,
        "updated_at": now,
        "completed_at": None,
    }


def test_create_and_list(db_session) -> None:
    repo = TodoRepository(session=db_session)
    todo_data = _todo_dict()
    repo.create(todo_data)

    results = repo.list_all()
    assert len(results) == 1
    assert results[0]["id"] == todo_data["id"]
    assert results[0]["title"] == "Repo Test"


def test_list_orders_by_created_at_desc(db_session) -> None:
    repo = TodoRepository(session=db_session)
    base = datetime.now(timezone.utc)
    first = _todo_dict(ts=base)
    second = _todo_dict(ts=base + timedelta(seconds=1))
    repo.create(first)
    repo.create(second)

    results = repo.list_all()
    assert results[0]["id"] == second["id"]
    assert results[1]["id"] == first["id"]


def test_get_and_update(db_session) -> None:
    repo = TodoRepository(session=db_session)
    todo = _todo_dict()
    repo.create(todo)

    fetched = repo.get(UUID(todo["id"]))
    assert fetched["title"] == "Repo Test"

    repo.update_full(
        UUID(todo["id"]),
        {
            "title": "changed",
            "description": "x",
            "updated_at": datetime.now(timezone.utc),
            "completed": False,
            "completed_at": None,
        },
    )
    updated = repo.get(UUID(todo["id"]))
    assert updated["title"] == "changed"


def test_delete_returns_boolean(db_session) -> None:
    repo = TodoRepository(session=db_session)
    todo = _todo_dict()
    repo.create(todo)
    assert repo.delete(UUID(todo["id"])) is True
    assert repo.delete(UUID(todo["id"])) is False
