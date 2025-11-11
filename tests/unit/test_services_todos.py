from __future__ import annotations

from uuid import uuid4

import pytest

from app.api import schemas
from app.repositories.todos import TodoRepository
from app.services.todos import TodoNotFoundError, TodoService


def _service(db_session) -> TodoService:
    repo = TodoRepository(session=db_session)
    return TodoService(repository=repo)


def test_create_todo_sets_defaults(db_session) -> None:
    service = _service(db_session)
    payload = schemas.TodoCreate(title="Service Layer", description="tests")
    result = service.create_todo(payload)

    assert result.title == "Service Layer"
    assert result.description == "tests"
    assert result.completed is False
    assert result.completed_at is None


def test_list_todos_returns_total_count(db_session) -> None:
    service = _service(db_session)
    service.create_todo(schemas.TodoCreate(title="First", description=None))
    service.create_todo(schemas.TodoCreate(title="Second", description=None))

    response = service.list_todos()
    assert response.total_count == 2
    titles = {item.title for item in response.items}
    assert titles == {"First", "Second"}


def test_get_todo_returns_item(db_session) -> None:
    service = _service(db_session)
    created = service.create_todo(schemas.TodoCreate(title="lookup", description=None))
    fetched = service.get_todo(created.id)
    assert fetched.id == created.id


def test_get_todo_not_found_raises(db_session) -> None:
    service = _service(db_session)
    with pytest.raises(TodoNotFoundError):
        service.get_todo(uuid4())


def test_replace_todo_updates_fields(db_session) -> None:
    service = _service(db_session)
    created = service.create_todo(schemas.TodoCreate(title="initial", description=None))
    updated = service.replace_todo(
        created.id,
        schemas.TodoUpdate(title="new", description="desc", completed=True),
    )
    assert updated.title == "new"
    assert updated.description == "desc"
    assert updated.completed is True
    assert updated.completed_at is not None


def test_patch_todo_requires_fields(db_session) -> None:
    service = _service(db_session)
    created = service.create_todo(schemas.TodoCreate(title="initial", description=None))
    with pytest.raises(ValueError):
        service.update_todo_partial(created.id, schemas.TodoPatch())


def test_patch_todo_updates_subset(db_session) -> None:
    service = _service(db_session)
    created = service.create_todo(
        schemas.TodoCreate(title="initial", description="old")
    )
    patched = service.update_todo_partial(
        created.id,
        schemas.TodoPatch(description="new"),
    )
    assert patched.description == "new"
    assert patched.title == "initial"


def test_toggle_status_updates_completed_flag(db_session) -> None:
    service = _service(db_session)
    created = service.create_todo(schemas.TodoCreate(title="toggle", description=None))
    toggled = service.toggle_status(created.id, completed=True)
    assert toggled.completed is True
    assert toggled.completed_at is not None


def test_delete_todo_removes_record(db_session) -> None:
    service = _service(db_session)
    created = service.create_todo(schemas.TodoCreate(title="delete", description=None))
    service.delete_todo(created.id)
    with pytest.raises(TodoNotFoundError):
        service.get_todo(created.id)
