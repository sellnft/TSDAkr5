import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_storage
from app.storage import TaskStorage

@pytest.fixture
def client():
    storage = get_storage()
    storage.clear()
    return TestClient(app)

def test_users_me_endpoint(client):
    response = client.get("/users/users/me", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["role"] == "user"

def test_users_me_no_header(client):
    response = client.get("/users/users/me")
    assert response.status_code == 401

def test_admin_stats_regular_user(client):
    response = client.get("/admin/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 403

def test_admin_stats_admin_user(client):
    client.post("/tasks/tasks", json={"title": "Task1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    client.post("/tasks/tasks", json={"title": "Task2", "status": "done", "priority": 2}, headers={"X-User-Id": "20"})
    client.post("/tasks/tasks", json={"title": "Task3", "status": "todo", "priority": 3}, headers={"X-User-Id": "10"})
    
    response = client.get("/admin/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["by_status"]["todo"] == 2
    assert data["by_status"]["done"] == 1

def test_regular_user_cannot_delete_others_task(client):
    response = client.post("/tasks/tasks", json={"title": "Task", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = response.json()["id"]
    
    response = client.delete(f"/tasks/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404

def test_admin_can_delete_any_task(client):
    response = client.post("/tasks/tasks", json={"title": "Task", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = response.json()["id"]
    
    response = client.delete(f"/admin/admin/tasks/{task_id}", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 204
    
    response = client.get(f"/tasks/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 404

def test_swagger_tags(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    tags = [tag["name"] for tag in data["tags"]]
    assert "tasks" in tags
    assert "users" in tags
    assert "admin" in tags