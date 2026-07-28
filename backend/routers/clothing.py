import os
import re

from auth import require_auth
from database import get_db
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from models import ClothingItem
from schemas import ClothingItemResponse
from sqlalchemy.orm import Session

from upload import UPLOAD_DIR, save_upload, validate_image

router = APIRouter(prefix="/api/clothing", tags=["clothing"])

CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")
MAX_NAME_LENGTH = 100

ALLOWED_CATEGORIES = {"Oberteil", "Hose", "Schuhe", "Accessoire", "Kleid", "Jacke"}


def validate_clothing_name(name: str) -> str:
    if not name or not name.strip():
        raise HTTPException(status_code=422, detail="Name darf nicht leer sein")
    if len(name) > MAX_NAME_LENGTH:
        raise HTTPException(
            status_code=422, detail=f"Name darf maximal {MAX_NAME_LENGTH} Zeichen lang sein"
        )
    if CONTROL_CHARS_RE.search(name):
        raise HTTPException(status_code=422, detail="Name enthält ungültige Steuerzeichen")
    return name.strip()


def _validate_category(category: str) -> str:
    cat = category.strip()
    if not cat:
        raise HTTPException(status_code=422, detail="Kategorie darf nicht leer sein")
    if cat not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Ungültige Kategorie '{cat}'. Erlaubt: {', '.join(sorted(ALLOWED_CATEGORIES))}",
        )
    return cat


@router.get("", response_model=list[ClothingItemResponse])
def list_items(
    category: str | None = None,
    user=Depends(require_auth),
    db: Session = Depends(get_db),
):
    if category is not None:
        cat = category.strip()
        if cat and cat not in ALLOWED_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Ungültige Kategorie '{cat}'. Erlaubt: {', '.join(sorted(ALLOWED_CATEGORIES))}",
            )

    query = db.query(ClothingItem).filter(ClothingItem.user_id == user.id)
    if category and category.strip():
        query = query.filter(ClothingItem.category == category.strip())

    items = query.order_by(ClothingItem.id.desc()).all()
    return items


@router.post("", response_model=ClothingItemResponse, status_code=201)
async def create_item(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = Form(...),
    user=Depends(require_auth),
    db: Session = Depends(get_db),
):
    name = validate_clothing_name(name)
    category = _validate_category(category)

    contents = await image.read()
    file_size = image.size if hasattr(image, "size") else len(contents)

    try:
        validate_image(
            file_bytes=contents,
            content_type=image.content_type or "",
            filename=image.filename,
            file_size=file_size,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        relative_path = save_upload(
            file_bytes=contents, filename=image.filename or "image", user_id=user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    image_url = f"/uploads/{relative_path}"

    item = ClothingItem(name=name, category=category, image_path=image_url, user_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    user=Depends(require_auth),
    db: Session = Depends(get_db),
):
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")
    if item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")

    if item.image_path.startswith("/uploads/"):
        file_rel = item.image_path[len("/uploads/") :]
        file_abs = UPLOAD_DIR / file_rel
        try:
            if file_abs.is_file():
                os.remove(file_abs)
        except OSError:
            pass

    db.delete(item)
    db.commit()
