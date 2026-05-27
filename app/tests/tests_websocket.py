import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

@pytest.fixture
def client():
    return TestClient(app)

def test_websocket_connect_success(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "system"
        assert "alice" in data["text"]

def test_websocket_missing_username(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/python"):
            pass

def test_send_and_receive_message(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        websocket.receive_json()
        
        websocket.send_json({"type": "message", "text": "Hello World"})
        
        response = websocket.receive_json()
        assert response["type"] == "message"
        assert response["username"] == "alice"
        assert response["text"] == "Hello World"

def test_two_clients_same_room(client):
    with client.websocket_connect("/ws/rooms/same?username=alice") as ws1, \
         client.websocket_connect("/ws/rooms/same?username=bob") as ws2:
        
        ws1.receive_json()
        ws2.receive_json()
        
        ws1.send_json({"type": "message", "text": "Hello Bob"})
        
        response1 = ws1.receive_json()
        response2 = ws2.receive_json()
        
        assert response1["text"] == "Hello Bob"
        assert response2["text"] == "Hello Bob"

def test_different_rooms(client):
    with client.websocket_connect("/ws/rooms/room1?username=alice") as ws1, \
         client.websocket_connect("/ws/rooms/room2?username=bob") as ws2:
        
        ws1.receive_json()
        ws2.receive_json()
        
        ws1.send_json({"type": "message", "text": "Only in room1"})
        
        response1 = ws1.receive_json()
        
        with pytest.raises(Exception):
            ws2.receive_json(timeout=1)
        
        assert response1["text"] == "Only in room1"

def test_message_too_long(client):
    with client.websocket_connect("/ws/rooms/long?username=alice") as websocket:
        websocket.receive_json() 
        
        long_message = "x" * 301
        websocket.send_json({"type": "message", "text": long_message})
        
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "too long" in response["detail"].lower()

def test_disconnect_user(client):
    with client.websocket_connect("/ws/rooms/disco?username=alice") as websocket:
        websocket.receive_json()
        
        response = client.get("/rooms/disco/users")
        assert response.json()["users"] == ["alice"]
    
    response = client.get("/rooms/disco/users")
    assert response.json()["users"] == []