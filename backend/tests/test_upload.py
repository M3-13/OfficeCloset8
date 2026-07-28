import io
import os
import tempfile
from contextlib import suppress
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from upload import save_upload, strip_exif, validate_image


def _make_upload(filename: str, content: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        filename=filename, file=io.BytesIO(content), headers={"content-type": content_type}
    )


def _make_jpeg() -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color="red")
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_png() -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGBA", (10, 10), color=(0, 255, 0, 255))
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_webp() -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color="blue")
    img.save(buf, format="WEBP")
    return buf.getvalue()


def test_validate_image_jpeg():
    content = _make_jpeg()
    f = _make_upload("test.jpg", content, "image/jpeg")
    assert validate_image(f) is True


def test_validate_image_png():
    content = _make_png()
    f = _make_upload("test.png", content, "image/png")
    assert validate_image(f) is True


def test_validate_image_webp():
    content = _make_webp()
    f = _make_upload("test.webp", content, "image/webp")
    assert validate_image(f) is True


def test_validate_rejects_wrong_mime():
    content = _make_jpeg()
    f = _make_upload("test.jpg", content, "image/gif")
    assert validate_image(f) is False


def test_validate_rejects_empty():
    f = _make_upload("empty.jpg", b"", "image/jpeg")
    assert validate_image(f) is False


def test_validate_rejects_bogus_bytes():
    f = _make_upload("evil.jpg", b"not an image at all", "image/jpeg")
    assert validate_image(f) is False


def test_validate_rejects_too_large():
    big = b"\xff\xd8\xff" + b"\x00" * (6 * 1024 * 1024)
    f = _make_upload("big.jpg", big, "image/jpeg")
    assert validate_image(f) is False


def test_strip_exif():
    content = _make_jpeg()
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        img = Image.open(tmp_path)
        assert img.getexif() is not None
        img.close()

        strip_exif(tmp_path)

        img2 = Image.open(tmp_path)
        exif = img2.getexif()
        img2.close()
        assert not exif or not dict(exif)
    finally:
        if tmp_path:
            with suppress(OSError):
                os.unlink(tmp_path)


def test_save_upload():
    content = _make_png()
    f = _make_upload("my photo.png", content, "image/png")

    orig_dir = os.environ.get("UPLOAD_DIR")
    td = tempfile.TemporaryDirectory()
    try:
        os.environ["UPLOAD_DIR"] = td.name
        import upload as u

        u.UPLOAD_DIR = Path(td.name).resolve()

        path = save_upload(f, 42)
        assert path.startswith("upload/42/")
        assert path.endswith(".png")
        full = Path(td.name).resolve() / "42" / os.path.basename(path)
        assert full.exists()

        img = Image.open(str(full))
        assert img.size == (10, 10)
        img.close()
    finally:
        if orig_dir is not None:
            os.environ["UPLOAD_DIR"] = orig_dir
        else:
            del os.environ["UPLOAD_DIR"]
        td.cleanup()


def test_save_upload_sanitizes_extension():
    content = _make_jpeg()
    f = _make_upload("dangerous.exe", content, "image/jpeg")

    orig_dir = os.environ.get("UPLOAD_DIR")
    td = tempfile.TemporaryDirectory()
    try:
        os.environ["UPLOAD_DIR"] = td.name
        import upload as u

        u.UPLOAD_DIR = Path(td.name).resolve()
        path = save_upload(f, 1)
        assert path.endswith(".jpg")
    finally:
        if orig_dir is not None:
            os.environ["UPLOAD_DIR"] = orig_dir
        else:
            del os.environ["UPLOAD_DIR"]
        td.cleanup()
