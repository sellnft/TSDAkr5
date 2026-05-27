import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_storage
from app.storage import TaskStorage

@pytest.fixture
def client():
    # Очищаем хранилище перед каждым тестом
    storage = get_storage()
    storage.clear()
    return TestClient(app)

def test_create_task_success(client):
    response = client.post(
        "/tasks/tasks",
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
    assert data["title"] == "Test Task"
    assert data["owner_id"] == 10
    assert "id" in data

def test_create_task_invalid_title(client):
    response = client.post(
        "/tasks/tasks",
        json={
            "title": "Te",  # Too short
            "description": "Test",
            "status": "todo",
            "priority": 3
        },
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 422

def test_create_task_no_user_id(client):
    response = client.post(
        "/tasks/tasks",
        json={
            "title": "Test Task",
            "description": "Test",
            "status": "todo",
            "priority": 3
        }
    )
    assert response.status_code == 401

def test_user_sees_only_own_tasks(client):
    # Создаем задачи для двух пользователей
    client.post("/tasks/tasks", json={"title": "Task1", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    client.post("/tasks/tasks", json={"title": "Task2", "status": "todo", "priority": 1}, headers={"X-User-Id": "20"})
    
    response = client.get("/tasks/tasks", headers={"X-User-Id": "10"})
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["owner_id"] == 10

def test_filter_tasks_by_status_and_priority(client):
    client.post("/tasks/tasks", json={"title": "Task1", "status": "todo", "priority": 2}, headers={"X-User-Id": "10"})
    client.post("/tasks/tasks", json={"title": "Task2", "status": "done", "priority": 4}, headers={"X-User-Id": "10"})
    client.post("/tasks/tasks", json={"title": "Task3", "status": "todo", "priority": 5}, headers={"X-User-Id": "10"})
    
    response = client.get("/tasks/tasks?status=todo&min_priority=3", headers={"X-User-Id": "10"})
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task3"

def test_update_task_status(client):
    response = client.post("/tasks/tasks", json={"title": "Task", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = response.json()["id"]
    
    response = client.patch(f"/tasks/tasks/{task_id}/status", json={"status": "done"}, headers={"X-User-Id": "10"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"

def test_get_nonexistent_task(client):
    response = client.get("/tasks/tasks/999", headers={"X-User-Id": "10"})
    assert response.status_code == 404

def test_delete_task(client):
    response = client.post("/tasks/tasks", json={"title": "Task", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    task_id = response.json()["id"]
    
    response = client.delete(f"/tasks/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 204
    
    response = client.get(f"/tasks/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 404

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"