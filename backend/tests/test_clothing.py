import io
import tempfile
from pathlib import Path

from auth import require_auth
from database import Base, SessionLocal, engine
from fastapi.testclient import TestClient
from main import app
from models import ClothingItem, User
from PIL import Image
from sqlalchemy.orm import Session


def _make_jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color="red")
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _create_user(db: Session, email: str = "test@example.com") -> User:
    user = User(email=email, password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _override_require_auth(user_id: int = 1):
    def _dep():
        return user_id

    return _dep


def _clean_db():
    db = SessionLocal()
    try:
        db.query(ClothingItem).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


def setup_module():
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


class TestClothingEndpoints:
    def setup_method(self):
        _clean_db()
        self.upload_tmp = tempfile.TemporaryDirectory()
        self.upload_dir = Path(self.upload_tmp.name)
        import upload as u

        self._orig_upload_dir = u.UPLOAD_DIR
        u.UPLOAD_DIR = self.upload_dir
        self.client = TestClient(app)
        app.dependency_overrides[require_auth] = _override_require_auth(1)
        db = SessionLocal()
        self.user = _create_user(db)
        db.close()

    def teardown_method(self):
        app.dependency_overrides.clear()
        import upload as u

        u.UPLOAD_DIR = self._orig_upload_dir
        self.upload_tmp.cleanup()

    def _post_item(self, name="Test Shirt", category="Oberteil") -> dict:
        content = _make_jpeg_bytes()
        resp = self.client.post(
            "/api/clothing",
            data={"name": name, "category": category},
            files={"image": ("test.jpg", io.BytesIO(content), "image/jpeg")},
        )
        return resp.json()

    def test_get_empty(self):
        resp = self.client.get("/api/clothing")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_item(self):
        resp = self.client.post(
            "/api/clothing",
            data={"name": "Test Shirt", "category": "Oberteil"},
            files={"image": ("test.jpg", io.BytesIO(_make_jpeg_bytes()), "image/jpeg")},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Shirt"
        assert data["category"] == "Oberteil"
        assert data["image_url"].startswith("/upload/")
        assert data["user_id"] == 1

    def test_get_items_after_create(self):
        self._post_item("Shirt", "Oberteil")
        self._post_item("Jeans", "Hose")

        resp = self.client.get("/api/clothing")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 2

    def test_get_items_filtered(self):
        self._post_item("Shirt", "Oberteil")
        self._post_item("Jeans", "Hose")

        resp = self.client.get("/api/clothing?category=Oberteil")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["category"] == "Oberteil"

    def test_get_items_invalid_category(self):
        self._post_item("Shirt", "Oberteil")
        resp = self.client.get("/api/clothing?category=Auto")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_rejects_missing_name(self):
        resp = self.client.post(
            "/api/clothing",
            data={"category": "Oberteil"},
            files={"image": ("test.jpg", io.BytesIO(_make_jpeg_bytes()), "image/jpeg")},
        )
        assert resp.status_code == 400

    def test_create_rejects_empty_name(self):
        resp = self.client.post(
            "/api/clothing",
            data={"name": "", "category": "Oberteil"},
            files={"image": ("test.jpg", io.BytesIO(_make_jpeg_bytes()), "image/jpeg")},
        )
        assert resp.status_code == 400

    def test_create_rejects_name_too_long(self):
        resp = self.client.post(
            "/api/clothing",
            data={"name": "A" * 101, "category": "Oberteil"},
            files={"image": ("test.jpg", io.BytesIO(_make_jpeg_bytes()), "image/jpeg")},
        )
        assert resp.status_code == 400

    def test_create_rejects_control_chars(self):
        resp = self.client.post(
            "/api/clothing",
            data={"name": "Bad\tName", "category": "Oberteil"},
            files={"image": ("test.jpg", io.BytesIO(_make_jpeg_bytes()), "image/jpeg")},
        )
        assert resp.status_code == 400

    def test_create_rejects_invalid_category(self):
        resp = self.client.post(
            "/api/clothing",
            data={"name": "Shirt", "category": "Auto"},
            files={"image": ("test.jpg", io.BytesIO(_make_jpeg_bytes()), "image/jpeg")},
        )
        assert resp.status_code == 400

    def test_create_rejects_invalid_image(self):
        resp = self.client.post(
            "/api/clothing",
            data={"name": "Shirt", "category": "Oberteil"},
            files={"image": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
        )
        assert resp.status_code == 400

    def test_delete_item(self):
        data = self._post_item()
        item_id = data["id"]

        resp = self.client.delete(f"/api/clothing/{item_id}")
        assert resp.status_code == 204

        resp2 = self.client.get("/api/clothing")
        assert resp2.json() == []

    def test_delete_nonexistent_returns_404(self):
        resp = self.client.delete("/api/clothing/9999")
        assert resp.status_code == 404

    def test_delete_other_user_item_returns_404(self):
        data = self._post_item()
        item_id = data["id"]

        app.dependency_overrides[require_auth] = _override_require_auth(2)
        resp = self.client.delete(f"/api/clothing/{item_id}")
        assert resp.status_code == 404
