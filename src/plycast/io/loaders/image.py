"""Image OCR via Tesseract."""

from __future__ import annotations

import shutil
from pathlib import Path

_tesseract_cmd_configured = False

IMAGE_SUFFIXES = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".gif",
        ".tiff",
        ".tif",
        ".bmp",
    }
)


def _find_tesseract_executable() -> str | None:
    found = shutil.which("tesseract")
    if found:
        return found
    for candidate in (
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract",
    ):
        p = Path(candidate)
        if p.is_file():
            return str(p)
    return None


def _ensure_tesseract_cmd(pytesseract: object) -> None:
    """Point pytesseract at ``tesseract`` when PATH is minimal (IDE/GUI)."""
    global _tesseract_cmd_configured
    if _tesseract_cmd_configured:
        return
    exe = _find_tesseract_executable()
    if not exe:
        raise RuntimeError(
            "Tesseract OCR is not installed or not on PATH. "
            "macOS: brew install tesseract tesseract-lang "
            "(then restart the terminal or add Homebrew to PATH)."
        )
    pyt = pytesseract.pytesseract  # type: ignore[attr-defined]
    pyt.tesseract_cmd = exe
    _tesseract_cmd_configured = True


def tesseract_lang_for_source(source_language: str) -> str | None:
    """Map CLI/source language codes to Tesseract ``-l`` names."""
    s = source_language.strip().lower().replace("_", "-")
    if s in ("zh", "zh-cn", "zh-hans", "cmn", "zh-hans-cn"):
        return "chi_sim"
    if s in ("zh-tw", "zh-hk", "zh-hant", "zh-hant-tw"):
        return "chi_tra"
    if s == "en":
        return "eng"
    if s in ("vi", "vie"):
        return "vie"
    if s in ("ja", "jp"):
        return "jpn"
    if s in ("ko", "kr"):
        return "kor"
    return None


def read_image_ocr(path: Path, *, lang: str | None = None) -> str:
    try:
        from PIL import Image
        import pytesseract
    except ImportError as exc:
        raise ImportError(
            "Image OCR requires: pip install pillow pytesseract "
            "(and a Tesseract binary on your system)"
        ) from exc
    _ensure_tesseract_cmd(pytesseract)
    image = Image.open(path)
    if lang:
        text = pytesseract.image_to_string(image, lang=lang)
    else:
        text = pytesseract.image_to_string(image)
    return text.strip()
