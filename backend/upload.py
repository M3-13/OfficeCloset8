import os
from pathlib import Path

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "./upload"))


def save_upload(file, user_id: int) -> str:
    raise NotImplementedError


def validate_image(file) -> bool:
    return True


def strip_exif(path: str):
    raise NotImplementedError
