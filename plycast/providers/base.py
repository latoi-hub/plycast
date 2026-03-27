from __future__ import annotations

from pathlib import Path
from typing import Protocol


class TranslatorProvider(Protocol):
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        """Translate text from source to target language."""


class TTSProvider(Protocol):
    def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        """Generate an audio file for text and return output path."""


__all__ = ["TTSProvider", "TranslatorProvider"]
