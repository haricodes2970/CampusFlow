import pytest
from fastapi.testclient import TestClient


def test_cors_preflight_allowed_origin(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app")
    from app.config import get_settings
    get_settings.cache_clear()
    
    from app.main import app
    client = TestClient(app)

    response = client.options(
        "/api/stats",
        headers={
            "Origin": "https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app"
    assert "GET" in response.headers.get("access-control-allow-methods", "")


def test_cors_preflight_unscheduled_endpoint(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app")
    from app.config import get_settings
    get_settings.cache_clear()
    
    from app.main import app
    client = TestClient(app)

    response = client.options(
        "/api/timetable/unscheduled",
        headers={
            "Origin": "https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app"


def test_cors_actual_request_allowed_origin(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app")
    from app.config import get_settings
    get_settings.cache_clear()
    
    from app.main import app
    client = TestClient(app)

    response = client.get(
        "/api/stats",
        headers={
            "Origin": "https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://campusflow-4ajiwvubu-haricodes2970s-projects.vercel.app"
