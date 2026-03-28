"""Dataclasses for pipeline I/O and high-level workflow results."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PipelineInput:
    source_path: Path
    source_language: str
    target_language: str
    max_chunk_chars: int = 1500
    audio_format: str = "mp3"


@dataclass(slots=True)
class PipelineOutput:
    translated_text_path: Path
    audio_path: Path
    translated_text: str


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


@dataclass(slots=True)
class ConvertResult:
    """End-to-end read → translate → TTS."""

    source_path: Path
    output_dir: Path
    translated_text_path: Path
    audio_path: Path
    translated_text: str
    source_language: str
    target_language: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_path": str(self.source_path),
            "output_dir": str(self.output_dir),
            "translated_text_path": str(self.translated_text_path),
            "audio_path": str(self.audio_path),
            "target_language": self.target_language,
            "source_language": self.source_language,
        }


@dataclass(slots=True)
class TranslateResult:
    """Read → translate only."""

    source_path: Path
    translated_text: str
    translated_text_path: Path
    source_language: str
    target_language: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_path": str(self.source_path),
            "translated_text_path": str(self.translated_text_path),
            "target_language": self.target_language,
            "source_language": self.source_language,
        }


@dataclass(slots=True)
class TtsResult:
    """Read → TTS (no translation)."""

    source_path: Path
    text: str
    audio_path: Path
    tts_language: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source_path": str(self.source_path),
            "audio_path": str(self.audio_path),
            "tts_language": self.tts_language,
        }


@dataclass(slots=True)
class InspectResult:
    """Lightweight ingest preview (no full pipeline)."""

    path: Path
    suffix: str
    size_bytes: int
    text_char_count: int | None
    preview: str | None
    source_language: str | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "suffix": self.suffix,
            "size_bytes": self.size_bytes,
            "text_char_count": self.text_char_count,
            "preview": self.preview,
            "source_language": self.source_language,
        }
