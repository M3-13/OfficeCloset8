import os
import re
import uuid
from pathlib import Path

from PIL import Image

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "../upload")).resolve()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024
SAFE_FILENAME_RE = re.compile(r"[^a-z0-9_.-]")

MAGIC_BYTES = {
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG\r\n\x1a\n": ".png",
    b"RIFF": ".webp",
}

MIME_MAP = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}


def validate_image(
    file_bytes: bytes,
    content_type: str,
    filename: str | None = None,
    file_size: int | None = None,
) -> bool:
    if file_size is not None and file_size > MAX_FILE_SIZE:
        raise ValueError("Datei überschreitet die maximale Größe von 5 MB")

    mime_exts = MIME_MAP.get(content_type)
    if mime_exts is None:
        raise ValueError(f"Unerlaubter Dateityp: {content_type}")

    if filename:
        ext = Path(filename).suffix.lower()
        if ext and ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unerlaubte Dateiendung: {ext}")

    header = file_bytes[:12]

    detected_magic = False
    for magic, ext in MAGIC_BYTES.items():
        if header.startswith(magic):
            if magic == b"RIFF":
                if len(header) >= 12 and header[8:12] == b"WEBP":
                    detected_magic = True
                    if ".webp" not in mime_exts:
                        raise ValueError("MIME-Type passt nicht zu WebP-Magic-Bytes")
            else:
                detected_magic = True
                if ext not in mime_exts:
                    raise ValueError("MIME-Type passt nicht zu Magic-Bytes")
            break

    if not detected_magic:
        raise ValueError(
            "Datei ist kein gültiges JPEG-, PNG- oder WebP-Bild (Magic Bytes fehlen)"
        )

    return True


def strip_exif(path: str):
    try:
        with Image.open(path) as img:
            if hasattr(img, "get_flattened_data"):
                data = list(img.get_flattened_data())
            elif hasattr(img, "getdata"):
                data = list(img.getdata())
            else:
                raise ValueError(f"Could not read image data from {path}")
            clean = Image.new(img.mode, img.size)
            clean.putdata(data)
            clean.save(path, format=img.format or "JPEG")
    except Exception as e:
        raise RuntimeError(f"EXIF-Entfernung fehlgeschlagen: {e}") from e


def save_upload(file_bytes: bytes, filename: str, user_id: int) -> str:
    if not filename:
        raise ValueError("Kein Dateiname vorhanden")

    original_ext = Path(filename).suffix.lower()
    if original_ext == ".jpeg":
        original_ext = ".jpg"

    safe_name = SAFE_FILENAME_RE.sub("_", Path(filename).stem.lower())
    safe_name = safe_name[:50]
    unique_name = f"{uuid.uuid4().hex}_{safe_name}{original_ext}"

    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / unique_name

    file_path.write_bytes(file_bytes)

    strip_exif(str(file_path))

    return f"{user_id}/{unique_name}"
