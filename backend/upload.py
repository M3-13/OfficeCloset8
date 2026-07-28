import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "../upload")).resolve()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE = 5 * 1024 * 1024

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WEBP_MAGIC_RIFF = b"RIFF"
WEBP_MAGIC_WEBP = b"WEBP"


def validate_image(file: UploadFile) -> bool:
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size == 0 or size > MAX_SIZE:
        return False

    header = file.file.read(12)
    file.file.seek(0)

    if len(header) < 4:
        return False

    if (
        header[:3] == JPEG_MAGIC
        or header[:8] == PNG_MAGIC
        or (header[:4] == WEBP_MAGIC_RIFF and len(header) >= 12 and header[8:12] == WEBP_MAGIC_WEBP)
    ):
        pass
    else:
        return False

    return not (file.content_type and file.content_type not in ALLOWED_MIME_TYPES)


def strip_exif(path: str) -> None:
    img = Image.open(path)
    clean = Image.new(img.mode, img.size)
    if hasattr(img, "get_flattened_data"):
        data = list(img.get_flattened_data())
    else:
        data = list(img.getdata())
    img.close()
    clean.putdata(data)
    clean.save(path)
    clean.close()


def _sanitize_filename(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".jpg"
    safe = f"{uuid.uuid4()}{ext}"
    return safe


def save_upload(file: UploadFile, user_id: int) -> str:
    original_name = file.filename or "upload"
    safe_name = _sanitize_filename(original_name)

    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / safe_name
    file.file.seek(0)
    contents = file.file.read()
    file_path.write_bytes(contents)

    strip_exif(str(file_path))

    relative = Path("upload") / str(user_id) / safe_name
    return str(relative).replace("\\", "/")
