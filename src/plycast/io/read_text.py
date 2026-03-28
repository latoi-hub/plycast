"""Extract plain text from supported file types."""

from __future__ import annotations

from pathlib import Path

from plycast.core.models import ReadTextResult
from plycast.io.loaders import IMAGE_SUFFIXES, _READERS
from plycast.io.loaders.image import read_image_ocr, tesseract_lang_for_source


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
        if ext in IMAGE_SUFFIXES:
            tess_lang = (
                tesseract_lang_for_source(source_language)
                if source_language
                else None
            )
            text = read_image_ocr(path, lang=tess_lang)
        else:
            reader = _READERS.get(ext)
            if reader is None:
                supported = ", ".join(
                    sorted(_READERS.keys() | set(IMAGE_SUFFIXES))
                )
                raise ValueError(
                    f"Unsupported file type {ext!r}. Supported: {supported}"
                )
            text = reader(path)
        if not text.strip():
            raise ValueError(f"No text could be extracted from {path}")
        return ReadTextResult(source_path=path, text=text)
