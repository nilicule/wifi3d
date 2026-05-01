import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_generate_stl_returns_binary():
    resp = client.post("/api/generate", json={
        "ssid": "TestNet", "password": "pw", "auth_type": "WPA",
        "format": "stl"
    })
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/octet-stream"
    assert len(resp.content) > 84


def test_generate_3mf_returns_zip():
    resp = client.post("/api/generate", json={
        "ssid": "TestNet", "password": "pw", "auth_type": "WPA",
        "format": "3mf"
    })
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"


def test_preview_returns_json():
    resp = client.post("/api/preview", json={
        "ssid": "TestNet", "password": "pw", "auth_type": "WPA"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "plate_vertices" in data
    assert "module_vertices" in data
    assert isinstance(data["plate_vertices"], list)


def test_invalid_ssid_returns_422():
    resp = client.post("/api/generate", json={
        "ssid": "", "password": "pw", "auth_type": "WPA", "format": "stl"
    })
    assert resp.status_code == 422
