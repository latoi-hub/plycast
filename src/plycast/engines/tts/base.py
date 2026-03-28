from __future__ import annotations

from pathlib import Path
from typing import Protocol


class TTSProvider(Protocol):
    def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        """Generate an audio file for text and return output path."""
