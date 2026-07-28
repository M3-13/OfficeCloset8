from fastapi.testclient import TestClient
from main import app


def test_health():
    with TestClient(app) as c:
        resp = c.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_cors_headers():
    with TestClient(app) as c:
        resp = c.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
        assert "access-control-allow-origin" in resp.headers
