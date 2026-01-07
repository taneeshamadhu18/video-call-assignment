from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_participants():
    res = client.get("/participants")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_search_participant():
    res = client.get("/participants", params={"search": "Alice"})
    assert res.status_code == 200


def test_toggle_microphone():
    res = client.patch("/api/participants/1/microphone", json={"mic_on": False})


    assert res.status_code == 200
    assert res.json()["mic_on"] is False


def test_toggle_camera():
    res = client.patch("/api/participants/1/camera", json={"camera_on": False})
    assert res.status_code == 200
    assert res.json()["camera_on"] is False
