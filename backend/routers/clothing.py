import logging
import os
import re
from contextlib import suppress

from auth import require_auth
from database import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from models import ClothingItem, outfit_items
from schemas import ClothingItemResponse
from sqlalchemy.orm import Session
from upload import UPLOAD_DIR, save_upload, validate_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/clothing", tags=["clothing"])

VALID_CATEGORIES = {
    "Oberteile",
    "Hosen",
    "Kleider",
    "Röcke",
    "Schuhe",
    "Accessoires",
    "Jacken",
    "Mäntel",
    "Pullover",
    "Tops",
    "Pants",
    "Shoes",
    "Dresses",
    "Skirts",
    "Jackets",
    "Coats",
    "Sweaters",
    "Accessories",
}

CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")
MAX_NAME_LENGTH = 100
MAX_CATEGORY_LENGTH = 50


def validate_clothing_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail="Name darf nicht leer sein")
    if len(cleaned) > MAX_NAME_LENGTH:
        raise HTTPException(
            status_code=422, detail=f"Name darf maximal {MAX_NAME_LENGTH} Zeichen lang sein"
        )
    if CONTROL_CHARS_RE.search(cleaned):
        raise HTTPException(status_code=422, detail="Name enthält ungültige Steuerzeichen")
    return cleaned


def validate_category(category: str) -> str:
    cat = category.strip()
    if len(cat) > MAX_CATEGORY_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Kategorie darf maximal {MAX_CATEGORY_LENGTH} Zeichen lang sein",
        )
    if CONTROL_CHARS_RE.search(cat):
        raise HTTPException(status_code=422, detail="Kategorie enthält ungültige Steuerzeichen")
    if not cat:
        raise HTTPException(status_code=422, detail="Kategorie darf nicht leer sein")
    return cat


@router.get("", response_model=list[ClothingItemResponse])
def list_clothing(
    user=Depends(require_auth),
    db: Session = Depends(get_db),
):
    items = (
        db.query(ClothingItem)
        .filter(ClothingItem.user_id == user.id)
        .order_by(ClothingItem.id.desc())
        .all()
    )
    return items


@router.post("", response_model=ClothingItemResponse, status_code=201)
def create_clothing(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    user=Depends(require_auth),
    db: Session = Depends(get_db),
):
    validated_name = validate_clothing_name(name)
    validated_category = validate_category(category)

    if not image.filename:
        raise HTTPException(status_code=422, detail="Kein Bild ausgewählt")

    if not validate_image(image.file):
        raise HTTPException(
            status_code=422,
            detail="Ungültiges Bild: nur JPG, PNG, GIF, WEBP bis 5 MB erlaubt",
        )

    try:
        image_path = save_upload(image.file, user.id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    item = ClothingItem(
        name=validated_name,
        category=validated_category,
        image_path=image_path,
        user_id=user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    logger.info("User %d created clothing item %d", user.id, item.id)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_clothing(
    item_id: int,
    user=Depends(require_auth),
    db: Session = Depends(get_db),
):
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")
    if item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")

    db.execute(outfit_items.delete().where(outfit_items.c.clothing_item_id == item_id))
    db.flush()

    db.delete(item)
    db.commit()

    full_path = UPLOAD_DIR / item.image_path
    if not os.path.isabs(str(full_path)):
        with suppress(FileNotFoundError, OSError):
            os.remove(full_path)

    logger.info("User %d deleted clothing item %d", user.id, item_id)
