from __future__ import annotations

from typing import TYPE_CHECKING

from .convert import convert_audio
from .espeak import EspeakTTS
from .system_say import SystemSayTTS
from .text_file import TextFileTTS

if TYPE_CHECKING:
    from .parler import ParlerTTS

__all__ = ["EspeakTTS", "ParlerTTS", "SystemSayTTS", "TextFileTTS", "convert_audio"]


def __getattr__(name: str):
    if name == "ParlerTTS":
        from .parler import ParlerTTS

        return ParlerTTS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
