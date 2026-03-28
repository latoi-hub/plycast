from __future__ import annotations

from typing import TYPE_CHECKING

from plycast.engines.audio.encode import convert_audio
from plycast.engines.tts.providers.espeak import EspeakTTS
from plycast.engines.tts.providers.system_say import SystemSayTTS
from plycast.engines.tts.providers.text_file import TextFileTTS

if TYPE_CHECKING:
    from plycast.engines.tts.providers.parler import ParlerTTS

__all__ = [
    "EspeakTTS",
    "ParlerTTS",
    "SystemSayTTS",
    "TextFileTTS",
    "convert_audio",
]


def __getattr__(name: str):
    if name == "ParlerTTS":
        from plycast.engines.tts.providers.parler import ParlerTTS

        return ParlerTTS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
