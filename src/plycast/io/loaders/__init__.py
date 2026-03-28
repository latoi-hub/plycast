"""Format-specific text extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from plycast.io.loaders.docx import read_docx
from plycast.io.loaders.image import IMAGE_SUFFIXES, read_image_ocr, tesseract_lang_for_source
from plycast.io.loaders.pdf import read_pdf
from plycast.io.loaders.txt import read_plain

_READERS: dict[str, Callable[[Path], str]] = {
    ".txt": read_plain,
    ".md": read_plain,
    ".markdown": read_plain,
    ".pdf": read_pdf,
    ".docx": read_docx,
}

__all__ = [
    "IMAGE_SUFFIXES",
    "_READERS",
    "read_docx",
    "read_image_ocr",
    "read_pdf",
    "read_plain",
    "tesseract_lang_for_source",
]
