import pytest


def test_users_me_endpoint(client):
    response = client.get("/users/me", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["role"] == "user"


def test_users_me_missing_header(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_admin_stats_regular_user_forbidden(client):
    response = client.get("/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 403


def test_admin_stats_admin_access(client):
    client.post("/tasks/", json={"title": "Task 1", "status": "todo", "priority": 3}, headers={"X-User-Id": "1"})
    client.post("/tasks/", json={"title": "Task 2", "status": "in_progress", "priority": 4}, headers={"X-User-Id": "2"})
    client.post("/tasks/", json={"title": "Task 3", "status": "done", "priority": 5}, headers={"X-User-Id": "1"})
    
    response = client.get("/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["by_status"]["todo"] == 1
    assert data["by_status"]["in_progress"] == 1
    assert data["by_status"]["done"] == 1


def test_regular_user_cannot_delete_foreign_task(client):
    create_response = client.post(
        "/tasks/",
        json={"title": "User 10 Task", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404


def test_admin_can_delete_any_task(client):
    create_response = client.post(
        "/tasks/",
        json={"title": "User 10 Task", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/admin/tasks/{task_id}", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 204
    
    get_response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_response.status_code == 404


def test_swagger_tags_present(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    
    tags = [tag["name"] for tag in data.get("tags", [])]
    assert "tasks" in tags
    assert "users" in tags
    assert "admin" in tags