from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _TrimmedModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class TodoBase(_TrimmedModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    completed: bool = False


class TodoPatch(_TrimmedModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None


class TodoToggle(BaseModel):
    completed: bool


class TodoResponse(TodoBase):
    id: UUID
    completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class TodoListResponse(BaseModel):
    total_count: int
    items: List[TodoResponse]


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
