import pytest
from app.storage import get_storage


def test_create_task_success(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": 3
        },
        headers={"X-User-Id": "10"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Task"
    assert data["owner_id"] == 10
    assert data["status"] == "todo"


def test_create_task_invalid_title_short(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "ab",
            "description": "Test",
            "status": "todo",
            "priority": 3
        },
        headers={"X-User-Id": "10"}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_create_task_missing_user_id(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test",
            "status": "todo",
            "priority": 3
        }
    )
    
    assert response.status_code == 401
    assert "X-User-Id header is required" in response.json()["detail"]


def test_user_sees_only_own_tasks(client):
    client.post(
        "/tasks/",
        json={"title": "Task for user 10", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    client.post(
        "/tasks/",
        json={"title": "Task for user 20", "priority": 3},
        headers={"X-User-Id": "20"}
    )
    response = client.get("/tasks/", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task for user 10"


def test_filter_tasks_by_status_and_priority(client):
    client.post("/tasks/", json={"title": "Task 1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Task 2", "status": "in_progress", "priority": 3}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Task 3", "status": "done", "priority": 5}, headers={"X-User-Id": "10"})
    response = client.get("/tasks/?status=in_progress", headers={"X-User-Id": "10"})
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "in_progress"
    response = client.get("/tasks/?min_priority=4", headers={"X-User-Id": "10"})
    assert len(response.json()) == 1
    assert response.json()[0]["priority"] == 5


def test_update_task_status_success(client):
    create_response = client.post(
        "/tasks/",
        json={"title": "Test Task", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]
    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers={"X-User-Id": "10"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_access_foreign_task_returns_404(client):
    create_response = client.post(
        "/tasks/",
        json={"title": "User 10 Task", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]
    response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404


def test_delete_task_success(client):
    create_response = client.post(
        "/tasks/",
        json={"title": "Task to delete", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]
    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 204
    get_response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_response.status_code == 404


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data