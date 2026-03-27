from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ReadTextResult:
    """Plain text extracted from a file (txt, md, pdf, docx, image OCR, …)."""

    source_path: Path
    text: str


@dataclass(slots=True)
class TranslateOnlyResult:
    """Read → translate; no audio."""

    source_path: Path
    translated_text: str
    translated_text_path: Path


@dataclass(slots=True)
class ReadAudioOnlyResult:
    """Read → TTS on extracted text (no translation)."""

    source_path: Path
    text: str
    audio_path: Path
