import logging
import mimetypes
import os
import secrets
from contextlib import suppress
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "./upload"))

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_GIF87_SIGNATURE = b"GIF87a"
_GIF89_SIGNATURE = b"GIF89a"
_WEBP_SIGNATURE = b"RIFF"


def validate_image(file) -> bool:
    if not hasattr(file, "read"):
        return False

    pos = file.tell() if hasattr(file, "tell") else 0
    try:
        header = file.read(16)
    except Exception:
        return False
    finally:
        if hasattr(file, "seek"):
            with suppress(Exception):
                file.seek(pos)

    if len(header) < 4:
        return False

    if (
        header.startswith(b"\xff\xd8\xff")
        or header.startswith(_PNG_SIGNATURE)
        or header.startswith(_GIF87_SIGNATURE)
        or header.startswith(_GIF89_SIGNATURE)
        or (header.startswith(_WEBP_SIGNATURE) and len(header) >= 12 and header[8:12] == b"WEBP")
    ):
        pass
    else:
        return False

    if hasattr(file, "seek"):
        try:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(pos)
        except Exception:
            file_size = 0
    else:
        file_size = 0

    return not (0 < file_size > MAX_FILE_SIZE)


def save_upload(file, user_id: int) -> str:
    if not hasattr(file, "seek"):
        raise ValueError("Invalid file object: must have seek")

    file.seek(0)
    ext = _guess_extension(file)
    file.seek(0)

    safe_name = f"{secrets.token_hex(16)}_{user_id}{ext}"
    relative_path = safe_name
    full_path = UPLOAD_DIR / relative_path

    with open(full_path, "wb") as f:
        file.seek(0)
        while True:
            chunk = file.read(8192)
            if not chunk:
                break
            f.write(chunk)

    try:
        strip_exif(str(full_path))
    except Exception as e:
        logger.warning("Failed to strip EXIF from %s: %s", relative_path, e)

    return relative_path


def strip_exif(path: str):
    try:
        img = Image.open(path)
    except Exception:
        return

    data = list(img.getdata()) if img.getdata() is not None else None
    mode = img.mode
    size = img.size
    fmt = img.format

    if data is None:
        img.close()
        return

    clean = Image.new(mode, size)
    clean.putdata(data)

    save_kwargs: dict = {}
    if fmt == "JPEG":
        save_kwargs["quality"] = 92

    clean.save(path, format=fmt, **save_kwargs)
    clean.close()
    img.close()


def _guess_extension(file) -> str:
    pos = file.tell() if hasattr(file, "tell") else 0
    try:
        header = file.read(16)
    finally:
        if hasattr(file, "seek"):
            with suppress(Exception):
                file.seek(pos)

    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    elif header.startswith(_PNG_SIGNATURE):
        return ".png"
    elif header.startswith(_GIF87_SIGNATURE) or header.startswith(_GIF89_SIGNATURE):
        return ".gif"
    elif header.startswith(_WEBP_SIGNATURE) and len(header) >= 12 and header[8:12] == b"WEBP":
        return ".webp"

    content_type = getattr(file, "content_type", None)
    if content_type:
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ext

    return ".jpg"
