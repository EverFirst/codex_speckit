from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from app.api import schemas
from app.repositories.todos import TodoRepository


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TodoNotFoundError(Exception):
    """Raised when requested todo does not exist."""


@dataclass
class TodoService:
    repository: TodoRepository

    def create_todo(self, payload: schemas.TodoCreate) -> schemas.TodoResponse:
        now = _utcnow()
        todo_dict = {
            "id": str(uuid4()),
            "title": payload.title,
            "description": payload.description,
            "completed": False,
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
        }
        self.repository.create(todo_dict)
        return schemas.TodoResponse(**todo_dict)

    def list_todos(self) -> schemas.TodoListResponse:
        items = [schemas.TodoResponse(**row) for row in self.repository.list_all()]
        return schemas.TodoListResponse(total_count=len(items), items=items)

    def get_todo(self, todo_id: UUID) -> schemas.TodoResponse:
        record = self.repository.get(todo_id)
        if not record:
            raise TodoNotFoundError
        return schemas.TodoResponse(**record)

    def replace_todo(
        self, todo_id: UUID, payload: schemas.TodoUpdate
    ) -> schemas.TodoResponse:
        now = _utcnow()
        data = {
            "title": payload.title,
            "description": payload.description,
            "completed": payload.completed,
            "completed_at": now if payload.completed else None,
            "updated_at": now,
        }
        updated = self.repository.update_full(todo_id, data)
        if not updated:
            raise TodoNotFoundError
        return schemas.TodoResponse(**updated)

    def update_todo_partial(
        self, todo_id: UUID, payload: schemas.TodoPatch
    ) -> schemas.TodoResponse:
        now = _utcnow()
        data: dict[str, Optional[bool | str | datetime]] = {}
        if payload.title is not None:
            data["title"] = payload.title
        if payload.description is not None:
            data["description"] = payload.description
        if payload.completed is not None:
            data["completed"] = payload.completed
            data["completed_at"] = now if payload.completed else None
        if not data:
            raise ValueError("No fields to update")
        data["updated_at"] = now
        updated = self.repository.update_partial(todo_id, data)
        if not updated:
            raise TodoNotFoundError
        return schemas.TodoResponse(**updated)

    def toggle_status(self, todo_id: UUID, completed: bool) -> schemas.TodoResponse:
        now = _utcnow()
        data = {
            "completed": completed,
            "completed_at": now if completed else None,
            "updated_at": now,
        }
        updated = self.repository.toggle_status(todo_id, data)
        if not updated:
            raise TodoNotFoundError
        return schemas.TodoResponse(**updated)

    def delete_todo(self, todo_id: UUID) -> None:
        success = self.repository.delete(todo_id)
        if not success:
            raise TodoNotFoundError
