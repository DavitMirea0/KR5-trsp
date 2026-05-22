import pytest


def test_websocket_connect_valid(client):
    with client.websocket_connect("/ws/rooms/test?username=alice"):
        pass


def test_websocket_connect_invalid_username(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/test?username="):
            pass


def test_send_and_receive_message(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        websocket.send_json({"type": "message", "text": "Hello, world!"})
        response = websocket.receive_json()
        assert response["type"] == "message"
        assert response["room_id"] == "test"
        assert response["username"] == "alice"
        assert response["text"] == "Hello, world!"


def test_two_clients_same_room(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket1, \
         client.websocket_connect("/ws/rooms/test?username=bob") as websocket2:
        
        websocket1.send_json({"type": "message", "text": "Hello everyone!"})
        
        response1 = websocket1.receive_json()
        response2 = websocket2.receive_json()
        
        assert response1["text"] == "Hello everyone!"
        assert response2["text"] == "Hello everyone!"


def test_different_rooms_isolation(client):
    with client.websocket_connect("/ws/rooms/room1?username=alice") as websocket1, \
         client.websocket_connect("/ws/rooms/room2?username=bob") as websocket2:
        
        websocket1.send_json({"type": "message", "text": "Message in room1"})
        
        response1 = websocket1.receive_json()
        assert response1["text"] == "Message in room1"
        
        with pytest.raises(Exception):
            websocket2.receive_json(timeout=1)


def test_message_too_long(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        long_text = "x" * 301
        
        websocket.send_json({"type": "message", "text": long_text})
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "Message is too long" in response["detail"]


def test_room_users_endpoint(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket1, \
         client.websocket_connect("/ws/rooms/test?username=bob") as websocket2:
        
        import time
        time.sleep(0.1)
        
        response = client.get("/rooms/test/users")
        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == "test"
        assert set(data["users"]) == {"alice", "bob"}