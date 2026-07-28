import os
import tempfile

import pytest
from auth import require_auth
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from models import ClothingItem, User
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from upload import MAX_FILE_SIZE, strip_exif, validate_image


class _MockUser:
    def __init__(self, id: int):
        self.id = id


class _MockFile:
    def __init__(
        self, content: bytes, content_type: str = "image/jpeg", filename: str = "test.jpg"
    ):
        self._content = content
        self._pos = 0
        self.content_type = content_type
        self.filename = filename

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            data = self._content[self._pos :]
            self._pos = len(self._content)
            return data
        data = self._content[self._pos : self._pos + size]
        self._pos += size
        return data

    def seek(self, pos: int, whence: int = 0):
        if whence == 0:
            self._pos = pos
        elif whence == 1:
            self._pos += pos
        elif whence == 2:
            self._pos = len(self._content) + pos

    def tell(self) -> int:
        return self._pos


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
    u = User(email="wardrobe@example.com", password_hash="hash")
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


@pytest.fixture
def client(user: User, session: Session):
    ov_db, ov_auth = _overrides(user.id, session)
    app.dependency_overrides[get_db] = ov_db
    app.dependency_overrides[require_auth] = ov_auth
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _jpg_bytes() -> bytes:
    b = bytearray()
    b.extend(b"\xff\xd8\xff\xe0")
    b.extend(b"\x00\x10JFIF\x00\x01")
    b.extend(b"\x01\x01\x00\x00\x01\x00\x01\x00\x00")
    b.extend(b"\xff\xdb\x00C\x00")
    for _ in range(60):
        b.append(0)
    b.extend(b"\xff\xd9")
    return bytes(b)


def _png_bytes() -> bytes:
    b = bytearray(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    b.extend(b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde")
    b.extend(b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05")
    b.extend(b"\x18\xd8N>\x00\x00\x00\x00IEND\xaeB`\x82")
    return bytes(b)


def _oversized_bytes() -> bytes:
    return b"\xff\xd8\xff\xe0" + b"\x00" * (MAX_FILE_SIZE + 100)


def _gif_bytes() -> bytes:
    return b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"


def _webp_bytes() -> bytes:
    b = bytearray(b"RIFF")
    b.extend(b"\x1a\x00\x00\x00WEBPVP8 ")
    b.extend(
        b"\x0a\x00\x00\x00\x10\x00\x00\xc3\x01\x00\x9d\x01\x2a\x01\x00\x01\x00\x02\x00\x34\x25\xa4\x00\x03p\x00\xfe\xfd\x94\x00\x00"
    )
    return bytes(b)


class TestValidateImage:
    def test_valid_jpeg(self):
        f = _MockFile(_jpg_bytes())
        assert validate_image(f) is True

    def test_valid_png(self):
        f = _MockFile(_png_bytes())
        assert validate_image(f) is True

    def test_valid_gif(self):
        f = _MockFile(_gif_bytes())
        assert validate_image(f) is True

    def test_valid_webp(self):
        f = _MockFile(_webp_bytes())
        assert validate_image(f) is True

    def test_invalid_magic_bytes(self):
        f = _MockFile(b"not an image file at all just text")
        assert validate_image(f) is False

    def test_oversized(self):
        f = _MockFile(_oversized_bytes())
        assert validate_image(f) is False

    def test_too_short_header(self):
        f = _MockFile(b"\xff\xd8")
        assert validate_image(f) is False

    def test_no_read_method(self):
        assert validate_image("not a file") is False  # pyright: ignore[reportArgumentType]


class TestStripExif:
    def test_strip_exif_jpeg(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
            tf.write(_jpg_bytes())
            path = tf.name
        try:
            strip_exif(path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_strip_exif_non_image(self):
        path = tempfile.mktemp(suffix=".txt")
        try:
            with open(path, "w") as f:
                f.write("not an image")
            strip_exif(path)
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestClothingList:
    def test_list_empty(self, client, session: Session, user: User):
        resp = client.get("/api/clothing")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_items(self, client, session: Session, user: User):
        item = ClothingItem(name="Shirt", category="Tops", image_path="test.jpg", user_id=user.id)
        session.add(item)
        session.commit()

        resp = client.get("/api/clothing")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Shirt"
        assert data[0]["category"] == "Tops"


class TestClothingDelete:
    def test_delete_success(self, client, session: Session, user: User):
        item = ClothingItem(name="Shirt", category="Tops", image_path="test.jpg", user_id=user.id)
        session.add(item)
        session.commit()
        session.refresh(item)

        resp = client.delete(f"/api/clothing/{item.id}")
        assert resp.status_code == 204

        remaining = session.query(ClothingItem).filter(ClothingItem.id == item.id).first()
        assert remaining is None

    def test_delete_not_found(self, client):
        resp = client.delete("/api/clothing/9999")
        assert resp.status_code == 404

    def test_delete_wrong_user(self, session: Session, client, user: User):
        other = User(email="other2@example.com", password_hash="hash")
        session.add(other)
        session.commit()
        session.refresh(other)

        item = ClothingItem(name="Fremd", category="Tops", image_path="x.jpg", user_id=other.id)
        session.add(item)
        session.commit()
        session.refresh(item)

        resp = client.delete(f"/api/clothing/{item.id}")
        assert resp.status_code == 404


class TestClothingCreate:
    def test_create_success(self, client, session: Session, user: User, monkeypatch):
        monkeypatch.setattr("routers.clothing.save_upload", lambda f, uid: "saved/test.jpg")
        monkeypatch.setattr("routers.clothing.validate_image", lambda f: True)

        jpg = _jpg_bytes()
        files = {"image": ("shirt.jpg", jpg, "image/jpeg")}
        data = {"name": "Mein Shirt", "category": "Oberteile"}

        resp = client.post("/api/clothing", data=data, files=files)
        assert resp.status_code == 201
        result = resp.json()
        assert result["name"] == "Mein Shirt"
        assert result["category"] == "Oberteile"
        assert result["image_path"] == "saved/test.jpg"
        assert result["user_id"] == user.id

    def test_create_empty_name(self, client, monkeypatch):
        monkeypatch.setattr("routers.clothing.validate_image", lambda f: True)
        jpg = _jpg_bytes()
        files = {"image": ("shirt.jpg", jpg, "image/jpeg")}
        data = {"name": "   ", "category": "Oberteile"}

        resp = client.post("/api/clothing", data=data, files=files)
        assert resp.status_code == 422

    def test_create_name_too_long(self, client, monkeypatch):
        monkeypatch.setattr("routers.clothing.validate_image", lambda f: True)
        jpg = _jpg_bytes()
        files = {"image": ("shirt.jpg", jpg, "image/jpeg")}
        data = {"name": "A" * 101, "category": "Oberteile"}

        resp = client.post("/api/clothing", data=data, files=files)
        assert resp.status_code == 422
        assert "100 Zeichen" in resp.json()["detail"]

    def test_create_no_image(self, client):
        data = {"name": "Shirt", "category": "Oberteile"}
        resp = client.post("/api/clothing", data=data)
        assert resp.status_code == 422

    def test_create_invalid_image(self, client, monkeypatch):
        monkeypatch.setattr("routers.clothing.validate_image", lambda f: False)
        data = {"name": "Shirt", "category": "Oberteile"}
        files = {"image": ("shirt.jpg", b"not valid", "image/jpeg")}
        resp = client.post("/api/clothing", data=data, files=files)
        assert resp.status_code == 422
        assert "Ungültiges Bild" in resp.json()["detail"]

    def test_create_control_chars_in_name(self, client, monkeypatch):
        monkeypatch.setattr("routers.clothing.validate_image", lambda f: True)
        jpg = _jpg_bytes()
        files = {"image": ("shirt.jpg", jpg, "image/jpeg")}
        data = {"name": "Bad\x00Name", "category": "Oberteile"}

        resp = client.post("/api/clothing", data=data, files=files)
        assert resp.status_code == 422
        assert "Steuerzeichen" in resp.json()["detail"]

    def test_create_control_chars_in_category(self, client, monkeypatch):
        monkeypatch.setattr("routers.clothing.validate_image", lambda f: True)
        jpg = _jpg_bytes()
        files = {"image": ("shirt.jpg", jpg, "image/jpeg")}
        data = {"name": "Shirt", "category": "Bad\x1fCat"}

        resp = client.post("/api/clothing", data=data, files=files)
        assert resp.status_code == 422
        assert "Steuerzeichen" in resp.json()["detail"]

    def test_create_category_too_long(self, client, monkeypatch):
        monkeypatch.setattr("routers.clothing.validate_image", lambda f: True)
        jpg = _jpg_bytes()
        files = {"image": ("shirt.jpg", jpg, "image/jpeg")}
        data = {"name": "Shirt", "category": "A" * 51}

        resp = client.post("/api/clothing", data=data, files=files)
        assert resp.status_code == 422


def test_clothing_endpoints_return_cors_headers():
    with TestClient(app) as c:
        resp = c.options(
            "/api/clothing",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
        assert "access-control-allow-origin" in resp.headers


def test_clothing_unauthenticated_rejected():
    app.dependency_overrides.clear()
    with TestClient(app) as c:
        resp = c.get("/api/clothing")
        assert resp.status_code == 401
