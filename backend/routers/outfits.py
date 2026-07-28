from auth import require_auth
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import ClothingItem, Outfit, outfit_items
from schemas import OutfitCreate, OutfitDetail
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/outfits", tags=["outfits"])


def _validate_item_ids(db: Session, user_id: int, item_ids: list[int]):
    if not item_ids:
        raise HTTPException(status_code=400, detail="Mindestens ein Kleidungsstück erforderlich")

    items = db.query(ClothingItem).filter(ClothingItem.id.in_(item_ids)).all()
    found_ids = {item.id for item in items}

    for iid in item_ids:
        if iid not in found_ids:
            raise HTTPException(status_code=404, detail=f"Kleidungsstück {iid} nicht gefunden")
        item = next(it for it in items if it.id == iid)
        if item.user_id != user_id:
            raise HTTPException(status_code=403, detail="Kleidungsstück gehört nicht dem Benutzer")

    categories = [item.category for item in items]
    if len(categories) != len(set(categories)):
        raise HTTPException(status_code=400, detail="Nur ein Kleidungsstück pro Kategorie erlaubt")

    return items


@router.get("", response_model=list[OutfitDetail])
def list_outfits(user=Depends(require_auth), db: Session = Depends(get_db)):
    outfits = db.query(Outfit).filter(Outfit.user_id == user.id).order_by(Outfit.id.desc()).all()
    return outfits


@router.get("/{outfit_id}", response_model=OutfitDetail)
def get_outfit(outfit_id: int, user=Depends(require_auth), db: Session = Depends(get_db)):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
    if outfit.user_id != user.id:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
    return outfit


@router.post("", response_model=OutfitDetail, status_code=201)
def create_outfit(body: OutfitCreate, user=Depends(require_auth), db: Session = Depends(get_db)):
    if len(body.name) > 100:
        raise HTTPException(status_code=400, detail="Name darf maximal 100 Zeichen lang sein")

    _validate_item_ids(db, user.id, body.item_ids)

    outfit = Outfit(name=body.name.strip(), user_id=user.id)
    db.add(outfit)
    db.flush()

    items = db.query(ClothingItem).filter(ClothingItem.id.in_(body.item_ids)).all()
    outfit.items = items
    db.commit()
    db.refresh(outfit)
    return outfit


@router.put("/{outfit_id}", response_model=OutfitDetail)
def update_outfit(
    outfit_id: int,
    body: OutfitCreate,
    user=Depends(require_auth),
    db: Session = Depends(get_db),
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
    if outfit.user_id != user.id:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")

    if len(body.name) > 100:
        raise HTTPException(status_code=400, detail="Name darf maximal 100 Zeichen lang sein")

    _validate_item_ids(db, user.id, body.item_ids)

    outfit.name = body.name.strip()
    items = db.query(ClothingItem).filter(ClothingItem.id.in_(body.item_ids)).all()
    outfit.items = items
    db.commit()
    db.refresh(outfit)
    return outfit


@router.delete("/{outfit_id}", status_code=204)
def delete_outfit(outfit_id: int, user=Depends(require_auth), db: Session = Depends(get_db)):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
    if outfit.user_id != user.id:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")

    db.execute(outfit_items.delete().where(outfit_items.c.outfit_id == outfit_id))
    db.delete(outfit)
    db.commit()
