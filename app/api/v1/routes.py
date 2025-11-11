from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api import schemas
from app.api.v1.dependencies import get_todo_repository
from app.repositories.todos import TodoRepository
from app.services.todos import TodoNotFoundError, TodoService

router = APIRouter(prefix="/todos", tags=["todos"])

ERROR_NOT_FOUND = ("TODO not found", "TODO_NOT_FOUND")
ERROR_INVALID_PATCH = ("No fields to update", "INVALID_PATCH")


def get_service(repo: TodoRepository) -> TodoService:
    return TodoService(repository=repo)


def _error_response(status_code: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"detail": message, "error_code": code}
    )


def _handle_not_found(exc: TodoNotFoundError) -> JSONResponse:
    return _error_response(status.HTTP_404_NOT_FOUND, *ERROR_NOT_FOUND)


@router.post(
    "",
    response_model=schemas.TodoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_todo(
    payload: schemas.TodoCreate,
    repo: TodoRepository = Depends(get_todo_repository),
) -> schemas.TodoResponse:
    service = get_service(repo)
    return service.create_todo(payload)


@router.get(
    "",
    response_model=schemas.TodoListResponse,
    status_code=status.HTTP_200_OK,
)
def list_todos(
    repo: TodoRepository = Depends(get_todo_repository),
) -> schemas.TodoListResponse:
    service = get_service(repo)
    return service.list_todos()


@router.get(
    "/{todo_id}",
    response_model=schemas.TodoResponse,
    responses={404: {"model": schemas.ErrorResponse}},
)
def get_todo(
    todo_id: UUID, repo: TodoRepository = Depends(get_todo_repository)
) -> schemas.TodoResponse:
    service = get_service(repo)
    try:
        return service.get_todo(todo_id)
    except TodoNotFoundError as exc:
        return _handle_not_found(exc)


@router.put(
    "/{todo_id}",
    response_model=schemas.TodoResponse,
    responses={404: {"model": schemas.ErrorResponse}},
)
def replace_todo(
    todo_id: UUID,
    payload: schemas.TodoUpdate,
    repo: TodoRepository = Depends(get_todo_repository),
) -> schemas.TodoResponse:
    service = get_service(repo)
    try:
        return service.replace_todo(todo_id, payload)
    except TodoNotFoundError as exc:
        return _handle_not_found(exc)


@router.patch(
    "/{todo_id}",
    response_model=schemas.TodoResponse,
    responses={
        404: {"model": schemas.ErrorResponse},
        400: {"model": schemas.ErrorResponse},
    },
)
def update_todo_partial(
    todo_id: UUID,
    payload: schemas.TodoPatch,
    repo: TodoRepository = Depends(get_todo_repository),
) -> schemas.TodoResponse:
    service = get_service(repo)
    try:
        return service.update_todo_partial(todo_id, payload)
    except TodoNotFoundError as exc:
        return _handle_not_found(exc)
    except ValueError:
        return _error_response(status.HTTP_400_BAD_REQUEST, *ERROR_INVALID_PATCH)


@router.patch(
    "/{todo_id}/status",
    response_model=schemas.TodoResponse,
    responses={404: {"model": schemas.ErrorResponse}},
)
def toggle_todo_status(
    todo_id: UUID,
    payload: schemas.TodoToggle,
    repo: TodoRepository = Depends(get_todo_repository),
) -> schemas.TodoResponse:
    service = get_service(repo)
    try:
        return service.toggle_status(todo_id, completed=payload.completed)
    except TodoNotFoundError as exc:
        return _handle_not_found(exc)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": schemas.ErrorResponse}},
)
def delete_todo(
    todo_id: UUID, repo: TodoRepository = Depends(get_todo_repository)
) -> None:
    service = get_service(repo)
    try:
        service.delete_todo(todo_id)
    except TodoNotFoundError as exc:
        return _handle_not_found(exc)
