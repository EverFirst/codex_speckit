from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from app.db.models import todos


def _row_to_dict(row) -> dict[str, Any]:
    data = dict(row._mapping)
    data["tags"] = _deserialize_tags(data.get("tags"))
    return data


def _normalize_id(todo_id: UUID | str) -> str:
    return str(todo_id)


def _deserialize_tags(value: Optional[str]) -> list[str]:
    if value in (None, "", "null"):
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return []


def _serialize_tags(value: Optional[list[str]]) -> Optional[str]:
    if not value:
        return None
    return json.dumps(value)


def _prepare_write_data(data: dict[str, Any]) -> dict[str, Any]:
    prepared = data.copy()
    if "tags" in prepared:
        prepared["tags"] = _serialize_tags(prepared["tags"])
    return prepared


@dataclass
class TodoRepository:
    session: Session

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        db_data = _prepare_write_data(data)
        self.session.execute(insert(todos).values(**db_data))
        self.session.commit()
        return data

    def list_all(self) -> list[dict[str, Any]]:
        result = self.session.execute(select(todos).order_by(todos.c.created_at.desc()))
        return [_row_to_dict(row) for row in result]

    def get(self, todo_id: UUID | str) -> Optional[dict[str, Any]]:
        result = self.session.execute(
            select(todos).where(todos.c.id == _normalize_id(todo_id))
        ).first()
        if result is None:
            return None
        return _row_to_dict(result)

    def _update(
        self, todo_id: UUID | str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        db_data = _prepare_write_data(data)
        result = self.session.execute(
            update(todos).where(todos.c.id == _normalize_id(todo_id)).values(**db_data)
        )
        if result.rowcount == 0:
            self.session.rollback()
            return None
        self.session.commit()
        return self.get(todo_id)

    def update_full(
        self, todo_id: UUID | str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return self._update(todo_id, data)

    def update_partial(
        self, todo_id: UUID | str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return self._update(todo_id, data)

    def toggle_status(
        self, todo_id: UUID | str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return self._update(todo_id, data)

    def delete(self, todo_id: UUID | str) -> bool:
        result = self.session.execute(
            delete(todos).where(todos.c.id == _normalize_id(todo_id))
        )
        if result.rowcount == 0:
            self.session.rollback()
            return False
        self.session.commit()
        return True
