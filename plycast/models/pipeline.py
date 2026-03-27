from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
