from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models as db_models


def _create(
    client: TestClient,
    title: str = "Write spec",
    description: str | None = "Finalize Phase 3",
) -> dict:
    payload = {"title": title, "description": description}
    response = client.post("/todos", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_todo_success(client: TestClient) -> None:
    data = _create(client)
    assert data["title"] == "Write spec"
    assert data["completed"] is False
    assert data["completed_at"] is None
    assert "id" in data
    assert "created_at" in data and "updated_at" in data


def test_list_todos_returns_descending(client: TestClient) -> None:
    _create(client, title="First", description="alpha")
    _create(client, title="Second", description="beta")

    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 2
    titles = [item["title"] for item in data["items"]]
    assert titles[0] == "Second"
    assert titles[1] == "First"


def test_create_todo_validation_error(client: TestClient) -> None:
    response = client.post("/todos", json={"title": "", "description": "invalid"})
    assert response.status_code == 422


def test_get_todo_detail(client: TestClient) -> None:
    todo = _create(client)
    response = client.get(f"/todos/{todo['id']}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["id"] == todo["id"]
    assert fetched["title"] == todo["title"]


def test_get_todo_not_found_returns_404(client: TestClient) -> None:
    response = client.get(f"/todos/{uuid4()}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "TODO not found",
        "error_code": "TODO_NOT_FOUND",
    }


def test_put_todo_updates_fields(client: TestClient) -> None:
    todo = _create(client)
    payload = {"title": "Updated title", "description": "new desc", "completed": True}
    response = client.put(f"/todos/{todo['id']}", json=payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Updated title"
    assert updated["description"] == "new desc"
    assert updated["completed"] is True
    assert updated["completed_at"] is not None


def test_patch_todo_partial_update(client: TestClient) -> None:
    todo = _create(client)
    response = client.patch(f"/todos/{todo['id']}", json={"description": "patched"})
    assert response.status_code == 200
    patched = response.json()
    assert patched["description"] == "patched"
    assert patched["title"] == todo["title"]


def test_patch_without_fields_returns_400(client: TestClient) -> None:
    todo = _create(client)
    response = client.patch(f"/todos/{todo['id']}", json={})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "No fields to update",
        "error_code": "INVALID_PATCH",
    }


def test_toggle_status_endpoint(client: TestClient) -> None:
    todo = _create(client)
    res = client.patch(f"/todos/{todo['id']}/status", json={"completed": True})
    assert res.status_code == 200
    body = res.json()
    assert body["completed"] is True
    assert body["completed_at"] is not None

    res = client.patch(f"/todos/{todo['id']}/status", json={"completed": False})
    assert res.status_code == 200
    assert res.json()["completed"] is False
    assert res.json()["completed_at"] is None


def test_delete_todo_endpoint(client: TestClient) -> None:
    todo = _create(client)
    res = client.delete(f"/todos/{todo['id']}")
    assert res.status_code == 204
    res = client.get(f"/todos/{todo['id']}")
    assert res.status_code == 404
