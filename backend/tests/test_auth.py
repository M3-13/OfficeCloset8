from fastapi.testclient import TestClient
from main import app

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "securepassword123"


def _extract_cookies(resp):
    result = {}
    for cookie in resp.headers.get_list("set-cookie"):
        if "=" in cookie:
            key, rest = cookie.split("=", 1)
            val = rest.split(";")[0]
            result[key] = val
    return result


def test_register_creates_user_and_session():
    with TestClient(app) as c:
        resp = c.post(
            "/api/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] is not None
        assert data["email"] == TEST_EMAIL
        assert "password_hash" not in data
        cookies = _extract_cookies(resp)
        assert "session" in cookies


def test_register_duplicate_rejected():
    with TestClient(app) as c:
        c.post(
            "/api/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        resp = c.post(
            "/api/auth/register",
            json={"email": TEST_EMAIL, "password": "anotherpassword1"},
        )
        assert resp.status_code == 409


def test_register_invalid_email():
    with TestClient(app) as c:
        resp = c.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": TEST_PASSWORD},
        )
        assert resp.status_code == 422


def test_register_short_password():
    with TestClient(app) as c:
        resp = c.post(
            "/api/auth/register",
            json={"email": "shortpw@example.com", "password": "1234567"},
        )
        assert resp.status_code == 422


def test_login_valid():
    with TestClient(app) as c:
        c.post(
            "/api/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        resp = c.post(
            "/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == TEST_EMAIL
        assert "password_hash" not in data
        cookies = _extract_cookies(resp)
        assert "session" in cookies


def test_login_wrong_password():
    with TestClient(app) as c:
        c.post(
            "/api/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        resp = c.post(
            "/api/auth/login",
            json={"email": TEST_EMAIL, "password": "wrongpassword1"},
        )
        assert resp.status_code == 401


def test_login_unknown_email():
    with TestClient(app) as c:
        resp = c.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": TEST_PASSWORD},
        )
        assert resp.status_code == 401


def test_me_unauthenticated():
    with TestClient(app) as c:
        resp = c.get("/api/auth/me")
        assert resp.status_code == 401


def test_me_authenticated():
    with TestClient(app) as c:
        reg = c.post(
            "/api/auth/register",
            json={"email": "me_test@example.com", "password": TEST_PASSWORD},
        )
        assert reg.status_code == 201
        session_token = _extract_cookies(reg).get("session", "")
        c.cookies.set("session", session_token)
        resp = c.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "me_test@example.com"
        assert "password_hash" not in data


def test_logout():
    with TestClient(app) as c:
        reg = c.post(
            "/api/auth/register",
            json={"email": "logout_test@example.com", "password": TEST_PASSWORD},
        )
        assert reg.status_code == 201
        session_token = _extract_cookies(reg).get("session", "")
        c.cookies.set("session", session_token)

        resp = c.post("/api/auth/logout")
        assert resp.status_code == 200

        me_resp = c.get("/api/auth/me")
        assert me_resp.status_code == 401


def test_full_register_login_logout_flow():
    with TestClient(app) as c:
        r1 = c.post(
            "/api/auth/register",
            json={"email": "flow@example.com", "password": TEST_PASSWORD},
        )
        assert r1.status_code == 201

        c.cookies.set("session", _extract_cookies(r1).get("session", ""))
        me1 = c.get("/api/auth/me")
        assert me1.status_code == 200

        c.post("/api/auth/logout")
        me2 = c.get("/api/auth/me")
        assert me2.status_code == 401

        r2 = c.post(
            "/api/auth/login",
            json={"email": "flow@example.com", "password": TEST_PASSWORD},
        )
        assert r2.status_code == 200

        c.cookies.set("session", _extract_cookies(r2).get("session", ""))
        me3 = c.get("/api/auth/me")
        assert me3.status_code == 200
        assert me3.json()["email"] == "flow@example.com"


def test_auth_endpoints_return_cors_headers():
    with TestClient(app) as c:
        resp = c.options(
            "/api/auth/register",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert resp.status_code == 200
        assert "access-control-allow-origin" in resp.headers
