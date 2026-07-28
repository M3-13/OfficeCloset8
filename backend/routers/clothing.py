import re

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/clothing", tags=["clothing"])

CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")
MAX_NAME_LENGTH = 100


def validate_clothing_name(name: str) -> str:
    if len(name) > MAX_NAME_LENGTH:
        raise HTTPException(
            status_code=422, detail=f"Name darf maximal {MAX_NAME_LENGTH} Zeichen lang sein"
        )
    if CONTROL_CHARS_RE.search(name):
        raise HTTPException(status_code=422, detail="Name enthält ungültige Steuerzeichen")
    return name.strip()
