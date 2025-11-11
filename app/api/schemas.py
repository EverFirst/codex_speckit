from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

PriorityLiteral = Literal["low", "medium", "high"]


class _TrimmedModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


def _validate_tags(value: List[str]) -> List[str]:
    if len(value) > 10:
        raise ValueError("Maximum of 10 tags allowed")
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in value:
        if len(tag) > 20:
            raise ValueError("Tags must be 20 characters or fewer")
        lowered = tag.lower()
        if lowered in seen:
            raise ValueError("Duplicate tags are not allowed")
        seen.add(lowered)
        normalized.append(tag)
    return normalized


class TodoBase(_TrimmedModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = None
    priority: PriorityLiteral = "medium"
    category: Optional[str] = Field(default=None, max_length=50)
    tags: List[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def enforce_tag_rules(cls, value: List[str]) -> List[str]:
        return _validate_tags(value)


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    completed: bool = False


class TodoPatch(_TrimmedModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None
    due_date: Optional[date] = None
    priority: Optional[PriorityLiteral] = None
    category: Optional[str] = Field(default=None, max_length=50)
    tags: Optional[List[str]] = None

    @field_validator("tags")
    @classmethod
    def enforce_patch_tags(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        return _validate_tags(value)


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
