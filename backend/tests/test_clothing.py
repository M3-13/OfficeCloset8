import io

import pytest
from auth import require_auth
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from models import ClothingItem, User
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


class _MockUser:
    def __init__(self, id: int):
        self.id = id


def _overrides(user_id: int, session: Session):
    def override_get_db():
        try:
            yield session
        finally:
            pass

    def override_require_auth():
        return _MockUser(id=user_id)

    return override_get_db, override_require_auth


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    from sqlalchemy.orm import sessionmaker

    s = sessionmaker(bind=engine)()
    try:
        yield s
    finally:
        s.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user(session: Session):
    u = User(email="test@example.com", password_hash="hash")
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


@pytest.fixture
def client(user: User, session: Session, monkeypatch, tmp_path):
    upload_dir = tmp_path / "upload"
    upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("upload.UPLOAD_DIR", upload_dir)
    monkeypatch.setattr("routers.clothing.UPLOAD_DIR", upload_dir)

    ov_db, ov_auth = _overrides(user.id, session)
    app.dependency_overrides[get_db] = ov_db
    app.dependency_overrides[require_auth] = ov_auth
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _make_test_image(format: str = "JPEG") -> io.BytesIO:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    buf.name = "test"
    return buf


class TestListItems:
    def test_list_empty(self, client):
        resp = client.get("/api/clothing")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_items(self, client, user: User, session: Session):
        i1 = ClothingItem(
            name="Shirt", category="Oberteil", image_path="/uploads/x.jpg", user_id=user.id
        )
        i2 = ClothingItem(
            name="Jeans", category="Hose", image_path="/uploads/y.jpg", user_id=user.id
        )
        session.add_all([i1, i2])
        session.commit()

        resp = client.get("/api/clothing")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        names = {it["name"] for it in data}
        assert names == {"Shirt", "Jeans"}

    def test_filter_by_category(self, client, user: User, session: Session):
        i1 = ClothingItem(
            name="Shirt", category="Oberteil", image_path="/uploads/x.jpg", user_id=user.id
        )
        i2 = ClothingItem(
            name="Jeans", category="Hose", image_path="/uploads/y.jpg", user_id=user.id
        )
        session.add_all([i1, i2])
        session.commit()

        resp = client.get("/api/clothing?category=Hose")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Jeans"

    def test_filter_invalid_category(self, client):
        resp = client.get("/api/clothing?category=InvalidCat")
        assert resp.status_code == 400

    def test_other_user_items_not_visible(self, client, session: Session, user: User):
        other = User(email="other@example.com", password_hash="hash")
        session.add(other)
        session.commit()
        session.refresh(other)
        other_item = ClothingItem(
            name="Fremd", category="Oberteil", image_path="/uploads/z.jpg", user_id=other.id
        )
        session.add(other_item)
        session.commit()

        resp = client.get("/api/clothing")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 0


class TestCreateItem:
    def test_create_success(self, client):
        img_buf = _make_test_image("JPEG")
        resp = client.post(
            "/api/clothing",
            data={"name": "Blaue Jeans", "category": "Hose"},
            files={"image": ("jeans.jpg", img_buf, "image/jpeg")},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Blaue Jeans"
        assert data["category"] == "Hose"
        assert data["image_path"].startswith("/uploads/")

    def test_create_empty_name(self, client):
        img_buf = _make_test_image("JPEG")
        resp = client.post(
            "/api/clothing",
            data={"name": "", "category": "Hose"},
            files={"image": ("jeans.jpg", img_buf, "image/jpeg")},
        )
        assert resp.status_code == 422

    def test_create_name_too_long(self, client):
        img_buf = _make_test_image("JPEG")
        resp = client.post(
            "/api/clothing",
            data={"name": "A" * 101, "category": "Hose"},
            files={"image": ("jeans.jpg", img_buf, "image/jpeg")},
        )
        assert resp.status_code == 422

    def test_create_invalid_category(self, client):
        img_buf = _make_test_image("JPEG")
        resp = client.post(
            "/api/clothing",
            data={"name": "Test", "category": "Invalid"},
            files={"image": ("jeans.jpg", img_buf, "image/jpeg")},
        )
        assert resp.status_code == 422

    def test_create_no_image(self, client):
        resp = client.post(
            "/api/clothing",
            data={"name": "Test", "category": "Hose"},
        )
        assert resp.status_code == 422

    def test_create_bad_image_type(self, client):
        img_buf = _make_test_image("GIF")
        resp = client.post(
            "/api/clothing",
            data={"name": "Test", "category": "Hose"},
            files={"image": ("test.gif", img_buf, "image/gif")},
        )
        assert resp.status_code == 400


class TestDeleteItem:
    def test_delete_success(self, client, user: User, session: Session):
        item = ClothingItem(
            name="Shirt", category="Oberteil", image_path="/uploads/x.jpg", user_id=user.id
        )
        session.add(item)
        session.commit()
        session.refresh(item)

        resp = client.delete(f"/api/clothing/{item.id}")
        assert resp.status_code == 204

        get_resp = client.get("/api/clothing")
        assert len(get_resp.json()) == 0

    def test_delete_not_found(self, client):
        resp = client.delete("/api/clothing/9999")
        assert resp.status_code == 404

    def test_delete_wrong_user(self, session: Session, client, user: User):
        other = User(email="other@example.com", password_hash="hash")
        session.add(other)
        session.commit()
        session.refresh(other)

        item = ClothingItem(
            name="Fremd", category="Oberteil", image_path="/uploads/z.jpg", user_id=other.id
        )
        session.add(item)
        session.commit()
        session.refresh(item)

        resp = client.delete(f"/api/clothing/{item.id}")
        assert resp.status_code == 404


class TestRequireAuth:
    def test_unauthenticated_rejected(self):
        app.dependency_overrides.clear()
        with TestClient(app) as c:
            resp = c.get("/api/clothing")
            assert resp.status_code == 401
