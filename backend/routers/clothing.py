import os
from contextlib import suppress

from auth import require_auth
from database import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from models import ClothingItem
from schemas import ClothingItemResponse
from sqlalchemy.orm import Session

from upload import UPLOAD_DIR, save_upload, validate_image

router = APIRouter(prefix="/api/clothing", tags=["clothing"])

ALLOWED_CATEGORIES = {"Oberteil", "Hose", "Schuhe", "Accessoire", "Kleid", "Jacke"}
MAX_NAME_LENGTH = 100


def _validate_name(name: str) -> str:
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Name darf nicht leer sein")
    if len(name) > MAX_NAME_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Name darf maximal {MAX_NAME_LENGTH} Zeichen lang sein",
        )
    if any(ord(c) < 32 for c in name):
        raise HTTPException(status_code=400, detail="Name enthält ungültige Zeichen")
    return name.strip()


def _validate_category(category: str) -> str:
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Ungültige Kategorie: {category}. Erlaubt: {', '.join(sorted(ALLOWED_CATEGORIES))}",
        )
    return category


@router.get("", response_model=list[ClothingItemResponse])
def get_items(
    category: str | None = Query(None),
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),  # noqa: B008
):
    query = db.query(ClothingItem).filter(ClothingItem.user_id == user_id)
    if category:
        if category not in ALLOWED_CATEGORIES:
            return []
        query = query.filter(ClothingItem.category == category)
    return query.all()


@router.post("", response_model=ClothingItemResponse, status_code=201)
def create_item(
    name: str = Form(default=""),
    category: str = Form(default=""),
    image: UploadFile = File(...),  # noqa: B008
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),  # noqa: B008
):
    _validate_name(name)
    _validate_category(category)

    if not validate_image(image):
        raise HTTPException(
            status_code=400,
            detail="Ungültiges Bild. Erlaubt: JPEG, PNG, WebP, maximal 5 MB.",
        )

    image_path = save_upload(image, user_id)

    item = ClothingItem(
        name=name.strip(),
        category=category,
        image_path=image_path,
        user_id=user_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db),  # noqa: B008
):
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item_id, ClothingItem.user_id == user_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")

    file_path = UPLOAD_DIR.parent / item.image_path
    with suppress(OSError):
        os.remove(str(file_path))

    db.delete(item)
    db.commit()
