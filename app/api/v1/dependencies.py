from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.repositories.todos import TodoRepository


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_todo_repository(db: Session = Depends(get_db)) -> TodoRepository:
    return TodoRepository(session=db)
