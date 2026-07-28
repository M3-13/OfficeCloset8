import io
import os
import tempfile
from unittest.mock import patch

import pytest
from PIL import Image

from upload import MAX_FILE_SIZE, save_upload, strip_exif, validate_image


def _make_jpeg_bytes(size_bytes: int | None = None) -> bytes:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    data = buf.getvalue()
    if size_bytes is not None and len(data) < size_bytes:
        data = data + b"\x00" * (size_bytes - len(data))
    return data[:size_bytes] if size_bytes is not None else data


def _make_png_bytes() -> bytes:
    img = Image.new("RGB", (10, 10), color=(0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_webp_bytes() -> bytes:
    img = Image.new("RGB", (10, 10), color=(0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    return buf.getvalue()


class TestValidateImage:
    def test_valid_jpeg(self):
        data = _make_jpeg_bytes()
        assert validate_image(data, "image/jpeg", "photo.jpg") is True

    def test_valid_png(self):
        data = _make_png_bytes()
        assert validate_image(data, "image/png", "image.png") is True

    def test_valid_webp(self):
        data = _make_webp_bytes()
        assert validate_image(data, "image/webp", "graphic.webp") is True

    def test_reject_oversized(self):
        data = _make_jpeg_bytes(size_bytes=MAX_FILE_SIZE + 1)
        with pytest.raises(ValueError, match="5 MB"):
            validate_image(data, "image/jpeg", "big.jpg", file_size=len(data))

    def test_reject_bad_mime(self):
        data = _make_jpeg_bytes()
        with pytest.raises(ValueError, match="Unerlaubter Dateityp"):
            validate_image(data, "application/octet-stream", "photo.jpg")

    def test_reject_bad_extension(self):
        data = _make_jpeg_bytes()
        with pytest.raises(ValueError, match="Unerlaubte Dateiendung"):
            validate_image(data, "image/jpeg", "photo.gif")

    def test_reject_bad_magic_bytes(self):
        with pytest.raises(ValueError, match="Magic Bytes"):
            validate_image(b"not an image at all", "image/jpeg", "photo.jpg")

    def test_reject_empty_file(self):
        with pytest.raises(ValueError, match="Magic Bytes"):
            validate_image(b"", "image/jpeg", "empty.jpg")


class TestStripExif:
    def test_strip_from_jpeg_without_crash(self):
        img = Image.new("RGB", (20, 20), color=(100, 150, 200))
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img.save(tmp.name, format="JPEG")
            tmp_path = tmp.name

        try:
            original_size = os.path.getsize(tmp_path)
            strip_exif(tmp_path)
            new_size = os.path.getsize(tmp_path)
            assert new_size > 0
            with Image.open(tmp_path) as reopened:
                assert reopened.size == (20, 20)
            assert new_size <= original_size
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_strip_from_png(self):
        img = Image.new("RGB", (20, 20), color=(100, 150, 200))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp.name, format="PNG")
            tmp_path = tmp.name

        try:
            strip_exif(tmp_path)
            with Image.open(tmp_path) as reopened:
                assert reopened.size == (20, 20)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_strip_nonexistent_file(self):
        with pytest.raises(RuntimeError, match="EXIF-Entfernung"):
            strip_exif("/nonexistent/path/image.jpg")


class TestSaveUpload:
    @pytest.fixture(autouse=True)
    def setup_upload_dir(self, tmp_path):
        self._tmp_upload = tmp_path / "upload"
        self._tmp_upload.mkdir(parents=True, exist_ok=True)
        with patch("upload.UPLOAD_DIR", self._tmp_upload):
            yield

    def test_save_valid_jpeg(self):
        data = _make_jpeg_bytes()
        rel_path = save_upload(file_bytes=data, filename="my Photo.jpg", user_id=42)

        assert rel_path.startswith("42/")
        assert "_my_photo.jpg" in rel_path.lower()
        full_path = self._tmp_upload / rel_path
        assert full_path.is_file()
        assert full_path.stat().st_size > 0

    def test_save_sanitizes_filename(self):
        data = _make_png_bytes()
        rel_path = save_upload(file_bytes=data, filename="Hello!!! World (1).png", user_id=1)

        parts = rel_path.split("/")
        assert parts[0] == "1"
        fname = parts[1]
        assert "!!!" not in fname
        assert "(" not in fname
        assert ")" not in fname
        assert fname.endswith(".png")

    def test_save_creates_user_dir(self):
        data = _make_jpeg_bytes()
        save_upload(file_bytes=data, filename="test.jpg", user_id=99)

        user_dir = self._tmp_upload / "99"
        assert user_dir.is_dir()

    def test_save_reject_no_filename(self):
        data = _make_jpeg_bytes()
        with pytest.raises(ValueError, match="Dateiname"):
            save_upload(file_bytes=data, filename="", user_id=1)
