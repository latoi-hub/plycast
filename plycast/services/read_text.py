"""Extract plain text from supported file types."""

from __future__ import annotations

import shutil
from pathlib import Path

from plycast.models import ReadTextResult

_tesseract_cmd_configured = False


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


# Suffixes handled by Tesseract (see :func:`_read_image_ocr`).
_IMAGE_SUFFIXES = frozenset(
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


def _tesseract_lang(source_language: str) -> str | None:
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


def _read_plain(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError(
            "PDF support requires: pip install pypdf"
        ) from exc
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n\n".join(parts).strip()


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise ImportError(
            "Word .docx support requires: pip install python-docx"
        ) from exc
    doc = Document(str(path))
    lines = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(lines).strip()


def _read_image_ocr(path: Path, *, lang: str | None = None) -> str:
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


_READERS: dict[str, object] = {
    ".txt": _read_plain,
    ".md": _read_plain,
    ".markdown": _read_plain,
    ".pdf": _read_pdf,
    ".docx": _read_docx,
}


class ReadTextService:
    """Load text from disk; format is chosen from the file suffix."""

    def read(
        self,
        path: Path,
        *,
        source_language: str | None = None,
    ) -> ReadTextResult:
        if not path.exists():
            hint = (
                f" (cwd: {Path.cwd()}; tried: {path.resolve()})"
                if not path.is_absolute()
                else f" (tried: {path.resolve()})"
            )
            raise FileNotFoundError(f"Input file not found: {path}{hint}")
        ext = path.suffix.lower()
        if ext in _IMAGE_SUFFIXES:
            tess_lang = (
                _tesseract_lang(source_language)
                if source_language
                else None
            )
            text = _read_image_ocr(path, lang=tess_lang)
        else:
            reader = _READERS.get(ext)
            if reader is None:
                supported = ", ".join(
                    sorted(_READERS.keys() | set(_IMAGE_SUFFIXES))
                )
                raise ValueError(
                    f"Unsupported file type {ext!r}. Supported: {supported}"
                )
            text = reader(path)  # type: ignore[operator]
        if not text.strip():
            raise ValueError(f"No text could be extracted from {path}")
        return ReadTextResult(source_path=path, text=text)
