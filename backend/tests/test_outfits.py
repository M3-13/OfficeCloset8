import pytest
from auth import require_auth
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from models import ClothingItem, Outfit, User
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
def items(user: User, session: Session):
    tops = [
        ClothingItem(name="Shirt", category="Tops", image_path="/img/shirt.jpg", user_id=user.id),
        ClothingItem(name="Bluse", category="Tops", image_path="/img/bluse.jpg", user_id=user.id),
    ]
    pants = ClothingItem(
        name="Jeans", category="Pants", image_path="/img/jeans.jpg", user_id=user.id
    )
    shoes = ClothingItem(
        name="Sneaker", category="Shoes", image_path="/img/sneaker.jpg", user_id=user.id
    )
    all_items = [*tops, pants, shoes]
    for it in all_items:
        session.add(it)
    session.commit()
    return all_items


@pytest.fixture
def client(user: User, session: Session):
    ov_db, ov_auth = _overrides(user.id, session)
    app.dependency_overrides[get_db] = ov_db
    app.dependency_overrides[require_auth] = ov_auth
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestCreateOutfit:
    def test_create_outfit_success(self, client, items):
        resp = client.post(
            "/api/outfits",
            json={"name": "Mein Outfit", "item_ids": [items[0].id, items[2].id, items[3].id]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Mein Outfit"
        assert len(data["items"]) == 3

    def test_create_outfit_empty_name(self, client, items):
        resp = client.post(
            "/api/outfits",
            json={"name": "   ", "item_ids": [items[0].id]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == ""

    def test_create_outfit_name_too_long(self, client, items):
        resp = client.post(
            "/api/outfits",
            json={"name": "A" * 101, "item_ids": [items[0].id]},
        )
        assert resp.status_code == 400
        assert "100 Zeichen" in resp.json()["detail"]

    def test_create_outfit_duplicate_category(self, client, items):
        resp = client.post(
            "/api/outfits",
            json={"name": "Outfit", "item_ids": [items[0].id, items[1].id]},
        )
        assert resp.status_code == 400
        assert "pro Kategorie" in resp.json()["detail"]

    def test_create_outfit_item_not_found(self, client):
        resp = client.post(
            "/api/outfits",
            json={"name": "Outfit", "item_ids": [9999]},
        )
        assert resp.status_code == 404

    def test_create_outfit_no_items(self, client):
        resp = client.post(
            "/api/outfits",
            json={"name": "Outfit", "item_ids": []},
        )
        assert resp.status_code == 400
        assert "erforderlich" in resp.json()["detail"]

    def test_create_outfit_wrong_user(self, session: Session, client, user: User):
        other = User(email="other@example.com", password_hash="hash")
        session.add(other)
        session.commit()
        session.refresh(other)
        other_item = ClothingItem(
            name="Fremd", category="Tops", image_path="/x.jpg", user_id=other.id
        )
        session.add(other_item)
        session.commit()

        resp = client.post(
            "/api/outfits",
            json={"name": "Outfit", "item_ids": [other_item.id]},
        )
        assert resp.status_code == 403


class TestListOutfits:
    def test_list_empty(self, client):
        resp = client.get("/api/outfits")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_outfits(self, client, items):
        client.post(
            "/api/outfits",
            json={"name": "Outfit 1", "item_ids": [items[0].id]},
        )
        client.post(
            "/api/outfits",
            json={"name": "Outfit 2", "item_ids": [items[2].id]},
        )
        resp = client.get("/api/outfits")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["name"] == "Outfit 2"


class TestGetOutfit:
    def test_get_outfit_success(self, client, items):
        create_resp = client.post(
            "/api/outfits",
            json={"name": "Detail", "item_ids": [items[0].id, items[2].id]},
        )
        outfit_id = create_resp.json()["id"]

        resp = client.get(f"/api/outfits/{outfit_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Detail"
        assert len(data["items"]) == 2

    def test_get_outfit_not_found(self, client):
        resp = client.get("/api/outfits/9999")
        assert resp.status_code == 404

    def test_get_outfit_wrong_user(self, session: Session, client, user: User):
        other = User(email="other@example.com", password_hash="hash")
        session.add(other)
        session.commit()
        session.refresh(other)

        outfit = Outfit(name="Fremd", user_id=other.id)
        session.add(outfit)
        session.commit()
        session.refresh(outfit)

        resp = client.get(f"/api/outfits/{outfit.id}")
        assert resp.status_code == 404


class TestUpdateOutfit:
    def test_update_name(self, client, items):
        create_resp = client.post(
            "/api/outfits",
            json={"name": "Alt", "item_ids": [items[0].id]},
        )
        outfit_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/outfits/{outfit_id}",
            json={"name": "Neu", "item_ids": [items[0].id]},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Neu"

    def test_update_items(self, client, items):
        create_resp = client.post(
            "/api/outfits",
            json={"name": "Outfit", "item_ids": [items[0].id]},
        )
        outfit_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/outfits/{outfit_id}",
            json={"name": "Outfit", "item_ids": [items[2].id, items[3].id]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        categories = [it["category"] for it in data["items"]]
        assert "Pants" in categories
        assert "Shoes" in categories

    def test_update_not_found(self, client, items):
        resp = client.put(
            "/api/outfits/9999",
            json={"name": "X", "item_ids": [items[0].id]},
        )
        assert resp.status_code == 404

    def test_update_duplicate_category(self, client, items):
        create_resp = client.post(
            "/api/outfits",
            json={"name": "Outfit", "item_ids": [items[0].id, items[2].id]},
        )
        outfit_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/outfits/{outfit_id}",
            json={"name": "Outfit", "item_ids": [items[0].id, items[1].id]},
        )
        assert resp.status_code == 400


class TestDeleteOutfit:
    def test_delete_success(self, client, items):
        create_resp = client.post(
            "/api/outfits",
            json={"name": "Del", "item_ids": [items[0].id]},
        )
        outfit_id = create_resp.json()["id"]

        resp = client.delete(f"/api/outfits/{outfit_id}")
        assert resp.status_code == 204

        get_resp = client.get(f"/api/outfits/{outfit_id}")
        assert get_resp.status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/api/outfits/9999")
        assert resp.status_code == 404

    def test_delete_wrong_user(self, session: Session, client, user: User):
        other = User(email="other@example.com", password_hash="hash")
        session.add(other)
        session.commit()
        session.refresh(other)

        outfit = Outfit(name="Fremd", user_id=other.id)
        session.add(outfit)
        session.commit()
        session.refresh(outfit)

        resp = client.delete(f"/api/outfits/{outfit.id}")
        assert resp.status_code == 404


class TestRequireAuth:
    def test_unauthenticated_rejected(self):
        app.dependency_overrides.clear()
        with TestClient(app) as c:
            resp = c.get("/api/outfits")
            assert resp.status_code == 401
