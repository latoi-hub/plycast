from __future__ import annotations

from typing import Protocol


class TranslatorProvider(Protocol):
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        """Translate text from source to target language."""
